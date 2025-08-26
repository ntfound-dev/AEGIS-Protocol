# performance_monitor.py
# Performance monitoring dan SLA enforcement sesuai PDF

import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    event_id: str
    detection_time: float  # seconds
    notification_time: float  # seconds
    dao_creation_time: float  # seconds
    physical_response_time: Optional[float] = None  # seconds
    sla_compliance: Dict[str, bool] = None

class PerformanceMonitor:
    """
    Performance Monitor - SLA enforcement
    Sesuai PDF targets:
    - Deteksi <30 detik
    - Notifikasi relawan <60 detik  
    - Bantuan fisik <4 jam
    """
    
    def __init__(self):
        self.sla_targets = {
            "detection_time": 30,  # seconds - sesuai PDF
            "notification_time": 60,  # seconds - sesuai PDF
            "dao_creation_time": 120,  # 2 minutes
            "physical_response_time": 4 * 3600  # 4 hours - sesuai PDF
        }
        self.event_timestamps = {}  # event_id -> timestamps
        self.performance_history: List[PerformanceMetrics] = []
        self.logger = logging.getLogger("aegis.performance")
    
    def start_tracking(self, event_id: str, stage: str):
        """Start tracking performance untuk event"""
        if event_id not in self.event_timestamps:
            self.event_timestamps[event_id] = {}
        
        self.event_timestamps[event_id][f"{stage}_start"] = time.time()
        
        if stage == "detection":
            self.event_timestamps[event_id]["event_start"] = time.time()
            self.logger.info(f"⏱️  Started tracking {event_id}")
    
    def end_tracking(self, event_id: str, stage: str):
        """End tracking untuk stage tertentu"""
        if event_id not in self.event_timestamps:
            return
            
        end_key = f"{stage}_end"
        self.event_timestamps[event_id][end_key] = time.time()
        
        # Calculate stage duration
        start_key = f"{stage}_start"
        if start_key in self.event_timestamps[event_id]:
            duration = (self.event_timestamps[event_id][end_key] - 
                       self.event_timestamps[event_id][start_key])
            
            self.event_timestamps[event_id][f"{stage}_duration"] = duration
            
            # Check SLA for this stage
            sla_met = duration <= self.sla_targets.get(f"{stage}_time", float('inf'))
            status = "✅" if sla_met else "❌"
            
            self.logger.info(f"{status} {stage.title()}: {duration:.2f}s (SLA: {self.sla_targets.get(f'{stage}_time', 'N/A')}s)")
    
    def record_physical_response(self, event_id: str, volunteer_id: str, arrival_time_hours: float):
        """Record physical response time"""
        if event_id not in self.event_timestamps:
            return
            
        response_time = arrival_time_hours * 3600  # Convert to seconds
        
        # Record first responder time
        if "first_physical_response" not in self.event_timestamps[event_id]:
            self.event_timestamps[event_id]["first_physical_response"] = response_time
            
            sla_met = response_time <= self.sla_targets["physical_response_time"]
            status = "✅" if sla_met else "❌"
            
            self.logger.info(f"{status} Physical Response: {arrival_time_hours:.1f}h (SLA: 4h)")
    
    def generate_performance_report(self, event_id: str) -> PerformanceMetrics:
        """Generate performance report untuk event"""
        if event_id not in self.event_timestamps:
            return None
            
        timestamps = self.event_timestamps[event_id]
        
        # Calculate durations
        detection_time = timestamps.get("detection_duration", 0)
        notification_time = timestamps.get("notification_duration", 0) 
        dao_creation_time = timestamps.get("dao_creation_duration", 0)
        physical_response_time = timestamps.get("first_physical_response", None)
        
        # Check SLA compliance
        sla_compliance = {
            "detection_sla": detection_time <= self.sla_targets["detection_time"],
            "notification_sla": notification_time <= self.sla_targets["notification_time"],
            "dao_creation_sla": dao_creation_time <= self.sla_targets["dao_creation_time"],
            "physical_response_sla": (physical_response_time is None or 
                                    physical_response_time <= self.sla_targets["physical_response_time"])
        }
        
        metrics = PerformanceMetrics(
            event_id=event_id,
            detection_time=detection_time,
            notification_time=notification_time,
            dao_creation_time=dao_creation_time,
            physical_response_time=physical_response_time,
            sla_compliance=sla_compliance
        )
        
        self.performance_history.append(metrics)
        
        # Log final report
        self._log_performance_summary(metrics)
        
        return metrics
    
    def _log_performance_summary(self, metrics: PerformanceMetrics):
        """Log performance summary"""
        compliance = metrics.sla_compliance
        total_slas = len([v for v in compliance.values() if v is True])
        total_checked = len(compliance)
        
        self.logger.info(f"""
📊 PERFORMANCE REPORT - {metrics.event_id}
─────────────────────────────────
Detection Time:    {metrics.detection_time:.2f}s {'✅' if compliance['detection_sla'] else '❌'} (Target: 30s)
Notification Time: {metrics.notification_time:.2f}s {'✅' if compliance['notification_sla'] else '❌'} (Target: 60s)  
DAO Creation:      {metrics.dao_creation_time:.2f}s {'✅' if compliance['dao_creation_sla'] else '❌'} (Target: 120s)
Physical Response: {(metrics.physical_response_time/3600):.1f}h {'✅' if compliance['physical_response_sla'] else '❌'} (Target: 4h)

SLA Compliance: {total_slas}/{total_checked} targets met
        """)
    
    def get_system_performance_stats(self) -> Dict:
        """Get overall system performance statistics"""
        if not self.performance_history:
            return {"status": "no_data"}
        
        recent_events = self.performance_history[-10:]  # Last 10 events
        
        # Calculate averages
        avg_detection = sum(m.detection_time for m in recent_events) / len(recent_events)
        avg_notification = sum(m.notification_time for m in recent_events) / len(recent_events)
        
        # Calculate SLA compliance rates
        detection_compliance = sum(1 for m in recent_events if m.sla_compliance["detection_sla"]) / len(recent_events)
        notification_compliance = sum(1 for m in recent_events if m.sla_compliance["notification_sla"]) / len(recent_events)
        
        # Physical response stats (exclude None values)
        physical_times = [m.physical_response_time for m in recent_events if m.physical_response_time]
        avg_physical = sum(physical_times) / len(physical_times) if physical_times else 0
        physical_compliance = sum(1 for m in recent_events if m.sla_compliance["physical_response_sla"]) / len(recent_events)
        
        return {
            "total_events_tracked": len(self.performance_history),
            "recent_events": len(recent_events),
            "averages": {
                "detection_time": round(avg_detection, 2),
                "notification_time": round(avg_notification, 2),  
                "physical_response_hours": round(avg_physical/3600, 1) if avg_physical else 0
            },
            "sla_compliance_rates": {
                "detection": f"{detection_compliance:.1%}",
                "notification": f"{notification_compliance:.1%}",
                "physical_response": f"{physical_compliance:.1%}"
            },
            "targets": {
                "detection": "30 seconds",
                "notification": "60 seconds", 
                "physical_response": "4 hours"
            }
        }
    
    def alert_sla_violation(self, event_id: str, stage: str, actual_time: float):
        """Alert untuk SLA violation"""
        target = self.sla_targets.get(f"{stage}_time", 0)
        if actual_time > target:
            violation_percent = ((actual_time - target) / target) * 100
            
            self.logger.warning(f"""
🚨 SLA VIOLATION ALERT
Event: {event_id}
Stage: {stage}
Actual: {actual_time:.2f}s
Target: {target}s
Violation: +{violation_percent:.1f}%
            """)
    
    def cleanup_old_data(self, days: int = 7):
        """Cleanup old tracking data"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Keep only recent performance history
        self.performance_history = [
            m for m in self.performance_history 
            if datetime.fromisoformat(m.event_id.split('_')[-1]) > cutoff
        ]
        
        # Clear old timestamps
        old_events = []
        for event_id in self.event_timestamps:
            try:
                # Extract timestamp from event_id (assuming format evt_timestamp)
                if len(event_id.split('_')) > 1:
                    old_events.append(event_id)
            except:
                pass
        
        for event_id in old_events:
            del self.event_timestamps[event_id]
        
        self.logger.info(f"Cleaned up data older than {days} days")