"""
HT Timeline Tracker
Tracks estimated arrival times and complete journey timelines for each HT-job assignment
"""
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from src.constant import CONSTANT


@dataclass
class TimelineEvent:
    """Single event in an HT's journey"""
    timestamp: float
    event_type: str  # BOOK_QC, DRIVE, WORK_QC, WORK_YARD, etc.
    location: str
    estimated_duration: float
    actual_duration: Optional[float] = None
    status: str = "pending"  # pending, in_progress, completed


@dataclass
class HTJobTimeline:
    """Complete timeline for a single HT job assignment"""
    job_seq: str
    job_type: str  # DI or LO
    HT_name: str
    QC_name: str
    yard_name: str
    start_time: float
    events: List[TimelineEvent] = field(default_factory=list)
    completion_time: Optional[float] = None
    total_duration: Optional[float] = None


class HTTimelineTracker:
    """Tracks all HT movements and job timelines"""
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_folder / "ht_timelines.csv"
        self.active_timelines: Dict[str, HTJobTimeline] = {}
        self.completed_timelines: List[HTJobTimeline] = []
        self.current_simulation_time = 0
        
        # Reset log file
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
            job_seq=job_seq,
            job_type=job_type,
            HT_name=HT_name,
            QC_name=QC_name,
            yard_name=yard_name,
            start_time=self.current_simulation_time
        )
        
        # Estimate timeline from instructions
        cumulative_time = self.current_simulation_time
        
        for idx, instruction in enumerate(instructions):
            instr_type = instruction.instructor_type.name
            
            if instr_type == "DRIVE":
                # Calculate drive time based on path length
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
                duration = 10  # Minimal booking time
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
    
    def update_event_status(self, job_seq: str, event_index: int, status: str, actual_time: Optional[float] = None):
        """Update the status of a specific event in the timeline"""
        if job_seq in self.active_timelines:
            timeline = self.active_timelines[job_seq]
            if 0 <= event_index < len(timeline.events):
                event = timeline.events[event_index]
                event.status = status
                if actual_time is not None:
                    event.actual_duration = actual_time
                self._log_event_update(timeline, event_index)
    
    def complete_job(self, job_seq: str, completion_time: float):
        """Mark a job as completed"""
        if job_seq in self.active_timelines:
            timeline = self.active_timelines[job_seq]
            timeline.completion_time = completion_time
            timeline.total_duration = completion_time - timeline.start_time
            
            self.completed_timelines.append(timeline)
            del self.active_timelines[job_seq]
            self._log_completion(timeline)
    
    def get_estimated_arrival(self, job_seq: str, location_type: str) -> Optional[float]:
        """Get estimated arrival time to a specific location (QC or YARD)"""
        if job_seq in self.active_timelines:
            timeline = self.active_timelines[job_seq]
            for event in timeline.events:
                if location_type in event.event_type:
                    return event.timestamp
        return None
    
    def get_active_ht_locations(self) -> Dict[str, str]:
        """Get current estimated location of all active HTs"""
        locations = {}
        for job_seq, timeline in self.active_timelines.items():
            current_event = None
            for event in timeline.events:
                if event.timestamp <= self.current_simulation_time < event.timestamp + event.estimated_duration:
                    current_event = event
                    break
            if current_event:
                locations[timeline.HT_name] = f"{current_event.event_type}@{current_event.location}"
            else:
                locations[timeline.HT_name] = "IDLE"
        return locations
    
    def _log_timeline_creation(self, timeline: HTJobTimeline):
        """Log timeline creation to CSV"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            for idx, event in enumerate(timeline.events):
                writer.writerow([
                    timeline.job_seq,
                    timeline.job_type,
                    timeline.HT_name,
                    timeline.QC_name,
                    timeline.yard_name,
                    timeline.start_time,
                    idx + 1,
                    event.event_type,
                    event.location,
                    event.timestamp,
                    event.timestamp + event.estimated_duration,
                    '',  # actual_start (to be filled)
                    '',  # actual_end (to be filled)
                    event.status,
                    '',  # completion_time
                    ''   # total_duration
                ])
    
    def _log_event_update(self, timeline: HTJobTimeline, event_index: int):
        """Update event status in log (append-only for now)"""
        pass  # For real-time updates, consider using a separate status log
    
    def _log_completion(self, timeline: HTJobTimeline):
        """Log job completion"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timeline.job_seq,
                timeline.job_type,
                timeline.HT_name,
                timeline.QC_name,
                timeline.yard_name,
                timeline.start_time,
                'COMPLETE',
                'JOB_COMPLETE',
                'ALL',
                '',
                '',
                '',
                '',
                'completed',
                timeline.completion_time,
                timeline.total_duration
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
