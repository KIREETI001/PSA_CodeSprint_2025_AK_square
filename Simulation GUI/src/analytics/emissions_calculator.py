"""
Emissions Calculator
Calculates and tracks CO2 emissions from HT movements
"""
import csv
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

from src.constant import CONSTANT


@dataclass
class EmissionRecord:
    """Single emission record"""
    job_seq: str
    job_type: str
    HT_name: str
    distance_traveled: float  # in sectors
    emissions_kg: float
    timestamp: float


class EmissionsCalculator:
    """Calculate and track emissions from HT operations"""
    
    # Emission factors (kg CO2 per sector traveled)
    # Assuming: 1 sector = ~50m, HT consumes ~0.5L diesel/km, diesel = 2.68kg CO2/L
    EMISSION_FACTOR_PER_SECTOR = 0.067  # kg CO2 per sector (~50m)
    
    # Additional factors
    IDLE_EMISSION_RATE = 0.001  # kg CO2 per second of idle time
    LOADED_MULTIPLIER = 1.2  # 20% more emissions when loaded (after QC/Yard work)
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)
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
                'distance_sectors', 'emissions_kg', 'cumulative_emissions',
                'timestamp'
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
            segment_emissions = 0.0
            segment_distance = 0
            
            if instr_type == "DRIVE":
                # Calculate distance from path
                if hasattr(instruction, 'path') and instruction.path:
                    segment_distance = len(instruction.path) - 1  # Number of moves
                    
                    # Apply multiplier if loaded
                    multiplier = self.LOADED_MULTIPLIER if is_loaded else 1.0
                    segment_emissions = segment_distance * self.EMISSION_FACTOR_PER_SECTOR * multiplier
                    
                    total_distance += segment_distance
                    total_emissions += segment_emissions
                    
                    segment_num += 1
                    self._log_segment(job_seq, job_type, HT_name, f"DRIVE_{segment_num}", 
                                    segment_distance, segment_emissions, total_emissions, timestamp)
            
            elif instr_type in ["WORK_QC", "WORK_YARD"]:
                # After working at QC (DI) or Yard (LO), HT is loaded
                if (job_type == "DI" and instr_type == "WORK_QC") or \
                   (job_type == "LO" and instr_type == "WORK_YARD"):
                    is_loaded = True
                
                # Idle emissions during work
                work_duration = CONSTANT.JOB_PARAMETER.QC_WORK_TIME_REQUIRED if "QC" in instr_type else \
                               CONSTANT.JOB_PARAMETER.YARD_WORK_TIME_REQUIRED
                idle_emissions = (work_duration / 10) * self.IDLE_EMISSION_RATE * 10  # per 10s interval
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
        
        # Store record
        record = EmissionRecord(
            job_seq=job_seq,
            job_type=job_type,
            HT_name=HT_name,
            distance_traveled=total_distance,
            emissions_kg=total_emissions,
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
    
    def get_top_emitters(self, top_n: int = 10) -> List[tuple]:
        """Get top N HTs by emissions"""
        sorted_hts = sorted(self.emissions_by_ht.items(), key=lambda x: x[1], reverse=True)
        return sorted_hts[:top_n]
    
    def export_summary(self):
        """Export summary to CSV"""
        summary_file = self.data_folder / "emissions_summary.csv"
        summary = self.get_summary()
        
        with open(summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in summary.items():
                writer.writerow([key, value])
