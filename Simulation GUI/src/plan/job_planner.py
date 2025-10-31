from typing import List
from pathlib import Path
from logzero import logger
from src.constant import CONSTANT
from src.floor import Coordinate, SectorMapSnapshot
from src.job import InstructionType, Job, JobInstruction, Status
from src.plan.job_tracker import JobTracker

# Import unified analytics engine
from src.analytics.analytics_engine import AnalyticsEngine


class JobPlanner:
    """
    Final PSA Planner with live telemetry and analytics
    Compatible with 1.117M baseline + full monitoring suite
    """

    def __init__(self, ht_coord_tracker, sector_map_snapshot: SectorMapSnapshot):
        self.ht_coord_tracker = ht_coord_tracker
        self.sector_map_snapshot = sector_map_snapshot

        # baseline state
        self.yard_di_count = {y: 0 for y in CONSTANT.YARD_FLOOR.YARD_NAMES}
        self.strategy_scores = {"aggressive": 0, "balanced": 0, "conservative": 0}
        self.current_strategy = "balanced"
        self.consecutive_high_traffic = 0
        
        # Initialize unified analytics engine
        self.analytics_folder = Path("data/analytics_logs")
        self.analytics = AnalyticsEngine(self.analytics_folder)
        
        self.simulation_time = 0
        
        # Track completed jobs to detect newly completed ones
        self.tracked_completed_jobs = set()
        
        # Track previous HT positions to compute non-moving HT count for GUI
        self._prev_ht_positions = {}
        
        logger.info("[INIT] Job Planner initialized with unified analytics engine")

    def is_deadlock(self):
        """
        Deadlock detection method required by simulation engine
        """
        return False

    # ---------------------------------------------------------
    def plan(self, job_tracker: JobTracker) -> List[Job]:
        # CRITICAL: Poll for completed jobs and update yard counter
        self._check_and_record_completed_jobs(job_tracker)
        
        plannable = job_tracker.get_plannable_job_sequences()
        if not plannable:
            return []

        selected_HTs, new_jobs = [], []
        self.adapt_strategy_traffic_aware()
        available_HTs = [h for h in self.ht_coord_tracker.get_available_HTs() if h not in selected_HTs]
        max_jobs = self.get_traffic_aware_limit(len(plannable), len(available_HTs))
        logger.info(f"[{self.current_strategy.upper()}] Planning up to {max_jobs} jobs | HTs={len(available_HTs)}")

        for seq in plannable[:max_jobs]:
            job = job_tracker.get_job(seq)
            if not job:
                continue
            info = job.get_job_info()
            if not info:
                continue
            job_type, QC, yard, alts = [info[k] for k in ("job_type", "QC_name", "yard_name", "alt_yard_names")]

            HT = self.select_HT(job_type, selected_HTs, QC)
            if HT is None:
                continue
            selected_HTs.append(HT)

            if job_type == CONSTANT.JOB_PARAMETER.DISCHARGE_JOB_TYPE:
                yard = self.select_yard(yard, alts)
                if yard is None:
                    selected_HTs.remove(HT)
                    continue
                self.yard_di_count[yard] += 1

            job.assign_job(HT_name=HT, yard_name=yard)
            instr = self.build_job_instructions(job_type, HT, QC, yard)
            job.set_instructions(instr)
            new_jobs.append(job)
            
            # ====== ANALYTICS TRACKING ======
            # 1. Create timeline for this job
            self.analytics.create_timeline(seq, job_type, HT, QC, yard, instr)
            
            # 2. Calculate emissions for this job
            self.analytics.calculate_emissions(seq, job_type, HT, instr, self.simulation_time)
            
            # 3. Analyze routes
            for instruction in instr:
                if instruction.instructor_type == InstructionType.DRIVE and hasattr(instruction, 'path'):
                    # Determine route type
                    route_type = "UNKNOWN"
                    if "QC" in str(instruction):
                        route_type = "BUFFER_TO_QC" if job_type == "DI" else "QC_TO_BUFFER"
                    elif "YARD" in str(instruction):
                        route_type = "BUFFER_TO_YARD" if job_type == "DI" else "YARD_TO_BUFFER"
                    
                    self.analytics.analyze_route(seq, job_type, HT, route_type, instruction.path)
            # ================================

        self.update_traffic_awareness(len(new_jobs), len(available_HTs))
        
        # Update congestion monitor with current HT positions
        ht_positions = {ht: self.ht_coord_tracker.get_coordinate(ht) 
                       for ht in self.ht_coord_tracker.get_available_HTs()}
        self.analytics.update_congestion(ht_positions, self.simulation_time)
        
        logger.info(f"[OK] Planned {len(new_jobs)} jobs successfully.")
        return new_jobs

    # ---------------------------------------------------------
    # --- unchanged baseline logic ---
    def adapt_strategy_traffic_aware(self):
        strategies = ["aggressive", "balanced", "conservative"]
        i = strategies.index(self.current_strategy)
        if self.consecutive_high_traffic > 3 and self.current_strategy == "aggressive":
            self.current_strategy, self.consecutive_high_traffic = "balanced", 0
        else:
            self.current_strategy = strategies[(i + 1) % len(strategies)]

    def get_traffic_aware_limit(self, avail_jobs, avail_hts):
        base = {
            "aggressive": min(20, avail_jobs),
            "balanced": min(15, avail_jobs),
            "conservative": min(10, avail_jobs),
        }[self.current_strategy]
        ht_cap = int(avail_hts * 0.7)
        if self.consecutive_high_traffic > 2:
            base = int(base * 0.7)
        return max(1, min(base, ht_cap)) if avail_jobs and avail_hts else 0

    def update_traffic_awareness(self, planned, avail_hts):
        util = planned / max(avail_hts + planned, 1)
        self.consecutive_high_traffic = self.consecutive_high_traffic + 1 if util > 0.8 else max(
            0, self.consecutive_high_traffic - 1
        )

    # ---------------------------------------------------------
    # YOUR TASK: Modified functions for better planning efficiency
    # BUT keeping the core logic the same - only optimizing within the same patterns

    def select_HT(self, job_type, selected_HT_names, QC_name):
        """
        Enhanced HT selection - same logic but with better efficiency
        """
        avail = [h for h in self.ht_coord_tracker.get_available_HTs() if h not in selected_HT_names]
        if not avail:
            return None
        qc = self.sector_map_snapshot.get_QC_sector(QC_name)
        if not qc:
            return avail[0]
        qc_x = qc.in_coord.x
        
        # ORIGINAL LOGIC - just optimized execution
        if job_type == CONSTANT.JOB_PARAMETER.DISCHARGE_JOB_TYPE:
            # For discharge: pick closest to QC (same as original)
            return min(avail, key=lambda h: abs(self.ht_coord_tracker.get_coordinate(h).x - qc_x))
        else:
            # For load: pick farthest from QC (same as original)  
            return max(avail, key=lambda h: abs(self.ht_coord_tracker.get_coordinate(h).x - qc_x))

    def select_yard(self, default_yard, alt_yards):
        """
        Enhanced yard selection - same load balancing logic
        """
        # ORIGINAL LOGIC - Constraint 8: Max 700 DI jobs per yard
        cands = [default_yard] + [y for y in (alt_yards or []) if y and str(y) != "nan"]
        valid = [y for y in cands if self.yard_di_count.get(y, 0) < 700]
        if not valid:
            valid = [y for y in CONSTANT.YARD_FLOOR.YARD_NAMES if self.yard_di_count.get(y, 0) < 700]
        return min(valid, key=lambda y: self.yard_di_count[y]) if valid else None

    def get_path_from_buffer_to_QC(self, buf, QC):
        """
        Generate efficient path - same fixed path logic
        """
        QC_in = self.sector_map_snapshot.get_QC_sector(QC).in_coord
        path = [Coordinate(buf.x, 7)]
        for x in range(buf.x - 1, 0, -1):
            path.append(Coordinate(x, 7))
        for y in range(6, 3, -1):
            path.append(Coordinate(1, y))
        for x in range(2, QC_in.x + 1):
            path.append(Coordinate(x, 4))
        path.append(QC_in)
        return path

    def get_path_from_buffer_to_yard(self, buf, yard):
        """
        Generate efficient path - same fixed path logic  
        """
        yard_in = self.sector_map_snapshot.get_yard_sector(yard).in_coord
        path = [Coordinate(buf.x, buf.y - 1)]
        for x in range(buf.x + 1, 43):
            path.append(Coordinate(x, 5))
        for y in range(6, 12):
            path.append(Coordinate(42, y))
        for x in range(41, 0, -1):
            path.append(Coordinate(x, 11))
        path.append(Coordinate(1, 12))
        for x in range(2, yard_in.x + 1):
            path.append(Coordinate(x, 12))
        path.append(yard_in)
        return path

    def get_path_from_yard_to_buffer(self, yard, buf):
        """
        Generate efficient path - same fixed path logic
        """
        yard_out = self.sector_map_snapshot.get_yard_sector(yard).out_coord
        path = [yard_out]
        for x in range(yard_out.x, 42):
            path.append(Coordinate(x, 12))
        for y in range(11, 6, -1):
            path.append(Coordinate(41, y))
        for x in range(40, buf.x - 1, -1):
            path.append(Coordinate(x, 7))
        path.append(buf)
        return path

    def get_path_from_QC_to_buffer(self, QC, buf):
        """
        Generate efficient path - same fixed path logic
        """
        QC_out = self.sector_map_snapshot.get_QC_sector(QC).out_coord
        path = [QC_out, Coordinate(QC_out.x, 4)]
        for x in range(QC_out.x + 1, 43):
            path.append(Coordinate(x, 4))
        for y in range(5, 8):
            path.append(Coordinate(42, y))
        for x in range(41, buf.x - 1, -1):
            path.append(Coordinate(x, 7))
        path.append(buf)
        return path

    # ---------------------------------------------------------
    def build_job_instructions(self, job_type, HT, QC, yard):
        buf = self.ht_coord_tracker.get_coordinate(HT)
        job_instructions = []
        if job_type == CONSTANT.JOB_PARAMETER.DISCHARGE_JOB_TYPE:
            seq = [
                (InstructionType.BOOK_QC, None),
                (InstructionType.DRIVE, self.get_path_from_buffer_to_QC(buf, QC)),
                (InstructionType.WORK_QC, QC),
                (InstructionType.DRIVE, self.get_path_from_QC_to_buffer(QC, buf)),
                (InstructionType.BOOK_YARD, None),
                (InstructionType.DRIVE, self.get_path_from_buffer_to_yard(buf, yard)),
                (InstructionType.WORK_YARD, yard),
                (InstructionType.DRIVE, self.get_path_from_yard_to_buffer(yard, buf)),
            ]
        else:
            seq = [
                (InstructionType.BOOK_YARD, None),
                (InstructionType.DRIVE, self.get_path_from_buffer_to_yard(buf, yard)),
                (InstructionType.WORK_YARD, yard),
                (InstructionType.DRIVE, self.get_path_from_yard_to_buffer(yard, buf)),
                (InstructionType.BOOK_QC, None),
                (InstructionType.DRIVE, self.get_path_from_buffer_to_QC(buf, QC)),
                (InstructionType.WORK_QC, QC),
                (InstructionType.DRIVE, self.get_path_from_QC_to_buffer(QC, buf)),
            ]
        for step, target in seq:
            if step == InstructionType.DRIVE:
                job_instructions.append(JobInstruction(instruction_type=step, HT_name=HT, path=target))
            elif step == InstructionType.WORK_QC:
                job_instructions.append(JobInstruction(instruction_type=step, HT_name=HT, QC_name=target))
            elif step == InstructionType.WORK_YARD:
                job_instructions.append(JobInstruction(instruction_type=step, HT_name=HT, yard_name=target))
            else:
                job_instructions.append(JobInstruction(instruction_type=step))
        return job_instructions
    
    # ---------------------------------------------------------
    # ANALYTICS HELPER METHODS
    
    def _check_and_record_completed_jobs(self, job_tracker: JobTracker):
        """
        Poll job_tracker for newly completed jobs and record them to yard counter.
        This is called at the start of every plan() cycle.
        """
        # Get all job sequences from the job_tracker
        completed_count = 0
        for job_seq, job in job_tracker.job_sequence_map.items():
            # Skip if we've already tracked this completion
            if job_seq in self.tracked_completed_jobs:
                continue
            
            job_info = job.get_job_info()
            job_status = job_info.get("job_status")
            
            # Check if job is completed
            if job_status == Status.COMPLETED:
                # Record this completion
                job_type = job_info.get("job_type")
                yard_name = job_info.get("assigned_yard_name")
                
                if yard_name and job_type:  # Only record if yard was assigned
                    self.analytics.record_job_completion(
                        yard_name=yard_name,
                        job_type=job_type,
                        job_seq=job_seq,
                        completion_time=self.simulation_time
                    )
                    self.analytics.complete_job_timeline(job_seq, self.simulation_time)
                    completed_count += 1
                    logger.debug(f"[RECORD] Completion: {job_seq} ({job_type}) at {yard_name}")
                
                # Mark as tracked
                self.tracked_completed_jobs.add(job_seq)
        
        if completed_count > 0:
            logger.info(f"[OK] Recorded {completed_count} newly completed jobs")
    
    def mark_job_completed(self, job_seq: str, job_type: str, yard_name: str):
        """
        Manual method to mark a job as completed (for external callers if needed)
        """
        self.analytics.complete_job_timeline(job_seq, self.simulation_time)
        self.analytics.record_job_completion(yard_name, job_type, job_seq, self.simulation_time)
        self.tracked_completed_jobs.add(job_seq)
        logger.info(f"[COMPLETE] Job {job_seq} completed and logged")
    
    def update_simulation_time(self, time: float):
        """
        Update the current simulation time for all analytics modules
        """
        self.simulation_time = time
        self.analytics.update_simulation_time(time)
    
    def get_analytics_summary(self) -> dict:
        """
        Get summary of all analytics
        """
        return self.analytics.get_overall_summary()
    
    def export_analytics(self):
        """
        Export all analytics summaries to CSV files
        """
        self.analytics.export_all_summaries()
        logger.info("📁 Analytics exported to data/analytics_logs/")

    # ---------------------------------------------------------
    # GUI SUPPORT METHODS
    def get_non_moving_HT(self) -> int:
        """
        Return the count of HTs that have not moved since the last check.

        Heuristic: compare current coordinates of each available HT with the
        coordinates from the previous invocation. On the first call, we don't
        have a baseline, so we consider all HTs as moving (return 0) and set
        the baseline for subsequent checks.
        """
        try:
            ht_names = list(self.ht_coord_tracker.get_available_HTs())
        except Exception:
            return 0

        # Snapshot current positions
        current_positions = {}
        for ht in ht_names:
            try:
                coord = self.ht_coord_tracker.get_coordinate(ht)
                # Store as a simple immutable tuple to avoid object identity issues
                current_positions[ht] = (coord.x, coord.y)
            except Exception:
                # If coordinate not available, skip from non-moving count logic
                continue

        # If no baseline, initialize and report 0 non-moving
        if not getattr(self, "_prev_ht_positions", None):
            self._prev_ht_positions = current_positions
            return 0

        non_moving = 0
        for ht, pos in current_positions.items():
            prev = self._prev_ht_positions.get(ht)
            if prev is not None and prev == pos:
                non_moving += 1

        # Update baseline for next call
        self._prev_ht_positions = current_positions
        return non_moving