"""
Unified Analytics Engine
Consolidates all analytics functionality into a single module:
- Yard Job Counter
- HT Timeline Tracker
- Emissions Calculator
- Route Optimization Analyzer
- Congestion Monitor

Maintains all original functionality while providing centralized management.
"""
import csv
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field

from src.constant import CONSTANT
from src.floor import Coordinate


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class EmissionRecord:
    """Single emission record"""
    job_seq: str
    job_type: str
    HT_name: str
    distance_traveled: float
    emissions_kg: float
    timestamp: float


@dataclass
class TimelineEvent:
    """Single event in an HT's journey"""
    timestamp: float
    event_type: str
    location: str
    estimated_duration: float
    actual_duration: Optional[float] = None
    status: str = "pending"


@dataclass
class HTJobTimeline:
    """Complete timeline for a single HT job assignment"""
    job_seq: str
    job_type: str
    HT_name: str
    QC_name: str
    yard_name: str
    start_time: float
    events: List[TimelineEvent] = field(default_factory=list)
    completion_time: Optional[float] = None
    total_duration: Optional[float] = None


@dataclass
class RouteMetrics:
    """Metrics for a single route"""
    job_seq: str
    job_type: str
    HT_name: str
    route_type: str
    path_length: int
    optimal_path_length: int
    efficiency: float
    detours: int
    backtracking: int


@dataclass
class CongestionEvent:
    """A detected congestion event"""
    timestamp: float
    location: Coordinate
    severity: str
    ht_count: int
    affected_hts: List[str]
    duration: float = 0.0
    resolved: bool = False


# ============================================================================
# YARD JOB COUNTER
# ============================================================================

class YardJobCounter:
    """Count and track jobs completed at each yard"""
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.log_file = self.data_folder / "yard_job_counts.csv"
        
        # Initialize counters for all 16 yards
        self.yard_totals: Dict[str, int] = {yard: 0 for yard in CONSTANT.YARD_FLOOR.YARD_NAMES}
        self.yard_di_counts: Dict[str, int] = {yard: 0 for yard in CONSTANT.YARD_FLOOR.YARD_NAMES}
        self.yard_lo_counts: Dict[str, int] = {yard: 0 for yard in CONSTANT.YARD_FLOOR.YARD_NAMES}
        self.job_history: list = []
        
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create fresh CSV log file"""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'yard_name', 'job_type', 'job_seq', 'completion_time',
                'yard_total', 'yard_di_count', 'yard_lo_count'
            ])
    
    def record_job_completion(self, yard_name: str, job_type: str, job_seq: str, completion_time: float):
        """Record a completed job at a yard"""
        if yard_name not in self.yard_totals:
            self.yard_totals[yard_name] = 0
            self.yard_di_counts[yard_name] = 0
            self.yard_lo_counts[yard_name] = 0
        
        self.yard_totals[yard_name] += 1
        if job_type == "DI":
            self.yard_di_counts[yard_name] += 1
        else:
            self.yard_lo_counts[yard_name] += 1
        
        self.job_history.append({
            'yard_name': yard_name,
            'job_type': job_type,
            'job_seq': job_seq,
            'completion_time': completion_time
        })
        
        self._log_job(yard_name, job_type, job_seq, completion_time)
    
    def _log_job(self, yard_name: str, job_type: str, job_seq: str, completion_time: float):
        """Log job completion to CSV"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                yard_name, job_type, job_seq, f"{completion_time:.2f}",
                self.yard_totals[yard_name],
                self.yard_di_counts[yard_name],
                self.yard_lo_counts[yard_name]
            ])
    
    def get_total_jobs(self) -> Dict:
        """Get overall totals"""
        total_di = sum(self.yard_di_counts.values())
        total_lo = sum(self.yard_lo_counts.values())
        total = total_di + total_lo
        
        return {
            'total_jobs': total,
            'total_di': total_di,
            'total_lo': total_lo,
            'di_percentage': round((total_di / max(total, 1)) * 100, 1),
            'lo_percentage': round((total_lo / max(total, 1)) * 100, 1)
        }


# ============================================================================
# HT TIMELINE TRACKER
# ============================================================================

class HTTimelineTracker:
    """Tracks all HT movements and job timelines"""
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.log_file = self.data_folder / "ht_timelines.csv"
        self.active_timelines: Dict[str, HTJobTimeline] = {}
        self.completed_timelines: List[HTJobTimeline] = []
        self.current_simulation_time = 0
        
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create fresh CSV log file"""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'job_seq', 'job_type', 'HT_name', 'QC_name', 'yard_name',
                'start_time', 'event_sequence', 'event_type', 'location',
                'estimated_start', 'estimated_end', 'actual_start', 'actual_end',
                'status', 'completion_time', 'total_duration'
            ])
    
    def create_timeline(self, job_seq: str, job_type: str, HT_name: str, 
                       QC_name: str, yard_name: str, instructions: List) -> HTJobTimeline:
        """Create a new timeline when a job is planned"""
        timeline = HTJobTimeline(
            job_seq=job_seq, job_type=job_type, HT_name=HT_name,
            QC_name=QC_name, yard_name=yard_name,
            start_time=self.current_simulation_time
        )
        
        cumulative_time = self.current_simulation_time
        
        for idx, instruction in enumerate(instructions):
            instr_type = instruction.instructor_type.name
            
            if instr_type == "DRIVE":
                path_length = len(instruction.path) if hasattr(instruction, 'path') and instruction.path else 0
                duration = path_length * CONSTANT.JOB_PARAMETER.HT_DRIVE_TIME_PER_SECTOR
                location = f"PATH_{path_length}_sectors"
            elif instr_type == "WORK_QC":
                duration = CONSTANT.JOB_PARAMETER.QC_WORK_TIME_REQUIRED
                location = QC_name
            elif instr_type == "WORK_YARD":
                duration = CONSTANT.JOB_PARAMETER.YARD_WORK_TIME_REQUIRED
                location = yard_name
            elif instr_type in ["BOOK_QC", "BOOK_YARD"]:
                duration = 10
                location = "BOOKING"
            else:
                duration = 0
                location = "UNKNOWN"
            
            event = TimelineEvent(
                timestamp=cumulative_time,
                event_type=instr_type,
                location=location,
                estimated_duration=duration
            )
            timeline.events.append(event)
            cumulative_time += duration
        
        self.active_timelines[job_seq] = timeline
        self._log_timeline_creation(timeline)
        return timeline
    
    def complete_job(self, job_seq: str, completion_time: float):
        """Mark a job as completed"""
        if job_seq in self.active_timelines:
            timeline = self.active_timelines[job_seq]
            timeline.completion_time = completion_time
            timeline.total_duration = completion_time - timeline.start_time
            
            self.completed_timelines.append(timeline)
            del self.active_timelines[job_seq]
            self._log_completion(timeline)
    
    def _log_timeline_creation(self, timeline: HTJobTimeline):
        """Log timeline creation to CSV"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            for idx, event in enumerate(timeline.events):
                writer.writerow([
                    timeline.job_seq, timeline.job_type, timeline.HT_name,
                    timeline.QC_name, timeline.yard_name, timeline.start_time,
                    idx + 1, event.event_type, event.location,
                    event.timestamp, event.timestamp + event.estimated_duration,
                    '', '', event.status, '', ''
                ])
    
    def _log_completion(self, timeline: HTJobTimeline):
        """Log job completion"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timeline.job_seq, timeline.job_type, timeline.HT_name,
                timeline.QC_name, timeline.yard_name, timeline.start_time,
                'COMPLETE', 'JOB_COMPLETE', 'ALL', '', '', '', '',
                'completed', timeline.completion_time, timeline.total_duration
            ])
    
    def update_simulation_time(self, time: float):
        """Update current simulation time"""
        self.current_simulation_time = time
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        return {
            'active_jobs': len(self.active_timelines),
            'completed_jobs': len(self.completed_timelines),
            'avg_job_duration': sum(t.total_duration for t in self.completed_timelines if t.total_duration) / 
                               max(len(self.completed_timelines), 1)
        }


# ============================================================================
# EMISSIONS CALCULATOR
# ============================================================================

class EmissionsCalculator:
    """Calculate and track CO2 emissions from HT operations"""
    
    EMISSION_FACTOR_PER_SECTOR = 0.067
    IDLE_EMISSION_RATE = 0.001
    LOADED_MULTIPLIER = 1.2
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.log_file = self.data_folder / "emissions.csv"
        
        self.total_emissions = 0.0
        self.di_emissions = 0.0
        self.lo_emissions = 0.0
        self.emissions_by_ht: Dict[str, float] = {}
        self.records: List[EmissionRecord] = []
        
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create fresh CSV log file"""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'job_seq', 'job_type', 'HT_name', 'segment_type',
                'distance_sectors', 'emissions_kg', 'cumulative_emissions', 'timestamp'
            ])
    
    def calculate_job_emissions(self, job_seq: str, job_type: str, HT_name: str, 
                               instructions: List, timestamp: float) -> float:
        """Calculate total emissions for a complete job"""
        total_distance = 0
        total_emissions = 0.0
        is_loaded = False
        segment_num = 0
        
        for instruction in instructions:
            instr_type = instruction.instructor_type.name
            
            if instr_type == "DRIVE":
                if hasattr(instruction, 'path') and instruction.path:
                    segment_distance = len(instruction.path) - 1
                    multiplier = self.LOADED_MULTIPLIER if is_loaded else 1.0
                    segment_emissions = segment_distance * self.EMISSION_FACTOR_PER_SECTOR * multiplier
                    
                    total_distance += segment_distance
                    total_emissions += segment_emissions
                    
                    segment_num += 1
                    self._log_segment(job_seq, job_type, HT_name, f"DRIVE_{segment_num}", 
                                    segment_distance, segment_emissions, total_emissions, timestamp)
            
            elif instr_type in ["WORK_QC", "WORK_YARD"]:
                if (job_type == "DI" and instr_type == "WORK_QC") or \
                   (job_type == "LO" and instr_type == "WORK_YARD"):
                    is_loaded = True
                
                work_duration = CONSTANT.JOB_PARAMETER.QC_WORK_TIME_REQUIRED if "QC" in instr_type else \
                               CONSTANT.JOB_PARAMETER.YARD_WORK_TIME_REQUIRED
                idle_emissions = (work_duration / 10) * self.IDLE_EMISSION_RATE * 10
                total_emissions += idle_emissions
                
                self._log_segment(job_seq, job_type, HT_name, instr_type, 
                                0, idle_emissions, total_emissions, timestamp)
        
        # Update totals
        self.total_emissions += total_emissions
        if job_type == "DI":
            self.di_emissions += total_emissions
        else:
            self.lo_emissions += total_emissions
        
        if HT_name not in self.emissions_by_ht:
            self.emissions_by_ht[HT_name] = 0.0
        self.emissions_by_ht[HT_name] += total_emissions
        
        record = EmissionRecord(
            job_seq=job_seq, job_type=job_type, HT_name=HT_name,
            distance_traveled=total_distance, emissions_kg=total_emissions,
            timestamp=timestamp
        )
        self.records.append(record)
        
        return total_emissions
    
    def _log_segment(self, job_seq: str, job_type: str, HT_name: str, segment_type: str,
                    distance: float, emissions: float, cumulative: float, timestamp: float):
        """Log a single segment to CSV"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                job_seq, job_type, HT_name, segment_type,
                f"{distance:.2f}", f"{emissions:.6f}", f"{cumulative:.6f}", f"{timestamp:.2f}"
            ])
    
    def get_summary(self) -> Dict:
        """Get emission summary statistics"""
        return {
            'total_emissions_kg': round(self.total_emissions, 3),
            'total_emissions_tons': round(self.total_emissions / 1000, 3),
            'di_emissions_kg': round(self.di_emissions, 3),
            'lo_emissions_kg': round(self.lo_emissions, 3),
            'di_percentage': round((self.di_emissions / max(self.total_emissions, 1)) * 100, 1),
            'lo_percentage': round((self.lo_emissions / max(self.total_emissions, 1)) * 100, 1),
            'jobs_tracked': len(self.records),
            'avg_emissions_per_job': round(self.total_emissions / max(len(self.records), 1), 3)
        }
    
    def export_summary(self):
        """Export summary to CSV"""
        summary_file = self.data_folder / "emissions_summary.csv"
        summary = self.get_summary()
        
        with open(summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in summary.items():
                writer.writerow([key, value])


# ============================================================================
# ROUTE OPTIMIZATION ANALYZER
# ============================================================================

class RouteOptimizationAnalyzer:
    """Analyze route efficiency and optimization opportunities"""
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.log_file = self.data_folder / "route_optimization.csv"
        self.summary_file = self.data_folder / "route_summary.csv"
        
        self.route_metrics: List[RouteMetrics] = []
        self.efficiency_by_type: Dict[str, List[float]] = defaultdict(list)
        
        self.optimal_distances = {
            'BUFFER_TO_QC': 15,
            'QC_TO_BUFFER': 15,
            'BUFFER_TO_YARD': 20,
            'YARD_TO_BUFFER': 20
        }
        
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create fresh CSV log file"""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'job_seq', 'job_type', 'HT_name', 'route_type',
                'path_length', 'optimal_length', 'efficiency_%',
                'detours', 'backtracking', 'distance_overhead'
            ])
    
    def analyze_route(self, job_seq: str, job_type: str, HT_name: str,
                     route_type: str, path: List[Coordinate]) -> Optional[RouteMetrics]:
        """Analyze a single route"""
        if not path or len(path) < 2:
            return None
        
        path_length = len(path) - 1
        start, end = path[0], path[-1]
        manhattan_distance = abs(end.x - start.x) + abs(end.y - start.y)
        optimal_length = self.optimal_distances.get(route_type, manhattan_distance)
        efficiency = (optimal_length / max(path_length, 1)) * 100
        detours = self._count_detours(path)
        backtracking = self._count_backtracking(path)
        
        metrics = RouteMetrics(
            job_seq=job_seq, job_type=job_type, HT_name=HT_name,
            route_type=route_type, path_length=path_length,
            optimal_path_length=optimal_length, efficiency=round(efficiency, 2),
            detours=detours, backtracking=backtracking
        )
        
        self.route_metrics.append(metrics)
        self.efficiency_by_type[route_type].append(efficiency)
        self._log_route(metrics)
        
        return metrics
    
    def _count_detours(self, path: List[Coordinate]) -> int:
        """Count unnecessary detours"""
        if len(path) < 3:
            return 0
        
        detours = 0
        for i in range(1, len(path) - 1):
            prev_dir = self._get_direction(path[i-1], path[i])
            next_dir = self._get_direction(path[i], path[i+1])
            
            if prev_dir and next_dir and self._is_sharp_turn(prev_dir, next_dir):
                detours += 1
        
        return detours
    
    def _count_backtracking(self, path: List[Coordinate]) -> int:
        """Count backtracking moves"""
        if len(path) < 3:
            return 0
        
        backtrack = 0
        for i in range(1, len(path) - 1):
            prev_dir = self._get_direction(path[i-1], path[i])
            next_dir = self._get_direction(path[i], path[i+1])
            
            if prev_dir and next_dir and self._is_opposite(prev_dir, next_dir):
                backtrack += 1
        
        return backtrack
    
    def _get_direction(self, from_coord: Coordinate, to_coord: Coordinate) -> Optional[str]:
        """Get direction of movement"""
        dx = to_coord.x - from_coord.x
        dy = to_coord.y - from_coord.y
        
        if dx > 0:
            return 'EAST'
        elif dx < 0:
            return 'WEST'
        elif dy > 0:
            return 'SOUTH'
        elif dy < 0:
            return 'NORTH'
        return None
    
    def _is_sharp_turn(self, dir1: str, dir2: str) -> bool:
        """Check if turn is 90+ degrees"""
        opposites = [
            ('NORTH', 'EAST'), ('NORTH', 'WEST'),
            ('SOUTH', 'EAST'), ('SOUTH', 'WEST'),
            ('EAST', 'NORTH'), ('EAST', 'SOUTH'),
            ('WEST', 'NORTH'), ('WEST', 'SOUTH')
        ]
        return (dir1, dir2) in opposites
    
    def _is_opposite(self, dir1: str, dir2: str) -> bool:
        """Check if directions are opposite"""
        opposites = [
            ('NORTH', 'SOUTH'), ('SOUTH', 'NORTH'),
            ('EAST', 'WEST'), ('WEST', 'EAST')
        ]
        return (dir1, dir2) in opposites
    
    def _log_route(self, metrics: RouteMetrics):
        """Log route metrics to CSV"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                metrics.job_seq, metrics.job_type, metrics.HT_name,
                metrics.route_type, metrics.path_length,
                metrics.optimal_path_length, f"{metrics.efficiency:.2f}",
                metrics.detours, metrics.backtracking,
                metrics.path_length - metrics.optimal_path_length
            ])
    
    def get_efficiency_summary(self) -> Dict:
        """Get route efficiency summary"""
        if not self.route_metrics:
            return {
                'avg_efficiency': 0,
                'total_routes': 0,
                'optimal_routes': 0,
                'inefficient_routes': 0
            }
        
        total_efficiency = sum(m.efficiency for m in self.route_metrics)
        avg_efficiency = total_efficiency / len(self.route_metrics)
        optimal_routes = sum(1 for m in self.route_metrics if m.efficiency >= 95)
        inefficient_routes = sum(1 for m in self.route_metrics if m.efficiency < 80)
        
        return {
            'avg_efficiency': round(avg_efficiency, 2),
            'total_routes': len(self.route_metrics),
            'optimal_routes': optimal_routes,
            'inefficient_routes': inefficient_routes,
            'total_detours': sum(m.detours for m in self.route_metrics),
            'total_backtracking': sum(m.backtracking for m in self.route_metrics)
        }
    
    def export_summary(self):
        """Export summary to CSV"""
        with open(self.summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            writer.writerow(['=== OVERALL EFFICIENCY ==='])
            summary = self.get_efficiency_summary()
            for key, value in summary.items():
                writer.writerow([key, value])


# ============================================================================
# CONGESTION MONITOR
# ============================================================================

class CongestionMonitor:
    """Monitor and detect congestion in real-time"""
    
    THRESHOLD_LOW = 3
    THRESHOLD_MEDIUM = 5
    THRESHOLD_HIGH = 7
    THRESHOLD_CRITICAL = 10
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.log_file = self.data_folder / "congestion_events.csv"
        self.alert_file = self.data_folder / "congestion_alerts.csv"
        
        self.sector_occupancy: Dict[tuple, Set[str]] = defaultdict(set)
        self.active_congestion: Dict[tuple, CongestionEvent] = {}
        self.congestion_history: List[CongestionEvent] = []
        
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
        self.sector_occupancy.clear()
        
        for ht_name, coord in ht_positions.items():
            if coord:
                sector_key = (coord.x, coord.y)
                self.sector_occupancy[sector_key].add(ht_name)
        
        self._detect_congestion(current_time)
    
    def _detect_congestion(self, current_time: float):
        """Detect congestion events"""
        new_alerts = []
        
        for sector_key, hts in self.sector_occupancy.items():
            ht_count = len(hts)
            
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
            
            if severity and sector_key not in self.active_congestion:
                event = CongestionEvent(
                    timestamp=current_time, location=coord,
                    severity=severity, ht_count=ht_count,
                    affected_hts=list(hts)
                )
                self.active_congestion[sector_key] = event
                self.total_congestion_events += 1
                
                if severity == "CRITICAL":
                    self.critical_events += 1
                
                zone_type = self._identify_zone(coord)
                alert_msg = f"{severity} congestion at {coord} ({zone_type}): {ht_count} HTs"
                new_alerts.append((severity, coord, alert_msg))
                self._log_alert(current_time, severity, coord, alert_msg)
            
            elif severity and sector_key in self.active_congestion:
                event = self.active_congestion[sector_key]
                event.ht_count = ht_count
                event.affected_hts = list(hts)
                event.duration = current_time - event.timestamp
                
                if event.severity != severity:
                    event.severity = severity
                    alert_msg = f"ESCALATED to {severity} at {coord}: {ht_count} HTs"
                    new_alerts.append((severity, coord, alert_msg))
                    self._log_alert(current_time, "ESCALATION", coord, alert_msg)
        
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
        return "UNKNOWN"
    
    def _log_event(self, event: CongestionEvent, event_id: int):
        """Log congestion event to CSV"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                event_id, f"{event.timestamp:.2f}",
                f"{event.timestamp + event.duration:.2f}",
                f"{event.duration:.2f}",
                event.location.x, event.location.y,
                event.severity, event.ht_count,
                ';'.join(event.affected_hts),
                self._identify_zone(event.location),
                event.resolved
            ])
    
    def _log_alert(self, timestamp: float, alert_type: str, location: Coordinate, message: str):
        """Log alert to CSV"""
        with open(self.alert_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                f"{timestamp:.2f}", alert_type,
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


# ============================================================================
# UNIFIED ANALYTICS ENGINE
# ============================================================================

class AnalyticsEngine:
    """
    Unified analytics engine that manages all analytics components.
    Provides a single interface for all analytics operations.
    """
    
    def __init__(self, data_folder: Path):
        """Initialize all analytics components"""
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize all analytics modules
        self.yard_counter = YardJobCounter(self.data_folder)
        self.timeline_tracker = HTTimelineTracker(self.data_folder)
        self.emissions_calculator = EmissionsCalculator(self.data_folder)
        self.route_optimizer = RouteOptimizationAnalyzer(self.data_folder)
        self.congestion_monitor = CongestionMonitor(self.data_folder)
        
        print(f"[INIT] Analytics Engine initialized with data folder: {self.data_folder}")
    
    def update_simulation_time(self, time: float):
        """Update simulation time across all trackers"""
        self.timeline_tracker.update_simulation_time(time)
    
    def record_job_completion(self, yard_name: str, job_type: str, job_seq: str, completion_time: float):
        """Record a completed job (yard counter)"""
        self.yard_counter.record_job_completion(yard_name, job_type, job_seq, completion_time)
    
    def create_timeline(self, job_seq: str, job_type: str, HT_name: str, 
                       QC_name: str, yard_name: str, instructions: List):
        """Create HT job timeline"""
        return self.timeline_tracker.create_timeline(job_seq, job_type, HT_name, QC_name, yard_name, instructions)
    
    def complete_job_timeline(self, job_seq: str, completion_time: float):
        """Complete a job timeline"""
        self.timeline_tracker.complete_job(job_seq, completion_time)
    
    def calculate_emissions(self, job_seq: str, job_type: str, HT_name: str, instructions: List, timestamp: float):
        """Calculate emissions for a job"""
        return self.emissions_calculator.calculate_job_emissions(job_seq, job_type, HT_name, instructions, timestamp)
    
    def analyze_route(self, job_seq: str, job_type: str, HT_name: str, route_type: str, path: List[Coordinate]):
        """Analyze a route for optimization"""
        return self.route_optimizer.analyze_route(job_seq, job_type, HT_name, route_type, path)
    
    def update_congestion(self, ht_positions: Dict[str, Coordinate], current_time: float):
        """Update congestion monitoring"""
        self.congestion_monitor.update_ht_positions(ht_positions, current_time)
    
    def export_all_summaries(self):
        """Export summaries from all analytics modules"""
        self.emissions_calculator.export_summary()
        self.route_optimizer.export_summary()
        print("[OK] All analytics summaries exported")
    
    def get_overall_summary(self) -> Dict:
        """Get summary from all analytics modules"""
        return {
            'yard_jobs': self.yard_counter.get_total_jobs(),
            'timelines': self.timeline_tracker.get_summary_stats(),
            'emissions': self.emissions_calculator.get_summary(),
            'routes': self.route_optimizer.get_efficiency_summary(),
            'congestion': self.congestion_monitor.get_current_status()
        }
