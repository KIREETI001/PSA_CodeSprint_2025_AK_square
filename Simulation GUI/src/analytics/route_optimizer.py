"""
Route Optimization Analyzer
Analyzes and tracks route efficiency metrics
"""
import csv
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from dataclasses import dataclass

from src.floor import Coordinate
from src.constant import CONSTANT


@dataclass
class RouteMetrics:
    """Metrics for a single route"""
    job_seq: str
    job_type: str
    HT_name: str
    route_type: str  # BUFFER_TO_QC, QC_TO_BUFFER, etc.
    path_length: int
    optimal_path_length: int
    efficiency: float  # percentage
    detours: int
    backtracking: int


class RouteOptimizationAnalyzer:
    """Analyze route efficiency and optimization opportunities"""
    
    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_folder / "route_optimization.csv"
        self.summary_file = self.data_folder / "route_summary.csv"
        
        self.route_metrics: List[RouteMetrics] = []
        self.efficiency_by_type: Dict[str, List[float]] = defaultdict(list)
        
        # Optimal distances (Manhattan distance baseline)
        self.optimal_distances = {
            'BUFFER_TO_QC': 15,  # Average
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
                     route_type: str, path: List[Coordinate]) -> RouteMetrics:
        """Analyze a single route"""
        if not path or len(path) < 2:
            return None
        
        path_length = len(path) - 1  # Number of moves
        
        # Calculate optimal path (Manhattan distance between start and end)
        start, end = path[0], path[-1]
        manhattan_distance = abs(end.x - start.x) + abs(end.y - start.y)
        
        # Use predefined optimal or calculate
        optimal_length = self.optimal_distances.get(route_type, manhattan_distance)
        
        # Calculate efficiency
        efficiency = (optimal_length / max(path_length, 1)) * 100
        
        # Detect detours and backtracking
        detours = self._count_detours(path)
        backtracking = self._count_backtracking(path)
        
        metrics = RouteMetrics(
            job_seq=job_seq,
            job_type=job_type,
            HT_name=HT_name,
            route_type=route_type,
            path_length=path_length,
            optimal_path_length=optimal_length,
            efficiency=round(efficiency, 2),
            detours=detours,
            backtracking=backtracking
        )
        
        self.route_metrics.append(metrics)
        self.efficiency_by_type[route_type].append(efficiency)
        self._log_route(metrics)
        
        return metrics
    
    def _count_detours(self, path: List[Coordinate]) -> int:
        """Count unnecessary detours (90+ degree turns)"""
        if len(path) < 3:
            return 0
        
        detours = 0
        for i in range(1, len(path) - 1):
            prev_dir = self._get_direction(path[i-1], path[i])
            next_dir = self._get_direction(path[i], path[i+1])
            
            # If direction changes by 90+ degrees, count as detour
            if prev_dir and next_dir and self._is_sharp_turn(prev_dir, next_dir):
                detours += 1
        
        return detours
    
    def _count_backtracking(self, path: List[Coordinate]) -> int:
        """Count backtracking moves (moving in opposite direction)"""
        if len(path) < 3:
            return 0
        
        backtrack = 0
        for i in range(1, len(path) - 1):
            prev_dir = self._get_direction(path[i-1], path[i])
            next_dir = self._get_direction(path[i], path[i+1])
            
            # If moving in exact opposite direction
            if prev_dir and next_dir and self._is_opposite(prev_dir, next_dir):
                backtrack += 1
        
        return backtrack
    
    def _get_direction(self, from_coord: Coordinate, to_coord: Coordinate) -> str:
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
        else:
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
                metrics.job_seq,
                metrics.job_type,
                metrics.HT_name,
                metrics.route_type,
                metrics.path_length,
                metrics.optimal_path_length,
                f"{metrics.efficiency:.2f}",
                metrics.detours,
                metrics.backtracking,
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
    
    def get_efficiency_by_route_type(self) -> Dict[str, Dict]:
        """Get efficiency metrics grouped by route type"""
        result = {}
        for route_type, efficiencies in self.efficiency_by_type.items():
            if efficiencies:
                result[route_type] = {
                    'avg_efficiency': round(sum(efficiencies) / len(efficiencies), 2),
                    'min_efficiency': round(min(efficiencies), 2),
                    'max_efficiency': round(max(efficiencies), 2),
                    'count': len(efficiencies)
                }
        return result
    
    def get_improvement_opportunities(self) -> List[Dict]:
        """Identify routes with improvement opportunities"""
        opportunities = []
        for metrics in self.route_metrics:
            if metrics.efficiency < 80 or metrics.detours > 2 or metrics.backtracking > 0:
                opportunities.append({
                    'job_seq': metrics.job_seq,
                    'route_type': metrics.route_type,
                    'efficiency': metrics.efficiency,
                    'detours': metrics.detours,
                    'backtracking': metrics.backtracking,
                    'potential_savings': metrics.path_length - metrics.optimal_path_length
                })
        
        # Sort by potential savings
        opportunities.sort(key=lambda x: x['potential_savings'], reverse=True)
        return opportunities[:20]  # Top 20
    
    def export_summary(self):
        """Export summary to CSV"""
        with open(self.summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Overall summary
            writer.writerow(['=== OVERALL EFFICIENCY ==='])
            summary = self.get_efficiency_summary()
            for key, value in summary.items():
                writer.writerow([key, value])
            
            writer.writerow([])
            writer.writerow(['=== EFFICIENCY BY ROUTE TYPE ==='])
            writer.writerow(['Route Type', 'Avg Efficiency', 'Min', 'Max', 'Count'])
            
            by_type = self.get_efficiency_by_route_type()
            for route_type, metrics in by_type.items():
                writer.writerow([
                    route_type,
                    metrics['avg_efficiency'],
                    metrics['min_efficiency'],
                    metrics['max_efficiency'],
                    metrics['count']
                ])
