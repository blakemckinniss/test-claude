#!/usr/bin/env python3
"""
Standalone utility for detecting and cleaning up zombie processes
Can be run manually or scheduled to clean up stuck processes
"""

import argparse
import logging
import os
import signal
import sys
import time
from datetime import datetime
from typing import Any

import psutil


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def get_process_info(proc: psutil.Process) -> dict[str, Any]:
    """Get detailed information about a process"""
    try:
        return {
            'pid': proc.pid,
            'name': proc.name(),
            'cmdline': ' '.join(proc.cmdline() or []),
            'status': proc.status(),
            'create_time': datetime.fromtimestamp(proc.create_time()),
            'cpu_percent': proc.cpu_percent(interval=0.1),
            'memory_info': proc.memory_info()._asdict(),
            'ppid': proc.ppid()
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def find_zombie_processes(pattern: str = None) -> list[dict[str, Any]]:
    """Find zombie processes, optionally filtering by pattern"""
    zombies = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
        try:
            # Check if it's a zombie
            if proc.info.get('status') == psutil.STATUS_ZOMBIE:
                info = get_process_info(proc)
                if info and (not pattern or pattern in info['cmdline']):
                    zombies.append(info)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return zombies

def find_long_running_processes(pattern: str, max_age_minutes: int = 5) -> list[dict[str, Any]]:
    """Find processes that have been running longer than max_age_minutes"""
    long_running = []
    current_time = time.time()
    max_age_seconds = max_age_minutes * 60

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any(pattern in str(arg) for arg in cmdline):
                create_time = proc.info.get('create_time', 0)
                if current_time - create_time > max_age_seconds:
                    info = get_process_info(proc)
                    if info:
                        info['age_minutes'] = (current_time - create_time) / 60
                        long_running.append(info)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return long_running

def kill_process_tree(pid: int, logger: logging.Logger) -> bool:
    """Kill a process and all its children"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        # Kill children first
        for child in children:
            try:
                logger.debug(f"Terminating child process {child.pid}")
                child.terminate()
            except psutil.NoSuchProcess:
                pass

        # Give them time to terminate gracefully
        gone, alive = psutil.wait_procs(children, timeout=3)

        # Force kill any remaining
        for p in alive:
            try:
                logger.debug(f"Force killing child process {p.pid}")
                p.kill()
            except psutil.NoSuchProcess:
                pass

        # Finally kill the parent
        try:
            logger.debug(f"Terminating parent process {pid}")
            parent.terminate()
            parent.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            try:
                logger.debug(f"Force killing parent process {pid}")
                parent.kill()
            except psutil.NoSuchProcess:
                pass

        logger.info(f"Successfully killed process tree for PID {pid}")
        return True

    except Exception as e:
        logger.error(f"Error killing process tree for PID {pid}: {e}")
        return False

def cleanup_claude_flow_processes(dry_run: bool = False, max_age_minutes: int = 5) -> dict[str, int]:
    """Clean up claude-flow related zombie and long-running processes"""
    logger = logging.getLogger(__name__)
    results = {
        'zombies_killed': 0,
        'long_running_killed': 0,
        'errors': 0
    }

    # Find zombie processes
    logger.info("Searching for zombie processes...")
    zombies = find_zombie_processes('claude-flow')

    if zombies:
        logger.info(f"Found {len(zombies)} zombie processes")
        for zombie in zombies:
            logger.info(f"Zombie: PID={zombie['pid']}, CMD={zombie['cmdline']}")
            if not dry_run:
                try:
                    os.kill(zombie['pid'], signal.SIGKILL)
                    results['zombies_killed'] += 1
                except Exception as e:
                    logger.error(f"Failed to kill zombie PID {zombie['pid']}: {e}")
                    results['errors'] += 1
    else:
        logger.info("No zombie processes found")

    # Find long-running processes
    logger.info(f"Searching for processes older than {max_age_minutes} minutes...")
    long_running = find_long_running_processes('claude-flow', max_age_minutes)

    if long_running:
        logger.info(f"Found {len(long_running)} long-running processes")
        for proc in long_running:
            logger.info(f"Long-running: PID={proc['pid']}, Age={proc['age_minutes']:.1f}min, CMD={proc['cmdline']}")
            if not dry_run:
                if kill_process_tree(proc['pid'], logger):
                    results['long_running_killed'] += 1
                else:
                    results['errors'] += 1
    else:
        logger.info("No long-running processes found")

    return results

def monitor_processes(pattern: str = 'claude-flow', interval: int = 60, max_age_minutes: int = 5):
    """Continuously monitor and clean up processes"""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting process monitor for pattern '{pattern}'")
    logger.info(f"Check interval: {interval} seconds, Max age: {max_age_minutes} minutes")

    try:
        while True:
            logger.info("=" * 60)
            logger.info("Running cleanup cycle...")

            results = cleanup_claude_flow_processes(dry_run=False, max_age_minutes=max_age_minutes)

            logger.info(f"Cleanup results: {results}")
            logger.info(f"Next check in {interval} seconds...")

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
        sys.exit(0)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Detect and clean up zombie and long-running processes'
    )

    parser.add_argument(
        '--pattern',
        default='claude-flow',
        help='Process pattern to search for (default: claude-flow)'
    )

    parser.add_argument(
        '--max-age',
        type=int,
        default=5,
        help='Maximum age in minutes for long-running processes (default: 5)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be killed without actually killing'
    )

    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Continuously monitor and clean up processes'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Monitor check interval in seconds (default: 60)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--list-all',
        action='store_true',
        help='List all processes matching the pattern'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.verbose)

    if args.list_all:
        # List all matching processes
        logger.info(f"Listing all processes matching '{args.pattern}'...")
        all_procs = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any(args.pattern in str(arg) for arg in cmdline):
                    info = get_process_info(proc)
                    if info:
                        age = (time.time() - proc.info['create_time']) / 60
                        info['age_minutes'] = age
                        all_procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if all_procs:
            logger.info(f"Found {len(all_procs)} processes:")
            for proc in sorted(all_procs, key=lambda x: x['create_time']):
                logger.info(f"  PID={proc['pid']}, Age={proc['age_minutes']:.1f}min, "
                           f"Status={proc['status']}, CMD={proc['cmdline']}")
        else:
            logger.info("No matching processes found")

    elif args.monitor:
        # Start continuous monitoring
        monitor_processes(
            pattern=args.pattern,
            interval=args.interval,
            max_age_minutes=args.max_age
        )
    else:
        # Run single cleanup
        logger.info(f"Cleaning up '{args.pattern}' processes...")
        results = cleanup_claude_flow_processes(
            dry_run=args.dry_run,
            max_age_minutes=args.max_age
        )

        logger.info("=" * 60)
        logger.info("Cleanup Summary:")
        logger.info(f"  Zombies killed: {results['zombies_killed']}")
        logger.info(f"  Long-running killed: {results['long_running_killed']}")
        logger.info(f"  Errors: {results['errors']}")

        if args.dry_run:
            logger.info("(DRY RUN - no processes were actually killed)")

if __name__ == "__main__":
    main()
