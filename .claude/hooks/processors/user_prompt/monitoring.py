#!/usr/bin/env python3
"""
Monitoring module for user prompt processing
"""

import queue
import threading
import time
from typing import Any

import psutil


def log_prompt_event(message: str) -> None:
    """Log user prompt processing event"""
    print(f"[UserPromptProcessor] {message}", flush=True)


class UserPromptMonitor:
    """Specialized monitoring for user prompt processing"""

    def __init__(self):
        self.process = psutil.Process()
        self.monitoring = False
        self.monitor_thread = None
        self.stats_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=50)
        self.prompt_metrics: dict[str, Any] = {
            'total_prompts': 0,
            'processing_times': [],
            'error_count': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self._metrics_lock = threading.RLock()

    def start_monitoring(self, interval=5):
        """Start user prompt monitoring"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        log_prompt_event(f"📊 User prompt monitoring started (interval: {interval}s)")

    def stop_monitoring(self):
        """Stop user prompt monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        log_prompt_event("📊 User prompt monitoring stopped")

    def _monitor_loop(self, interval):
        """Monitoring loop for user prompt processing"""
        while self.monitoring:
            try:
                stats = self._get_current_stats()

                # Add to queue (non-blocking)
                try:
                    self.stats_queue.put_nowait(stats)
                except queue.Full:
                    # Remove oldest item if queue is full
                    try:
                        self.stats_queue.get_nowait()
                        self.stats_queue.put_nowait(stats)
                    except queue.Empty:
                        pass

                # Check for critical resource usage
                self._check_prompt_thresholds(stats)

                time.sleep(interval)
            except Exception as e:
                log_prompt_event(f"❌ User prompt monitoring error: {e}")
                time.sleep(interval)

    def _get_current_stats(self):
        """Get current user prompt processing statistics"""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()

            # System stats
            system_memory = psutil.virtual_memory()

            with self._metrics_lock:
                avg_processing_time = (
                    sum(self.prompt_metrics['processing_times'][-10:]) /
                    len(self.prompt_metrics['processing_times'][-10:])
                    if self.prompt_metrics['processing_times'] else 0
                )

                cache_hit_rate = (
                    self.prompt_metrics['cache_hits'] /
                    (self.prompt_metrics['cache_hits'] + self.prompt_metrics['cache_misses'])
                    if (self.prompt_metrics['cache_hits'] + self.prompt_metrics['cache_misses']) > 0 else 0
                )

            return {
                'timestamp': time.time(),
                'process': {
                    'memory_rss': memory_info.rss,
                    'memory_vms': memory_info.vms,
                    'cpu_percent': cpu_percent
                },
                'system': {
                    'memory_percent': system_memory.percent,
                    'memory_available': system_memory.available
                },
                'prompt_metrics': {
                    'total_prompts': self.prompt_metrics['total_prompts'],
                    'error_count': self.prompt_metrics['error_count'],
                    'avg_processing_time': avg_processing_time,
                    'cache_hit_rate': cache_hit_rate * 100
                }
            }
        except Exception as e:
            log_prompt_event(f"❌ Failed to get user prompt stats: {e}")
            return {'error': str(e), 'timestamp': time.time()}

    def _check_prompt_thresholds(self, stats):
        """Check if user prompt processing exceeds thresholds"""
        if 'error' in stats:
            return

        # Check memory usage (> 100MB for prompt processing)
        process_memory_mb = stats['process']['memory_rss'] / (1024 * 1024)
        if process_memory_mb > 100:
            log_prompt_event(f"⚠️ HIGH PROMPT PROCESS MEMORY: {process_memory_mb:.1f}MB")

        # Check error rate (> 10%)
        if stats['prompt_metrics']['total_prompts'] > 10:
            error_rate = (stats['prompt_metrics']['error_count'] / stats['prompt_metrics']['total_prompts']) * 100
            if error_rate > 10:
                log_prompt_event(f"⚠️ HIGH PROMPT ERROR RATE: {error_rate:.1f}%")

        # Check cache hit rate (< 50%)
        if stats['prompt_metrics']['cache_hit_rate'] < 50 and stats['prompt_metrics']['total_prompts'] > 5:
            log_prompt_event(f"⚠️ LOW CACHE HIT RATE: {stats['prompt_metrics']['cache_hit_rate']:.1f}%")

    def record_prompt_processing(self, processing_time: float, had_error: bool = False, cache_hit: bool = False) -> None:
        """Record metrics for a prompt processing operation"""
        with self._metrics_lock:
            self.prompt_metrics['total_prompts'] += 1
            self.prompt_metrics['processing_times'].append(processing_time)

            # Keep only last 100 processing times
            if len(self.prompt_metrics['processing_times']) > 100:
                self.prompt_metrics['processing_times'] = self.prompt_metrics['processing_times'][-100:]

            if had_error:
                self.prompt_metrics['error_count'] += 1

            if cache_hit:
                self.prompt_metrics['cache_hits'] += 1
            else:
                self.prompt_metrics['cache_misses'] += 1

    def get_metrics_summary(self):
        """Get summary of prompt processing metrics"""
        with self._metrics_lock:
            return {
                'total_prompts': self.prompt_metrics['total_prompts'],
                'error_count': self.prompt_metrics['error_count'],
                'error_rate': (self.prompt_metrics['error_count'] / self.prompt_metrics['total_prompts'] * 100)
                              if self.prompt_metrics['total_prompts'] > 0 else 0,
                'cache_hits': self.prompt_metrics['cache_hits'],
                'cache_misses': self.prompt_metrics['cache_misses'],
                'cache_hit_rate': (self.prompt_metrics['cache_hits'] /
                                  (self.prompt_metrics['cache_hits'] + self.prompt_metrics['cache_misses']) * 100)
                                  if (self.prompt_metrics['cache_hits'] + self.prompt_metrics['cache_misses']) > 0 else 0,
                'avg_processing_time': (sum(self.prompt_metrics['processing_times']) /
                                       len(self.prompt_metrics['processing_times']))
                                       if self.prompt_metrics['processing_times'] else 0,
                'recent_processing_times': self.prompt_metrics['processing_times'][-10:]
            }
