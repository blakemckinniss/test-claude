"""
Configuration files for Claude Code hooks
"""

import json
from pathlib import Path

# Path to MCP tools configuration
MCP_TOOLS_CONFIG_PATH = Path(__file__).parent / "mcp_tools.json"

def load_mcp_tools_config():
    """Load MCP tools configuration"""
    try:
        with open(MCP_TOOLS_CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}

__all__ = ['MCP_TOOLS_CONFIG_PATH', 'load_mcp_tools_config']
