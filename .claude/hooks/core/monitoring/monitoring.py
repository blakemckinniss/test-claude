"""
System monitoring module for Claude Code hooks.
Monitors system resources, file changes, and provides alerting.
"""

import json
import logging
import os
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Import system monitoring libraries
import psutil

from ..alerting import AlertingSystem
from ..utils.utils import log_to_file

# Define LOGS_DIR
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

# Check if watchdog is available
WATCHDOG_AVAILABLE = False
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    Observer = None  # type: ignore
    FileSystemEventHandler = None  # type: ignore


class FileChangeHandler:
    """Base class for handling file system changes"""

    def __init__(self, monitoring_system: 'SystemMonitor'):
        self.monitoring_system = monitoring_system
        self.last_event_time: dict[str, float] = defaultdict(float)
        self.debounce_interval = 0.5  # Prevent spam events

    def _should_process_event(self, file_path: str) -> bool:
        """Check if event should be processed (debouncing)"""
        current_time = time.time()
        last_time = self.last_event_time[file_path]

        if current_time - last_time > self.debounce_interval:
            self.last_event_time[file_path] = current_time
            return True
        return False

    def handle_file_change(self, file_path: str, change_type: str):
        """Handle a file change event"""
        if self._should_process_event(file_path):
            rel_path = os.path.relpath(file_path) if file_path != 'unknown' else 'unknown'

            # Log file change with appropriate emoji
            emoji_map = {
                'modified': '📝',
                'created': '📄',
                'deleted': '🗑️'
            }
            emoji = emoji_map.get(change_type, '📋')
            log_to_file(f"{emoji} File {change_type}: {rel_path}")

            # Update monitoring system
            self.monitoring_system.record_file_change(file_path, change_type)


# Create the appropriate file handler based on watchdog availability
if WATCHDOG_AVAILABLE and FileSystemEventHandler is not None:
    class WatchdogFileHandler(FileSystemEventHandler, FileChangeHandler):
        """Watchdog-based file system event handler"""

        def __init__(self, monitoring_system: 'SystemMonitor'):
            # Initialize FileChangeHandler which has actual initialization logic
            FileChangeHandler.__init__(self, monitoring_system)
            # FileSystemEventHandler doesn't require special initialization

        def on_modified(self, event: Any) -> None:
            """Handle file modification events"""
            if not event.is_directory:
                self.handle_file_change(event.src_path, 'modified')

        def on_created(self, event: Any) -> None:
            """Handle file creation events"""
            if not event.is_directory:
                self.handle_file_change(event.src_path, 'created')

        def on_deleted(self, event: Any) -> None:
            """Handle file deletion events"""
            if not event.is_directory:
                self.handle_file_change(event.src_path, 'deleted')
else:
    # Fallback when watchdog is not available
    WatchdogFileHandler = FileChangeHandler  # type: ignore


class SystemMonitor:
    """System monitoring and alerting service"""

    def __init__(self, watch_paths: list[str] | None = None, alert_file: str | None = None):
        self.watch_paths = watch_paths or ['.claude/hooks']
        self.alert_file = alert_file
        self.observer: Any | None = None
        self.monitoring_thread: threading.Thread | None = None
        self.event_handler: FileChangeHandler | Any | None = None
        self.file_changes = []
        self.system_stats_history = []
        self.max_history_size = 100
        self.monitoring_interval = 30  # seconds
        self.running = False

        # Initialize alerting system
        self.alerting = AlertingSystem(alert_file)

        # Performance tracking
        self.performance_metrics = {
            'start_time': time.time(),
            'total_events': 0,
            'file_changes': 0,
            'alerts_sent': 0,
            'errors': 0
        }

        # Setup file watching if watchdog is available
        if WATCHDOG_AVAILABLE and Observer:
            self.observer = Observer()
            self.event_handler = WatchdogFileHandler(self)

            # Setup watchers for specified paths
            for watch_path in self.watch_paths:
                if os.path.exists(watch_path):
                    self.observer.schedule(self.event_handler, watch_path, recursive=True)
                    log_to_file(f"👀 Watching: {watch_path}")
                else:
                    log_to_file(f"⚠️ Watch path doesn't exist: {watch_path}")
        else:
            log_to_file("⚠️ Watchdog not available - file monitoring disabled")
            self.event_handler = None

    def record_file_change(self, file_path: str, change_type: str):
        """Record a file system change"""
        change_record = {
            'timestamp': time.time(),
            'file_path': file_path,
            'change_type': change_type,
            'size': self._get_file_size(file_path) if os.path.exists(file_path) else 0
        }

        self.file_changes.append(change_record)
        self.performance_metrics['file_changes'] += 1

        # Keep only recent changes
        if len(self.file_changes) > self.max_history_size:
            self.file_changes = self.file_changes[-self.max_history_size:]

    def _get_file_size(self, file_path: str) -> int:
        """Get file size safely"""
        try:
            return os.path.getsize(file_path)
        except OSError:  # FileNotFoundError is a subclass of OSError
            return 0

    def get_system_stats(self) -> dict[str, Any]:
        """Get current system statistics"""
        try:
            # Get system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Get process stats
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()

            stats = {
                'timestamp': time.time(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3),
                    'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                },
                'process': {
                    'cpu_percent': process_cpu,
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'memory_percent': process.memory_percent(),
                    'num_threads': process.num_threads(),
                    'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
                }
            }

            return stats

        except Exception as e:
            error_stats = {
                'timestamp': time.time(),
                'error': str(e),
                'system': {
                    'cpu_percent': 0,
                    'memory_percent': 0,
                    'memory_available_gb': 0,
                    'disk_percent': 0,
                    'disk_free_gb': 0,
                    'load_average': [0, 0, 0]
                },
                'process': {
                    'cpu_percent': 0,
                    'memory_rss': 0,
                    'memory_vms': 0,
                    'memory_percent': 0,
                    'num_threads': 0,
                    'num_fds': 0
                }
            }

            self.performance_metrics['errors'] += 1
            log_to_file(f"❌ Error getting system stats: {e}")
            return error_stats

    def _monitoring_loop(self):
        """Main monitoring loop that runs in background thread"""
        log_to_file("🔄 System monitoring started")

        while self.running:
            try:
                # Get system stats
                stats = self.get_system_stats()

                # Add to history
                self.system_stats_history.append(stats)
                if len(self.system_stats_history) > self.max_history_size:
                    self.system_stats_history = self.system_stats_history[-self.max_history_size:]

                # Check for alerts
                self.alerting.check_and_alert(stats)

                # Update performance metrics
                self.performance_metrics['total_events'] += 1

                # Log periodic stats (every 10th cycle)
                if self.performance_metrics['total_events'] % 10 == 0:
                    cpu = stats['system']['cpu_percent']
                    memory = stats['system']['memory_percent']
                    disk = stats['system']['disk_percent']
                    log_to_file(f"📊 System: CPU {cpu:.1f}%, Memory {memory:.1f}%, Disk {disk:.1f}%")

                # Sleep until next monitoring cycle
                time.sleep(self.monitoring_interval)

            except Exception as e:
                self.performance_metrics['errors'] += 1
                log_to_file(f"❌ Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)

        log_to_file("⏹️ System monitoring stopped")

    def start(self):
        """Start monitoring services"""
        if self.running:
            log_to_file("⚠️ Monitor already running")
            return

        self.running = True

        # Start file watching
        if WATCHDOG_AVAILABLE and self.observer:
            try:
                self.observer.start()
                log_to_file("👀 File monitoring started")
            except Exception as e:
                log_to_file(f"❌ Failed to start file monitoring: {e}")

        # Start system monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        log_to_file("🚀 System monitor started successfully")

    def stop(self):
        """Stop monitoring services"""
        if not self.running:
            return

        log_to_file("🛑 Stopping system monitor...")
        self.running = False

        # Stop file watching
        if WATCHDOG_AVAILABLE and self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=5)
                log_to_file("👀 File monitoring stopped")
            except Exception as e:
                log_to_file(f"❌ Error stopping file monitoring: {e}")

        # Wait for monitoring thread to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)

        log_to_file("⏹️ System monitor stopped")

    def get_status(self) -> dict[str, Any]:
        """Get current monitoring status"""
        status = {
            'running': self.running,
            'watchdog_available': WATCHDOG_AVAILABLE,
            'watch_paths': self.watch_paths,
            'performance_metrics': self.performance_metrics.copy(),
            'recent_file_changes': len(self.file_changes),
            'system_stats_history_size': len(self.system_stats_history),
            'uptime_seconds': time.time() - self.performance_metrics['start_time']
        }

        # Add latest system stats if available
        if self.system_stats_history:
            status['latest_system_stats'] = self.system_stats_history[-1]

        # Add active alerts
        try:
            status['active_alerts'] = self.alerting.get_active_alerts()
        except Exception as e:
            log_to_file(f"❌ Error getting active alerts: {e}")
            status['active_alerts'] = []

        return status

    def get_recent_file_changes(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent file changes"""
        return self.file_changes[-limit:] if self.file_changes else []

    def get_system_stats_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent system stats history"""
        return self.system_stats_history[-limit:] if self.system_stats_history else []

    def export_data(self, output_file: str | None = None) -> str:
        """Export monitoring data to JSON file"""
        data = {
            'export_timestamp': time.time(),
            'status': self.get_status(),
            'file_changes': self.file_changes,
            'system_stats_history': self.system_stats_history,
            'alert_thresholds': self.alerting.get_thresholds()
        }

        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file_path = LOGS_DIR / f"monitoring_export_{timestamp}.json"
            output_file = str(output_file_path)

        try:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            log_to_file(f"📤 Monitoring data exported to: {output_file}")
            return output_file

        except Exception as e:
            log_to_file(f"❌ Failed to export monitoring data: {e}")
            raise

    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old monitoring data"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)

        # Clean file changes
        original_file_changes = len(self.file_changes)
        self.file_changes = [
            change for change in self.file_changes
            if change['timestamp'] > cutoff_time
        ]

        # Clean system stats history
        original_stats = len(self.system_stats_history)
        self.system_stats_history = [
            stats for stats in self.system_stats_history
            if stats['timestamp'] > cutoff_time
        ]

        # Clean old alerts
        self.alerting.clear_old_alerts(max_age_hours)

        cleaned_changes = original_file_changes - len(self.file_changes)
        cleaned_stats = original_stats - len(self.system_stats_history)

        if cleaned_changes > 0 or cleaned_stats > 0:
            log_to_file(f"🧹 Cleaned up {cleaned_changes} old file changes and {cleaned_stats} old stats")


# Global monitor instance
_monitor_instance = None


def initialize_monitoring():
    """Initialize the monitoring system"""
    # Just return the monitor instance
    return get_monitor()

def get_monitor() -> SystemMonitor:
    """Get or create global monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemMonitor()
    return _monitor_instance


def start_monitoring(watch_paths: list[str] | None = None, alert_file: str | None = None):
    """Start system monitoring"""
    global _monitor_instance
    _monitor_instance = SystemMonitor(watch_paths, alert_file)
    _monitor_instance.start()


def stop_monitoring():
    """Stop system monitoring"""
    global _monitor_instance
    if _monitor_instance:
        _monitor_instance.stop()


def get_monitoring_status() -> dict[str, Any]:
    """Get current monitoring status"""
    monitor = get_monitor()
    return monitor.get_status()


# Utility functions for quick access
def log_system_stats():
    """Log current system statistics"""
    monitor = get_monitor()
    stats = monitor.get_system_stats()

    system = stats['system']
    process = stats['process']

    log_to_file("💻 System Stats:")
    log_to_file(f"   CPU: {system['cpu_percent']:.1f}%")
    log_to_file(f"   Memory: {system['memory_percent']:.1f}% ({system['memory_available_gb']:.1f}GB available)")
    log_to_file(f"   Disk: {system['disk_percent']:.1f}% ({system['disk_free_gb']:.1f}GB free)")
    log_to_file(f"   Process: CPU {process['cpu_percent']:.1f}%, Memory {process['memory_percent']:.1f}%")


def check_system_health() -> dict[str, Any]:
    """Check overall system health"""
    monitor = get_monitor()
    stats = monitor.get_system_stats()
    status = monitor.get_status()

    health = {
        'overall_status': 'healthy',
        'issues': [],
        'warnings': [],
        'metrics': {
            'cpu_usage': stats['system']['cpu_percent'],
            'memory_usage': stats['system']['memory_percent'],
            'disk_usage': stats['system']['disk_percent'],
            'uptime_hours': status['uptime_seconds'] / 3600,
            'total_errors': status['performance_metrics']['errors']
        }
    }

    # Check for issues
    if stats['system']['cpu_percent'] > 90:
        health['issues'].append('High CPU usage detected')
        health['overall_status'] = 'degraded'

    if stats['system']['memory_percent'] > 95:
        health['issues'].append('High memory usage detected')
        health['overall_status'] = 'degraded'

    if stats['system']['disk_percent'] > 95:
        health['issues'].append('Low disk space detected')
        health['overall_status'] = 'critical'

    # Check for warnings
    if stats['system']['cpu_percent'] > 70:
        health['warnings'].append('Elevated CPU usage')

    if stats['system']['memory_percent'] > 80:
        health['warnings'].append('High memory usage')

    if status['performance_metrics']['errors'] > 10:
        health['warnings'].append('Multiple monitoring errors detected')

    return health
