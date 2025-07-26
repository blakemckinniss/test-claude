#!/usr/bin/env python3
"""
MCP tool integration functions for user prompt processing
"""

import builtins
import contextlib
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any


# Import cache decorators for enhanced caching
# Define fallback decorators since cache_integration.py was removed
def cached_prompt_operation(ttl=300, key_prefix=""):
    """Fallback decorator - caching now handled by orchestration_cache backend"""
    return lambda func: func

def cached_file_operation(ttl=300):
    """Fallback decorator - caching now handled by orchestration_cache backend"""
    return lambda func: func

# Constants
COMMAND_TIMEOUT_SECONDS = 60
CODE2PROMPT_TIMEOUT_SECONDS = 30
PROJECT_CONTEXT_LIMIT = 10000


@cached_prompt_operation(ttl=3600, key_prefix="mcp_tools")  # Cache for 1 hour
def get_available_mcp_tools():
    """
    Retrieve available MCP tools from the environment or configuration
    """
    # Try to load from mcp_tools.json file
    hooks_dir = Path(__file__).parent.parent
    mcp_tools_file = hooks_dir / 'mcp_tools.json'

    if mcp_tools_file.exists():
        try:
            with open(mcp_tools_file) as f:
                mcp_tools_raw = json.load(f)

            # Parse the flat structure into a categorized structure
            mcp_tools: dict[str, Any] = {}
            for tool_name, _description in mcp_tools_raw.items():
                # Parse tool name format: mcp__<server>__<tool>
                parts = tool_name.split('__')
                if len(parts) == 3 and parts[0] == 'mcp':
                    server = parts[1]
                    tool = parts[2]
                    if server not in mcp_tools:
                        mcp_tools[server] = []
                    mcp_tools[server].append(tool)

            logging.getLogger(__name__).debug(f"Loaded {len(mcp_tools_raw)} MCP tools from mcp_tools.json")
            return mcp_tools
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to load mcp_tools.json: {e}")

    # Fallback to static list if file not found or error
    return {
        'claude-flow': ['swarm_init', 'agent_spawn', 'task_orchestrate', 'memory_usage'],
        'serena': ['find_symbol', 'read_file', 'replace_symbol', 'search_pattern'],
        'github': ['list_issues', 'create_pr', 'get_pr', 'merge_pr'],
        'context7': ['resolve-library-id', 'get-library-docs'],
        'tavily': ['tavily_search', 'tavily_extract'],
        'zen': ['chat', 'thinkdeep', 'debug', 'analyze']
    }


def run_claude_flow_mcp_command(tool: str, params: dict[str, Any] | None = None, logger: logging.Logger | None = None, process_manager: Any = None) -> tuple[int, str, str]:
    """
    Generate instructions for Claude Flow MCP tool (no execution)
    """
    if logger:
        logger.info(f"Generating instructions for Claude Flow MCP tool: {tool}")

    # Generate instruction text instead of executing
    instruction = f"""
Use the following MCP tool:
- Tool: `mcp__claude-flow__{tool}`
- Parameters: {json.dumps(params, indent=2) if params else "{}"}
"""

    # Return success with instructions
    return 0, instruction, ""


def run_serena_mcp_command(tool: str, params: dict[str, Any] | None = None, logger: logging.Logger | None = None, process_manager: Any = None) -> tuple[int, str, str]:
    """
    Generate instructions for Serena MCP tool (no execution)
    """
    if logger:
        logger.info(f"Generating instructions for Serena MCP tool: {tool}")

    # Generate instruction text
    instruction = f"""
Use the following MCP tool:
- Tool: `mcp__serena__{tool}`
- Parameters: {json.dumps(params, indent=2) if params else "{}"}
"""

    # Return success with instructions
    return 0, instruction, ""


@cached_prompt_operation(ttl=1800, key_prefix="serena_context")  # Cache for 30 minutes
def generate_serena_project_context(logger: logging.Logger | None = None, process_manager: Any = None) -> dict[str, Any]:
    """
    Generate instructions for project context analysis (no execution)
    """
    context = {
        'instructions': """
### 📊 Project Context Analysis

To understand the project structure, use the following Serena MCP tools:

1. **Get Project Overview**:
   ```
   Tool: mcp__serena__get_symbols_overview
   Parameters: {"relative_path": "."}
   ```

2. **List Project Directory**:
   ```
   Tool: mcp__serena__list_dir
   Parameters: {"relative_path": ".", "recursive": false}
   ```

3. **Find Key Files**:
   ```
   Tool: mcp__serena__find_file
   Parameters: {"file_mask": "package.json", "relative_path": "."}
   Tool: mcp__serena__find_file
   Parameters: {"file_mask": "requirements.txt", "relative_path": "."}
   ```

This will help identify:
- Main programming languages
- Frameworks in use
- Project structure
- Key configuration files
""",
        'suggested_analysis': True
    }
    
    return context


@cached_prompt_operation(ttl=900, key_prefix="code2prompt")  # Cache for 15 minutes
def generate_code2prompt_context():
    """
    Generate instructions for using code2prompt (no execution)
    """
    # Return instructions instead of executing
    return {
        'source': 'code2prompt_instructions',
        'content': """
To generate project context, you can use:

```bash
code2prompt . --tokens 5000 --no-codeblock
```

This will provide a comprehensive overview of the codebase structure and content.
""",
        'truncated': False
    }


def run_context7_documentation_lookup(prompt: str, library_analysis: dict[str, Any], logger: logging.Logger | None = None, process_manager: Any = None) -> dict[str, Any] | None:
    """
    Generate instructions for Context7 documentation lookup (no execution)
    """
    if logger:
        logger.info("Generating Context7 documentation lookup instructions")

    library_hint = library_analysis.get('library_hint', '')

    if not library_hint:
        return None

    instructions = f"""### 📚 Library Documentation Lookup

**Library**: {library_hint}

1. **Resolve Library ID**:
   ```
   Tool: mcp__context7__resolve-library-id
   Parameters: {{
     "libraryName": "{library_hint}"
   }}
   ```

2. **Get Documentation** (after resolving ID):
   ```
   Tool: mcp__context7__get-library-docs
   Parameters: {{
     "context7CompatibleLibraryID": "[resolved_library_id]",
     "tokens": 5000,
     "topic": "{prompt[:100]}..."
   }}
   ```

This will provide up-to-date documentation for the requested library.
"""

    return {
        'source': 'context7_instructions',
        'library': library_hint,
        'documentation': instructions
    }


def run_mcp_tool_command(server: str, tool: str, params: dict[str, Any] | None, logger: logging.Logger | None = None, process_manager: Any = None) -> tuple[int, str, str]:
    """
    Generic MCP tool instruction generator (no execution)
    """
    if server == 'claude-flow':
        return run_claude_flow_mcp_command(tool, params, logger, process_manager)
    elif server == 'serena':
        return run_serena_mcp_command(tool, params, logger, process_manager)
    else:
        # Generic MCP tool instruction
        if logger:
            logger.info(f"Generating instructions for MCP tool: {server}.{tool}")

        instruction = f"""
Use the following MCP tool:
- Tool: `mcp__{server}__{tool}`
- Parameters: {json.dumps(params, indent=2) if params else "{}"}
"""

        # Return success with instructions
        return 0, instruction, ""
