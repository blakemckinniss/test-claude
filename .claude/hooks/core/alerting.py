"""
Alerting module for Claude Code hooks.
Provides alerting system for critical issues.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .utils.utils import log_to_file

# Define LOGS_DIR
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


class AlertingSystem:
    """Simple alerting system for critical issues"""

    def __init__(self, alert_file=None):
        self.alert_file = alert_file or (LOGS_DIR / "alerts.log")
        self.alert_thresholds = {
            'memory_percent': 85.0,
            'cpu_percent': 90.0,
            'disk_percent': 90.0,
            'process_memory_mb': 200.0
        }
        self.alert_cooldown = {}  # Prevent spam alerts
        self.cooldown_period = 300  # 5 minutes
        self.active_alerts = []  # Store active alerts

    def check_and_alert(self, stats: dict[str, Any]):
        """Check stats and send alerts if thresholds exceeded"""
        if 'error' in stats:
            return

        current_time = time.time()

        # Check system memory
        memory_percent = stats['system']['memory_percent']
        if memory_percent > self.alert_thresholds['memory_percent']:
            self._send_alert('high_memory', f"High system memory usage: {memory_percent:.1f}%", current_time)

        # Check system CPU
        cpu_percent = stats['system']['cpu_percent']
        if cpu_percent > self.alert_thresholds['cpu_percent']:
            self._send_alert('high_cpu', f"High system CPU usage: {cpu_percent:.1f}%", current_time)

        # Check disk usage
        disk_percent = stats['system']['disk_percent']
        if disk_percent > self.alert_thresholds['disk_percent']:
            self._send_alert('high_disk', f"High disk usage: {disk_percent:.1f}%", current_time)

        # Check process memory
        process_memory_mb = stats['process']['memory_rss'] / (1024 * 1024)
        if process_memory_mb > self.alert_thresholds['process_memory_mb']:
            self._send_alert('high_process_memory', f"High process memory: {process_memory_mb:.1f}MB", current_time)

    def _send_alert(self, alert_type: str, message: str, current_time: float):
        """Send an alert if not in cooldown period"""
        last_alert = self.alert_cooldown.get(alert_type, 0)

        if current_time - last_alert > self.cooldown_period:
            alert_msg = f"🚨 ALERT [{datetime.fromtimestamp(current_time)}]: {message}"

            # Add to active alerts
            alert_data = {
                'type': alert_type,
                'message': message,
                'timestamp': current_time,
                'resolved': False
            }
            self.active_alerts.append(alert_data)

            # Log to alert file
            try:
                with open(self.alert_file, 'a') as f:
                    f.write(f"{alert_msg}\n")
            except Exception as e:
                log_to_file(f"❌ Failed to write alert: {e}")

            # Also log to main log
            log_to_file(alert_msg)

            # Update cooldown
            self.alert_cooldown[alert_type] = current_time

    def send_custom_alert(self, alert_type: str, message: str):
        """Send a custom alert with cooldown checking"""
        current_time = time.time()
        self._send_alert(alert_type, message, current_time)

    def set_threshold(self, metric: str, value: float):
        """Update alert threshold for a specific metric"""
        if metric in self.alert_thresholds:
            old_value = self.alert_thresholds[metric]
            self.alert_thresholds[metric] = value
            log_to_file(f"🔧 Updated alert threshold for {metric}: {old_value} → {value}")

    def get_thresholds(self) -> dict[str, float]:
        """Get current alert thresholds"""
        return self.alert_thresholds.copy()

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get list of active (unresolved) alerts"""
        # Filter out resolved alerts and alerts older than 1 hour
        current_time = time.time()
        active = []
        for alert in self.active_alerts:
            if not alert.get('resolved', False) and (current_time - alert['timestamp']) < 3600:
                active.append(alert.copy())
        return active

    def resolve_alert(self, alert_type: str):
        """Mark alerts of a specific type as resolved"""
        for alert in self.active_alerts:
            if alert['type'] == alert_type and not alert.get('resolved', False):
                alert['resolved'] = True
                log_to_file(f"✅ Resolved alert: {alert_type}")

    def clear_old_alerts(self, max_age_hours: int = 24):
        """Remove alerts older than specified hours"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)

        original_count = len(self.active_alerts)
        self.active_alerts = [
            alert for alert in self.active_alerts
            if alert['timestamp'] > cutoff_time
        ]
        removed_count = original_count - len(self.active_alerts)

        if removed_count > 0:
            log_to_file(f"🗑️ Cleared {removed_count} old alerts")

    def reset_cooldown(self, alert_type: str | None = None):
        """Reset cooldown for specific alert type or all alerts"""
        if alert_type:
            if alert_type in self.alert_cooldown:
                del self.alert_cooldown[alert_type]
                log_to_file(f"Reset cooldown for alert type: {alert_type}")
        else:
            self.alert_cooldown.clear()
            log_to_file("Reset all alert cooldowns")

    def get_alert_history(self, limit: int = 50) -> list:
        """Read recent alerts from the alert file"""
        alerts = []

        try:
            if self.alert_file.exists():
                with open(self.alert_file) as f:
                    lines = f.readlines()
                    # Get the last 'limit' lines
                    alerts = lines[-limit:] if len(lines) > limit else lines
                    # Strip newlines
                    alerts = [line.strip() for line in alerts]
        except Exception as e:
            logger.error(f"Failed to read alert history: {e}")

        return alerts


# Export main components
__all__ = ['AlertingSystem']
