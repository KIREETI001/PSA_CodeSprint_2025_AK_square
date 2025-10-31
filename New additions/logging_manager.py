"""
PSA CodeSprint 2025 - Centralized Logging Manager
==================================================
Handles all CSV logging operations for port terminal operations.
This module runs logging operations concurrently without impacting
the main job planning performance.

Author: PSA CodeSprint Team
Date: October 2025
"""

import os
import csv
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

# Setup logger
logger = logging.getLogger(__name__)


class LoggingManager:
    """
    Centralized manager for all port operations logging.
    Handles emission tracking, ETA monitoring, yard capacity, congestion,
    HT utilization, QC performance, route efficiency, and more.
    """
    
    def __init__(self, data_dir: str = os.path.join("App", "data")):
        """
        Initialize the logging manager with all CSV log files.
        
        Args:
            data_dir: Directory where log files will be stored
        """
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Define all log file paths
        self.log_paths = {
            'emission': os.path.join(data_dir, "emission_log.csv"),
            'eta': os.path.join(data_dir, "eta_tracker.csv"),
            'yard_capacity': os.path.join(data_dir, "yard_capacity_log.csv"),
            'congestion': os.path.join(data_dir, "congestion_log.csv"),
            'ht_utilization': os.path.join(data_dir, "ht_utilization_log.csv"),
            'route_efficiency': os.path.join(data_dir, "route_efficiency_log.csv"),
        }
        
        # Event counters
        self.counters = {
            'congestion_events': 0,
            'ht_jobs': {},
        }
        
        # Initialize all log files
        self._initialize_log_files()
    
    def _initialize_log_files(self):
        """Create all CSV log files with headers if they don't exist."""
        
        # Emission log
        self._init_csv(self.log_paths['emission'], [
            "timestamp", "job_id", "job_type", "QC", "Yard", "HT_name",
            "distance_sectors", "emission_kg"
        ])
        
        # ETA tracker
        self._init_csv(self.log_paths['eta'], [
            "timestamp", "job_id", "HT_name", "QC", "Yard",
            "distance_sectors", "ETA_seconds"
        ])
        
        # Yard capacity log
        self._init_csv(self.log_paths['yard_capacity'], [
            "timestamp", "yard_name", "total_jobs", "discharge_jobs",
            "load_jobs", "capacity_alert"
        ])
        
        # Congestion log
        self._init_csv(self.log_paths['congestion'], [
            "timestamp", "congestion_type", "location", "severity",
            "available_HTs", "pending_jobs", "strategy", "description"
        ])
        
        # HT Utilization log (NEW)
        self._init_csv(self.log_paths['ht_utilization'], [
            "timestamp", "HT_name", "status", "current_job_id",
            "jobs_completed", "total_distance", "active_time_sec",
            "idle_time_sec", "utilization_percent"
        ])
        
        # Route Efficiency log
        self._init_csv(self.log_paths['route_efficiency'], [
            "timestamp", "HT_name", "origin", "destination", "job_type",
            "distance_sectors", "actual_time_sec", "optimal_time_sec",
            "efficiency_percent", "congestion_encountered"
        ])
        
        logger.info("All log files initialized successfully")
    
    def _init_csv(self, path: str, headers: List[str]):
        """Initialize a CSV file with headers if it doesn't exist."""
        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(headers)
    
    def _write_log(self, log_type: str, data: List[Any]):
        """
        Write a log entry to the specified log file.
        Uses try-except to ensure logging never crashes the main application.
        """
        try:
            with open(self.log_paths[log_type], "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(data)
        except Exception as e:
            logger.debug(f"{log_type} log skipped: {e}")
    
    # ==================== EMISSION LOGGING ====================
    
    def log_emission(self, job_id: str, job_type: str, qc: str, yard: str,
                     ht_name: str, distance: int, emission: float):
        """Log carbon emission data for a job."""
        self._write_log('emission', [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            job_id, job_type, qc, yard, ht_name, distance, round(emission, 4)
        ])
    
    # ==================== ETA LOGGING ====================
    
    def log_eta(self, job_id: str, ht_name: str, qc: str, yard: str,
                distance: int, eta_seconds: int):
        """Log estimated time of arrival for a job."""
        self._write_log('eta', [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            job_id, ht_name, qc, yard, distance, eta_seconds
        ])
    
    # ==================== YARD CAPACITY LOGGING ====================
    
    def log_yard_capacity(self, yard_name: str, total_jobs: int,
                          discharge_jobs: int, load_jobs: int, alert: str = ""):
        """Log current yard capacity status."""
        self._write_log('yard_capacity', [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            yard_name, total_jobs, discharge_jobs, load_jobs, alert
        ])
    
    # ==================== CONGESTION LOGGING ====================
    
    def log_congestion(self, congestion_type: str, location: str, severity: str,
                       available_hts: int, pending_jobs: int, strategy: str,
                       description: str = ""):
        """Log congestion events during planning stage."""
        self._write_log('congestion', [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            congestion_type, location, severity, available_hts,
            pending_jobs, strategy, description
        ])
        self.counters['congestion_events'] += 1
        logger.info(f"[CONGESTION] {severity} {congestion_type} at {location}")
    
    # ==================== HT UTILIZATION LOGGING ====================
    
    def log_ht_utilization(self, ht_name: str, status: str, current_job_id: str,
                           jobs_completed: int, total_distance: int,
                           active_time: int, idle_time: int):
        """
        Log HT (Horizontal Transport) utilization metrics.
        
        Args:
            ht_name: Name of the HT
            status: Current status (ACTIVE, IDLE, MOVING, LOADING)
            current_job_id: ID of current job or "NONE"
            jobs_completed: Total jobs completed by this HT
            total_distance: Total distance traveled in sectors
            active_time: Time spent actively working (seconds)
            idle_time: Time spent idle (seconds)
        """
        total_time = active_time + idle_time
        utilization = (active_time / total_time * 100) if total_time > 0 else 0
        
        self._write_log('ht_utilization', [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ht_name, status, current_job_id, jobs_completed,
            total_distance, active_time, idle_time, round(utilization, 2)
        ])
    
    # ==================== ROUTE EFFICIENCY LOGGING ====================
    
    def log_route_efficiency(self, ht_name: str, origin: str, destination: str,
                             job_type: str, distance: int, actual_time: int,
                             optimal_time: int, congestion: bool = False):
        """
        Log route efficiency for HT travel patterns.
        
        Args:
            ht_name: Name of the HT
            origin: Starting location (QC or Yard name)
            destination: End location (QC or Yard name)
            job_type: Type of job (DI or LO)
            distance: Distance in sectors
            actual_time: Actual time taken (seconds)
            optimal_time: Theoretical optimal time (seconds)
            congestion: Whether congestion was encountered
        """
        efficiency = (optimal_time / actual_time * 100) if actual_time > 0 else 100
        
        self._write_log('route_efficiency', [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ht_name, origin, destination, job_type, distance,
            actual_time, optimal_time, round(efficiency, 2),
            "YES" if congestion else "NO"
        ])
    
    # ==================== BATCH LOGGING HELPERS ====================
    
    def log_job_complete(self, job_data: Dict[str, Any]):
        """
        Convenience method to log multiple metrics for a completed job.
        Extracts relevant data and calls appropriate logging methods.
        """
        # Log emission
        if 'emission' in job_data:
            self.log_emission(
                job_data.get('job_id', 'UNKNOWN'),
                job_data.get('job_type', 'UNKNOWN'),
                job_data.get('qc', 'UNKNOWN'),
                job_data.get('yard', 'UNKNOWN'),
                job_data.get('ht_name', 'UNKNOWN'),
                job_data.get('distance', 0),
                job_data['emission']
            )
        
        # Log ETA
        if 'eta' in job_data:
            self.log_eta(
                job_data.get('job_id', 'UNKNOWN'),
                job_data.get('ht_name', 'UNKNOWN'),
                job_data.get('qc', 'UNKNOWN'),
                job_data.get('yard', 'UNKNOWN'),
                job_data.get('distance', 0),
                job_data['eta']
            )
        
        # Log route efficiency
        if 'actual_time' in job_data and 'optimal_time' in job_data:
            self.log_route_efficiency(
                job_data.get('ht_name', 'UNKNOWN'),
                job_data.get('origin', 'UNKNOWN'),
                job_data.get('destination', 'UNKNOWN'),
                job_data.get('job_type', 'UNKNOWN'),
                job_data.get('distance', 0),
                job_data['actual_time'],
                job_data['optimal_time'],
                job_data.get('congestion', False)
            )
    
    def get_log_path(self, log_type: str) -> str:
        """Get the file path for a specific log type."""
        return self.log_paths.get(log_type, "")
    
    def get_counters(self) -> Dict[str, Any]:
        """Get current event counters."""
        return self.counters.copy()


# ==================== SINGLETON INSTANCE ====================

# Global singleton instance
_logging_manager_instance: Optional[LoggingManager] = None


def get_logging_manager(data_dir: str = os.path.join("App", "data")) -> LoggingManager:
    """
    Get or create the singleton LoggingManager instance.
    
    Args:
        data_dir: Directory for log files (only used on first call)
    
    Returns:
        LoggingManager instance
    """
    global _logging_manager_instance
    if _logging_manager_instance is None:
        _logging_manager_instance = LoggingManager(data_dir)
    return _logging_manager_instance
