"""
Yard Job Counter
Tracks completed jobs per yard, split by DI and LO
"""
import csv
from pathlib import Path
from typing import Dict
from collections import defaultdict

from src.constant import CONSTANT


class YardJobCounter:
    """Count and track jobs completed at each yard"""
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_folder / "yard_job_counts.csv"
        
        # Initialize counters for all 16 yards
        self.yard_totals: Dict[str, int] = {yard: 0 for yard in CONSTANT.YARD_FLOOR.YARD_NAMES}
        self.yard_di_counts: Dict[str, int] = {yard: 0 for yard in CONSTANT.YARD_FLOOR.YARD_NAMES}
        self.yard_lo_counts: Dict[str, int] = {yard: 0 for yard in CONSTANT.YARD_FLOOR.YARD_NAMES}
        
        # Track job details
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
            # Handle unexpected yard names
            self.yard_totals[yard_name] = 0
            self.yard_di_counts[yard_name] = 0
            self.yard_lo_counts[yard_name] = 0
        
        # Update counters
        self.yard_totals[yard_name] += 1
        if job_type == "DI":
            self.yard_di_counts[yard_name] += 1
        else:
            self.yard_lo_counts[yard_name] += 1
        
        # Store history
        self.job_history.append({
            'yard_name': yard_name,
            'job_type': job_type,
            'job_seq': job_seq,
            'completion_time': completion_time
        })
        
        # Log to CSV
        self._log_job(yard_name, job_type, job_seq, completion_time)
    
    def _log_job(self, yard_name: str, job_type: str, job_seq: str, completion_time: float):
        """Log job completion to CSV"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                yard_name,
                job_type,
                job_seq,
                f"{completion_time:.2f}",
                self.yard_totals[yard_name],
                self.yard_di_counts[yard_name],
                self.yard_lo_counts[yard_name]
            ])
    
    def get_yard_summary(self, yard_name: str) -> Dict:
        """Get summary for a specific yard"""
        return {
            'yard_name': yard_name,
            'total_jobs': self.yard_totals.get(yard_name, 0),
            'di_jobs': self.yard_di_counts.get(yard_name, 0),
            'lo_jobs': self.yard_lo_counts.get(yard_name, 0),
            'di_percentage': round((self.yard_di_counts.get(yard_name, 0) / 
                                   max(self.yard_totals.get(yard_name, 0), 1)) * 100, 1),
            'lo_percentage': round((self.yard_lo_counts.get(yard_name, 0) / 
                                   max(self.yard_totals.get(yard_name, 0), 1)) * 100, 1)
        }
    
    def get_all_yards_summary(self) -> list:
        """Get summary for all yards"""
        return [self.get_yard_summary(yard) for yard in CONSTANT.YARD_FLOOR.YARD_NAMES]
    
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
    
    def get_top_yards(self, top_n: int = 5) -> list:
        """Get top N busiest yards"""
        sorted_yards = sorted(self.yard_totals.items(), key=lambda x: x[1], reverse=True)
        return [{'yard': yard, 'jobs': count} for yard, count in sorted_yards[:top_n]]
    
    def export_summary(self):
        """Export summary to CSV"""
        summary_file = self.data_folder / "yard_summary.csv"
        
        with open(summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Yard', 'Total_Jobs', 'DI_Jobs', 'LO_Jobs', 'DI_%', 'LO_%'])
            
            for yard in CONSTANT.YARD_FLOOR.YARD_NAMES:
                summary = self.get_yard_summary(yard)
                writer.writerow([
                    summary['yard_name'],
                    summary['total_jobs'],
                    summary['di_jobs'],
                    summary['lo_jobs'],
                    summary['di_percentage'],
                    summary['lo_percentage']
                ])
