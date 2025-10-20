"""
Congestion Monitor
Detects and tracks congestion events in the terminal
"""
import csv
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from src.constant import CONSTANT
from src.floor import Coordinate


@dataclass
class CongestionEvent:
    """A detected congestion event"""
    timestamp: float
    location: Coordinate
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    ht_count: int
    affected_hts: List[str]
    duration: float = 0.0
    resolved: bool = False


class CongestionMonitor:
    """Monitor and detect congestion in real-time"""
    
    # Congestion thresholds
    THRESHOLD_LOW = 3  # 3+ HTs in same sector
    THRESHOLD_MEDIUM = 5
    THRESHOLD_HIGH = 7
    THRESHOLD_CRITICAL = 10
    
    # Critical zones (more sensitive)
    CRITICAL_ZONES = {
        'QC_TRAVEL': [(x, y) for x in range(1, 43) for y in [4, 5]],
        'HIGHWAY': [(x, y) for x in range(1, 43) for y in range(7, 13)],
        'BUFFER': [(x, 6) for x in range(1, 43)]
    }
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_folder / "congestion_events.csv"
        self.alert_file = self.data_folder / "congestion_alerts.csv"
        
        # Track sector occupancy
        self.sector_occupancy: Dict[tuple, Set[str]] = defaultdict(set)
        self.active_congestion: Dict[tuple, CongestionEvent] = {}
        self.congestion_history: List[CongestionEvent] = []
        
        # Metrics
        self.total_congestion_events = 0
        self.critical_events = 0
        self.current_alerts: List[str] = []
        
        self._initialize_log_files()
    
    def _initialize_log_files(self):
        """Create fresh CSV log files"""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'event_id', 'start_time', 'end_time', 'duration',
                'location_x', 'location_y', 'severity', 'ht_count',
                'affected_hts', 'zone_type', 'resolved'
            ])
        
        with open(self.alert_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'alert_type', 'location', 'severity', 'message'
            ])
    
    def update_ht_positions(self, ht_positions: Dict[str, Coordinate], current_time: float):
        """Update HT positions and detect congestion"""
        # Clear previous occupancy
        self.sector_occupancy.clear()
        
        # Build new occupancy map
        for ht_name, coord in ht_positions.items():
            if coord:
                sector_key = (coord.x, coord.y)
                self.sector_occupancy[sector_key].add(ht_name)
        
        # Check for congestion
        self._detect_congestion(current_time)
    
    def _detect_congestion(self, current_time: float):
        """Detect congestion events"""
        new_alerts = []
        
        for sector_key, hts in self.sector_occupancy.items():
            ht_count = len(hts)
            
            # Determine severity
            if ht_count >= self.THRESHOLD_CRITICAL:
                severity = "CRITICAL"
            elif ht_count >= self.THRESHOLD_HIGH:
                severity = "HIGH"
            elif ht_count >= self.THRESHOLD_MEDIUM:
                severity = "MEDIUM"
            elif ht_count >= self.THRESHOLD_LOW:
                severity = "LOW"
            else:
                severity = None
            
            coord = Coordinate(sector_key[0], sector_key[1])
            
            # Check if this is a new or continuing congestion
            if severity and sector_key not in self.active_congestion:
                # New congestion event
                event = CongestionEvent(
                    timestamp=current_time,
                    location=coord,
                    severity=severity,
                    ht_count=ht_count,
                    affected_hts=list(hts)
                )
                self.active_congestion[sector_key] = event
                self.total_congestion_events += 1
                
                if severity == "CRITICAL":
                    self.critical_events += 1
                
                # Generate alert
                zone_type = self._identify_zone(coord)
                alert_msg = f"{severity} congestion at {coord} ({zone_type}): {ht_count} HTs"
                new_alerts.append((severity, coord, alert_msg))
                self._log_alert(current_time, severity, coord, alert_msg)
            
            elif severity and sector_key in self.active_congestion:
                # Update existing congestion
                event = self.active_congestion[sector_key]
                event.ht_count = ht_count
                event.affected_hts = list(hts)
                event.duration = current_time - event.timestamp
                
                # Update severity if escalated
                if event.severity != severity:
                    event.severity = severity
                    alert_msg = f"ESCALATED to {severity} at {coord}: {ht_count} HTs"
                    new_alerts.append((severity, coord, alert_msg))
                    self._log_alert(current_time, "ESCALATION", coord, alert_msg)
        
        # Check for resolved congestion
        resolved_sectors = set(self.active_congestion.keys()) - set(self.sector_occupancy.keys())
        for sector_key in resolved_sectors:
            event = self.active_congestion[sector_key]
            event.resolved = True
            event.duration = current_time - event.timestamp
            self.congestion_history.append(event)
            self._log_event(event, len(self.congestion_history))
            
            del self.active_congestion[sector_key]
            
            alert_msg = f"Congestion RESOLVED at ({sector_key[0]}, {sector_key[1]})"
            self._log_alert(current_time, "RESOLVED", event.location, alert_msg)
        
        # Update current alerts
        self.current_alerts = [msg for _, _, msg in new_alerts]
    
    def _identify_zone(self, coord: Coordinate) -> str:
        """Identify which zone a coordinate belongs to"""
        if coord.y in [4, 5]:
            return "QC_TRAVEL_LANE"
        elif coord.y == 6:
            return "BUFFER_ZONE"
        elif coord.y in range(7, 13):
            return "HIGHWAY"
        elif coord.y == 3:
            return "QC_SECTOR"
        elif coord.y == 13:
            return "YARD_SECTOR"
        else:
            return "UNKNOWN"
    
    def _log_event(self, event: CongestionEvent, event_id: int):
        """Log congestion event to CSV"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                event_id,
                f"{event.timestamp:.2f}",
                f"{event.timestamp + event.duration:.2f}",
                f"{event.duration:.2f}",
                event.location.x,
                event.location.y,
                event.severity,
                event.ht_count,
                ';'.join(event.affected_hts),
                self._identify_zone(event.location),
                event.resolved
            ])
    
    def _log_alert(self, timestamp: float, alert_type: str, location: Coordinate, message: str):
        """Log alert to CSV"""
        with open(self.alert_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                f"{timestamp:.2f}",
                alert_type,
                f"({location.x},{location.y})",
                alert_type if alert_type in ["LOW", "MEDIUM", "HIGH", "CRITICAL"] else "INFO",
                message
            ])
    
    def get_current_status(self) -> Dict:
        """Get current congestion status"""
        active_by_severity = defaultdict(int)
        for event in self.active_congestion.values():
            active_by_severity[event.severity] += 1
        
        return {
            'active_congestion_count': len(self.active_congestion),
            'critical_active': active_by_severity.get('CRITICAL', 0),
            'high_active': active_by_severity.get('HIGH', 0),
            'medium_active': active_by_severity.get('MEDIUM', 0),
            'low_active': active_by_severity.get('LOW', 0),
            'total_events': self.total_congestion_events,
            'critical_events_total': self.critical_events,
            'current_alerts': self.current_alerts
        }
    
    def get_hotspots(self, top_n: int = 10) -> List[Dict]:
        """Get top congestion hotspots"""
        location_counts = defaultdict(int)
        for event in self.congestion_history + list(self.active_congestion.values()):
            location_counts[(event.location.x, event.location.y)] += 1
        
        sorted_hotspots = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {'location': f"({x},{y})", 'events': count, 'zone': self._identify_zone(Coordinate(x, y))}
            for (x, y), count in sorted_hotspots[:top_n]
        ]
    
    def has_active_alerts(self) -> bool:
        """Check if there are active HIGH or CRITICAL alerts"""
        return any(event.severity in ['HIGH', 'CRITICAL'] for event in self.active_congestion.values())
