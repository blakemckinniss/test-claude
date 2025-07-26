#!/usr/bin/env python3
"""
Simplified Process Management for Claude Code Hooks
Removes over-engineering and focuses on essential functionality
"""

import asyncio
import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class SimpleProcessManager:
    """Simplified process manager for executing commands"""
    
    def __init__(self):
        self.active_processes: list[subprocess.Popen] = []
    
    def execute_command(self, cmd: str | list[str], timeout: int = 60) -> tuple[int, str, str]:
        """
        Execute a command synchronously
        
        Args:
            cmd: Command to execute (string or list)
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Handle both string and list commands
            if isinstance(cmd, str):
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            self.active_processes.append(process)
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return process.returncode, stdout, stderr
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return -1, stdout, f"Command timed out after {timeout} seconds\n{stderr}"
            finally:
                if process in self.active_processes:
                    self.active_processes.remove(process)
                    
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return -1, "", str(e)
    
    async def execute_command_async(self, cmd: str | list[str], timeout: int = 60) -> tuple[int, str, str]:
        """
        Execute a command asynchronously
        
        Args:
            cmd: Command to execute (string or list)
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Handle both string and list commands
            if isinstance(cmd, str):
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                return process.returncode, stdout.decode(), stderr.decode()
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return -1, "", f"Command timed out after {timeout} seconds"
                
        except Exception as e:
            logger.error(f"Failed to execute async command: {e}")
            return -1, "", str(e)
    
    def cleanup_all(self):
        """Clean up any remaining processes"""
        for process in self.active_processes[:]:
            try:
                if process.poll() is None:
                    process.kill()
            except Exception:
                pass
        self.active_processes.clear()


# Global instance for backward compatibility
_process_manager = SimpleProcessManager()


def execute_command(cmd: str | list[str], timeout: int = 60) -> tuple[int, str, str]:
    """Execute a command synchronously"""
    return _process_manager.execute_command(cmd, timeout)


async def execute_command_async(cmd: str | list[str], timeout: int = 60) -> tuple[int, str, str]:
    """Execute a command asynchronously"""
    return await _process_manager.execute_command_async(cmd, timeout)


def cleanup_processes():
    """Clean up all active processes"""
    _process_manager.cleanup_all()


# Export main components
__all__ = [
    'SimpleProcessManager',
    'execute_command',
    'execute_command_async',
    'cleanup_processes'
]