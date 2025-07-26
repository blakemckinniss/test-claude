#!/usr/bin/env python3
"""
Analysis and detection functions for user prompt processing
"""

import logging
import os
import re
import subprocess
from functools import lru_cache
from typing import Any


# Import cache decorators for enhanced caching
# Define fallback decorators since cache_integration.py was removed
def cached_prompt_operation(ttl=300, key_prefix=""):
    """Fallback decorator - caching now handled by orchestration_cache backend"""
    return lambda func: func

def cached_file_operation(ttl=300):
    """Fallback decorator - caching now handled by orchestration_cache backend"""
    return lambda func: func

# Try importing data science utils
try:
    from data_science_utils import (
        analyze_commands,
        analyze_complexity,
        analyze_sentiment,
        cluster_files,
        get_analyzer,
        predict_category,
    )
    HAS_DATA_SCIENCE_UTILS = True
except ImportError:
    HAS_DATA_SCIENCE_UTILS = False
    get_analyzer = None


@lru_cache(maxsize=128)
def cached_prompt_hash(prompt: str) -> str:
    """Generate a cached hash for the prompt"""
    return str(hash(prompt))


@cached_prompt_operation(ttl=600, key_prefix="expensive_analysis")
def expensive_prompt_analysis(prompt_text: str) -> dict[str, Any]:
    """Perform expensive analysis operations on the prompt - suitable for caching"""
    # This would include ML model predictions, complex regex matching, etc.
    analysis_result = {
        'word_count': len(prompt_text.split()),
        'char_count': len(prompt_text),
        'line_count': len(prompt_text.splitlines()),
        'complexity_score': len(prompt_text) * 0.1,  # Placeholder
        'timestamp': os.environ.get('TIMESTAMP', 'N/A')
    }
    return analysis_result


@cached_prompt_operation(ttl=300, key_prefix="prompt_complexity")
def analyze_prompt_complexity(prompt: str, logger: logging.Logger | None = None) -> dict[str, Any]:
    """
    Analyze the complexity and nature of the user prompt
    Enhanced version with data science integration
    """
    prompt_lower = prompt.lower()

    # 🚨 CRITICAL: Initialize analysis results with HEAVY BIAS towards swarm coordination
    analysis = {
        'complexity': 'high',  # 🚨 DEFAULT TO HIGH - force swarm coordination
        'type': 'general',
        'has_code': bool(re.search(r'```|def |class |function |import |const |let |var ', prompt)),
        'needs_swarm': True,  # 🚨 FORCE TRUE - always recommend swarm
        'needs_consultation': True,  # 🚨 FORCE TRUE - always recommend Task()
        'estimated_tokens': len(prompt.split()) * 1.3,
        'github_references': [],
        'confidence': 0.8,  # 🚨 HIGH CONFIDENCE - make recommendations stronger
        'indicators': ['swarm_forced'],  # 🚨 Add indicator for forced swarm
        'prompt': prompt  # 🚨 ADD PROMPT for workflow determination
    }

    # Enhanced ML-based analysis if available
    if HAS_DATA_SCIENCE_UTILS and get_analyzer:
        try:
            get_analyzer()

            # Sentiment analysis
            sentiment = analyze_sentiment(prompt)
            analysis['sentiment'] = sentiment

            # Command extraction
            commands = analyze_commands(prompt)
            analysis['detected_commands'] = commands

            # Complexity prediction
            complexity_score = analyze_complexity(prompt)
            analysis['ml_complexity_score'] = complexity_score

            # Category prediction
            category = predict_category(prompt)
            analysis['predicted_category'] = category

            # Adjust complexity based on ML predictions
            if isinstance(complexity_score, int | float):
                if complexity_score > 0.7:
                    analysis['complexity'] = 'high'
                elif complexity_score > 0.4:
                    analysis['complexity'] = 'medium'
                else:
                    analysis['complexity'] = 'low'

        except Exception as e:
            if logger:
                logger.warning(f"ML analysis failed: {e}")

    # Keyword-based analysis (fallback and enhancement)

    # Check for complex multi-step tasks
    complex_indicators = [
        'build', 'create', 'implement', 'design', 'architecture',
        'full-stack', 'microservice', 'distributed', 'scale',
        'optimize', 'refactor', 'migrate', 'integrate',
        'and then', 'after that', 'multiple', 'several', 'various'
    ]

    complex_count = sum(1 for indicator in complex_indicators if indicator in prompt_lower)

    # Check for specific technical domains
    technical_indicators = {
        'api': ['api', 'rest', 'graphql', 'endpoint', 'webhook'],
        'database': ['database', 'sql', 'mongodb', 'postgres', 'mysql'],
        'frontend': ['react', 'vue', 'angular', 'frontend', 'ui', 'css'],
        'backend': ['backend', 'server', 'nodejs', 'python', 'java'],
        'devops': ['docker', 'kubernetes', 'ci/cd', 'deploy', 'aws', 'azure'],
        'ai/ml': ['machine learning', 'neural', 'ai', 'model', 'training']
    }

    detected_domains = []
    for domain, keywords in technical_indicators.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_domains.append(domain)
            analysis['indicators'].append(f"technical:{domain}")

    # Check for GitHub references
    github_patterns = [
        r'github\.com/[\w-]+/[\w-]+',
        r'issue\s*#\d+',
        r'pr\s*#\d+',
        r'pull request\s*#\d+',
        r'repository\s+[\w-]+/[\w-]+',
        r'repo\s+[\w-]+/[\w-]+'
    ]

    for pattern in github_patterns:
        matches = re.findall(pattern, prompt_lower)
        if matches:
            analysis['github_references'].extend(matches)
            analysis['indicators'].append('github_reference')

    # Check for research/analysis needs
    research_indicators = [
        'research', 'analyze', 'investigate', 'explore',
        'compare', 'evaluate', 'assess', 'study',
        'find out', 'understand', 'explain', 'how does', 'what is'
    ]

    if any(indicator in prompt_lower for indicator in research_indicators):
        analysis['type'] = 'research'
        analysis['needs_consultation'] = True
        analysis['indicators'].append('research_task')

    # Check for code-heavy tasks
    code_indicators = [
        'implement', 'code', 'function', 'class', 'method',
        'algorithm', 'script', 'program', 'develop'
    ]

    code_count = sum(1 for indicator in code_indicators if indicator in prompt_lower)

    # 🚨 CRITICAL: ALWAYS favor high complexity and swarm coordination
    # Even simple tasks benefit from swarm coordination and Task() approach
    if complex_count >= 1 or len(detected_domains) >= 1 or code_count >= 1 or len(prompt.split()) > 5:
        analysis['complexity'] = 'high'  # 🚨 LOWERED THRESHOLD - most tasks are "high"
        analysis['needs_swarm'] = True
        analysis['needs_consultation'] = True
        analysis['confidence'] = 0.9  # 🚨 VERY HIGH CONFIDENCE
        analysis['indicators'].append('elevated_to_high')
    elif len(prompt.split()) > 3:  # 🚨 EVEN 3+ words = medium complexity
        analysis['complexity'] = 'medium'  
        analysis['needs_swarm'] = True  # 🚨 STILL FORCE SWARM
        analysis['needs_consultation'] = True
        analysis['confidence'] = 0.8
        analysis['indicators'].append('elevated_to_medium')
    else:
        # 🚨 Even "simple" tasks get medium complexity for Task() recommendations
        analysis['complexity'] = 'medium'  # 🚨 NO MORE "LOW" COMPLEXITY
        analysis['needs_swarm'] = True  # 🚨 ALWAYS SWARM
        analysis['needs_consultation'] = True  # 🚨 ALWAYS TASK()
        analysis['confidence'] = 0.7
        analysis['indicators'].append('forced_minimum_medium')

    # Check for specific task types
    if 'test' in prompt_lower or 'debug' in prompt_lower:
        analysis['type'] = 'testing'
        analysis['indicators'].append('testing_task')
    elif 'fix' in prompt_lower or 'bug' in prompt_lower or 'error' in prompt_lower:
        analysis['type'] = 'debugging'
        analysis['indicators'].append('debugging_task')
    elif 'deploy' in prompt_lower or 'release' in prompt_lower:
        analysis['type'] = 'deployment'
        analysis['indicators'].append('deployment_task')
    elif 'document' in prompt_lower or 'readme' in prompt_lower:
        analysis['type'] = 'documentation'
        analysis['indicators'].append('documentation_task')

    # Check for file operations
    if re.search(r'\.(py|js|ts|java|cpp|go|rs|rb)', prompt_lower):
        analysis['has_file_references'] = True
        analysis['indicators'].append('file_reference')

    # 🚨 CRITICAL: Even shorter prompts benefit from swarm coordination
    word_count = len(prompt.split())
    if word_count > 20:  # 🚨 LOWERED from 100 to 20
        analysis['complexity'] = 'high'
        analysis['needs_swarm'] = True  # 🚨 ENSURE SWARM
        analysis['needs_consultation'] = True
        analysis['confidence'] = 0.95  # 🚨 MAXIMUM CONFIDENCE
        analysis['indicators'].append('long_prompt')
    elif word_count > 10:  # 🚨 LOWERED from 50 to 10
        analysis['complexity'] = 'high'  # 🚨 ELEVATED from medium to high
        analysis['needs_swarm'] = True  # 🚨 ENSURE SWARM
        analysis['needs_consultation'] = True
        analysis['indicators'].append('medium_prompt')

    # Add domains to analysis
    analysis['detected_domains'] = detected_domains

    # ML confidence adjustment
    if 'ml_complexity_score' in analysis and isinstance(analysis['ml_complexity_score'], int | float):
        analysis['confidence'] = max(analysis['confidence'], float(analysis['ml_complexity_score']))

    if logger:
        logger.info(f"Prompt analysis complete: {analysis}")

    return analysis


@cached_prompt_operation(ttl=300, key_prefix="zen_workflow")
def determine_zen_workflow(prompt_analysis: dict[str, Any], logger: logging.Logger | None) -> str:
    """
    🚨 CRITICAL: ALWAYS prefer Task() execution with Zen consultation
    Heavily bias towards swarm coordination and parallel execution
    """
    complexity = prompt_analysis.get('complexity', 'unknown')
    task_type = prompt_analysis.get('type', 'general')
    has_code = prompt_analysis.get('has_code', False)
    needs_swarm = prompt_analysis.get('needs_swarm', True)  # 🚨 FORCE TRUE
    needs_consultation = prompt_analysis.get('needs_consultation', True)  # 🚨 FORCE TRUE
    prompt_text = prompt_analysis.get('prompt', '')
    
    # 🚨 CRITICAL: ALWAYS use advanced Zen workflows that recommend Task()
    # Priority: thinkdeep > analyze > debug > testgen > codereview > chat
    
    if complexity in ['high', 'complex', 'unknown'] or needs_swarm or len(prompt_text.split()) > 10:
        workflow = 'thinkdeep'  # 🚨 MOST LIKELY to recommend Task() and swarm coordination
        if logger:
            logger.info("🚨 FORCED 'thinkdeep' workflow - will recommend Task() and swarm coordination")
    elif task_type in ['research', 'analysis', 'planning', 'architecture'] or needs_consultation:
        workflow = 'analyze'  # 🚨 SECOND CHOICE - good for systematic Task() approach
        if logger:
            logger.info("🚨 FORCED 'analyze' workflow - will recommend systematic Task() approach")
    elif task_type == 'debugging' or 'error' in prompt_text.lower():
        workflow = 'debug'  # 🚨 Will recommend investigative Task() workflow
        if logger:
            logger.info("🚨 Selected 'debug' workflow - will recommend investigative Task() approach")
    elif task_type == 'testing' or 'test' in prompt_text.lower():
        workflow = 'testgen'  # 🚨 Will recommend comprehensive Task() test generation
        if logger:
            logger.info("🚨 Selected 'testgen' workflow - will recommend comprehensive Task() approach")
    elif has_code or task_type in ['coding', 'implementation']:
        workflow = 'codereview'  # 🚨 Will recommend thorough Task() code analysis
        if logger:
            logger.info("🚨 Selected 'codereview' workflow - will recommend thorough Task() analysis")
    elif task_type == 'documentation':
        workflow = 'docgen'  # 🚨 Will recommend systematic Task() documentation
        if logger:
            logger.info("🚨 Selected 'docgen' workflow - will recommend systematic Task() approach")
    else:
        # 🚨 EVEN "simple" queries get elevated to analysis for Task() recommendations
        workflow = 'analyze'  # 🚨 CHANGED FROM 'chat' - always prefer analysis
        if logger:
            logger.info("🚨 ELEVATED to 'analyze' workflow - will recommend Task() consultation")
    
    return workflow


@cached_prompt_operation(ttl=300, key_prefix="swarm_detection")
def detect_claude_flow_swarm_needs(prompt: str, logger: logging.Logger | None = None) -> dict[str, Any]:
    """
    🚨 CRITICAL: ALWAYS recommend Claude Flow swarm orchestration
    Every task benefits from swarm coordination and parallel execution
    """
    prompt_lower = prompt.lower()

    # 🚨 CRITICAL: ALWAYS recommend swarm coordination
    analysis = {
        'needs_swarm': True,  # 🚨 FORCE TRUE - every task needs swarm
        'suggested_topology': 'hierarchical',  # 🚨 DEFAULT TO HIERARCHICAL
        'estimated_agents': 6,  # 🚨 DEFAULT TO 6 AGENTS
        'reasoning': ['🚨 FORCED: All tasks benefit from swarm coordination'],
        'confidence': 0.95  # 🚨 MAXIMUM CONFIDENCE
    }

    # 🚨 Enhanced analysis to determine optimal agent count and topology
    word_count = len(prompt.split())
    
    # Determine agent count based on prompt complexity
    if word_count > 50 or len(prompt) > 300:
        analysis['estimated_agents'] = 8
        analysis['suggested_topology'] = 'mesh'
        analysis['reasoning'].append('🚨 Large prompt - mesh topology with 8 agents')
    elif word_count > 25 or len(prompt) > 150:
        analysis['estimated_agents'] = 6
        analysis['suggested_topology'] = 'hierarchical'
        analysis['reasoning'].append('🚨 Medium prompt - hierarchical with 6 agents')
    else:
        analysis['estimated_agents'] = 4
        analysis['suggested_topology'] = 'star'
        analysis['reasoning'].append('🚨 Standard prompt - star topology with 4 agents')

    # 🚨 ALWAYS recommend swarm for any technical keywords
    technical_keywords = [
        'api', 'database', 'frontend', 'backend', 'code', 'implement',
        'build', 'create', 'design', 'fix', 'debug', 'test', 'analyze',
        'optimize', 'deploy', 'configure', 'setup', 'install', 'review'
    ]
    
    found_technical = [word for word in technical_keywords if word in prompt_lower]
    if found_technical:
        analysis['estimated_agents'] = min(8, analysis['estimated_agents'] + len(found_technical))
        analysis['reasoning'].append(f'🚨 Technical keywords found: {found_technical} - increased agents')
        analysis['confidence'] = 0.99

    # 🚨 Special cases for maximum coordination
    if any(keyword in prompt_lower for keyword in ['swarm', 'parallel', 'coordinate', 'orchestrate']):
        analysis['estimated_agents'] = 8
        analysis['suggested_topology'] = 'mesh'
        analysis['reasoning'].append('🚨 Explicit coordination request - maximum agents')

    if logger:
        logger.info(f"🚨 FORCED Claude Flow swarm analysis: {analysis}")

    return analysis


@cached_prompt_operation(ttl=300, key_prefix="serena_detection")
def detect_serena_code_analysis_needs(prompt: str, logger: logging.Logger | None = None) -> dict[str, Any]:
    """
    Detect if the prompt needs Serena code analysis tools
    """
    prompt_lower = prompt.lower()

    analysis = {
        'needs_serena': False,
        'suggested_tools': [],
        'confidence': 0.0,
        'reasoning': []
    }

    # Serena-specific indicators
    serena_indicators = {
        'symbol_search': ['find class', 'find function', 'find method', 'where is', 'locate'],
        'code_analysis': ['analyze code', 'understand codebase', 'code structure', 'dependencies'],
        'refactoring': ['refactor', 'rename', 'move', 'extract method', 'improve code'],
        'navigation': ['go to definition', 'find usages', 'references', 'call hierarchy']
    }

    for category, keywords in serena_indicators.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                analysis['needs_serena'] = True
                analysis['suggested_tools'].append(category)
                analysis['reasoning'].append(f"Found '{keyword}' indicating {category}")
                analysis['confidence'] = min(0.9, analysis['confidence'] + 0.2)

    if logger and analysis['needs_serena']:
        logger.info(f"Serena code analysis needed: {analysis}")

    return analysis


def detect_smart_mcp_triggers(prompt: str) -> dict[str, Any]:
    """
    Smart detection of MCP tool usage based on prompt analysis
    """
    prompt_lower = prompt.lower()

    triggers = {
        'github_mcp': False,
        'playwright_mcp': False,
        'filesystem_mcp': False,
        'tavily_mcp': False,
        'ruv_swarm_mcp': False,
        'magicui_mcp': False,
        'code_search_mcp': False,
        'context7_mcp': False,
        'indicators': []
    }

    # GitHub MCP triggers
    github_patterns = [
        r'github\.com',
        r'(issue|pr|pull request)\s*#?\d+',
        r'(create|open|close|merge)\s+(issue|pr|pull request)',
        r'(repository|repo)\s+\w+/\w+',
        r'github\s+(action|workflow|notification)'
    ]

    for pattern in github_patterns:
        if re.search(pattern, prompt_lower):
            triggers['github_mcp'] = True
            triggers['indicators'].append(f'github: {pattern}')
            break

    # Playwright MCP triggers
    browser_keywords = [
        'browser', 'web page', 'screenshot', 'navigate', 'click',
        'automation', 'scrape', 'test ui', 'web test', 'playwright'
    ]

    if any(keyword in prompt_lower for keyword in browser_keywords):
        triggers['playwright_mcp'] = True
        triggers['indicators'].append('browser_automation')

    # Filesystem MCP triggers
    file_patterns = [
        r'(read|write|create|delete|edit)\s+file',
        r'file\s+system',
        r'directory',
        r'folder',
        r'\.txt|\.py|\.js|\.json|\.md'
    ]

    for pattern in file_patterns:
        if re.search(pattern, prompt_lower):
            triggers['filesystem_mcp'] = True
            triggers['indicators'].append(f'filesystem: {pattern}')
            break

    # Tavily MCP triggers (web search)
    search_keywords = [
        'search web', 'google', 'find information', 'research online',
        'latest news', 'current', 'up to date', 'recent'
    ]

    if any(keyword in prompt_lower for keyword in search_keywords):
        triggers['tavily_mcp'] = True
        triggers['indicators'].append('web_search')

    # Ruv Swarm MCP triggers
    swarm_keywords = [
        'swarm', 'parallel agents', 'concurrent', 'distributed task',
        'multi-agent', 'orchestrate agents'
    ]

    if any(keyword in prompt_lower for keyword in swarm_keywords):
        triggers['ruv_swarm_mcp'] = True
        triggers['indicators'].append('swarm_orchestration')

    # Magic UI MCP triggers
    ui_keywords = [
        'magic ui', 'ui component', 'shadcn', 'component library',
        'button component', 'animation component', 'react component'
    ]

    if any(keyword in prompt_lower for keyword in ui_keywords):
        triggers['magicui_mcp'] = True
        triggers['indicators'].append('ui_components')

    # Code search MCP triggers
    if 'search code' in prompt_lower or 'find snippet' in prompt_lower:
        triggers['code_search_mcp'] = True
        triggers['indicators'].append('code_search')

    # Context7 MCP triggers (documentation)
    doc_keywords = [
        'documentation for', 'docs for', 'api reference',
        'library docs', 'framework docs', 'how to use'
    ]

    if any(keyword in prompt_lower for keyword in doc_keywords):
        triggers['context7_mcp'] = True
        triggers['indicators'].append('documentation_lookup')

    return triggers


def detect_library_documentation_needs(prompt: str) -> dict[str, Any]:
    """
    Detect if user is asking about library/framework documentation
    """
    # Common library patterns
    library_patterns = [
        r'(how to use|documentation for|docs for|api for)\s+(\w+)',
        r'(\w+)\s+(library|framework|package|module)',
        r'(react|vue|angular|django|flask|express|fastapi|numpy|pandas|tensorflow|pytorch)',
    ]

    for pattern in library_patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            return {
                'needs_docs': True,
                'library_hint': match.group(0),
                'confidence': 0.8
            }

    return {'needs_docs': False, 'confidence': 0.0}


def detect_github_repository_context_prompt(logger=None) -> dict[str, Any]:
    """
    Detect if we're in a GitHub repository context
    """
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and 'github.com' in result.stdout:
            # Extract owner and repo from URL
            url = result.stdout.strip()
            match = re.search(r'github\.com[/:]([^/]+)/([^/\s]+?)(?:\.git)?$', url)

            if match:
                owner, repo = match.groups()

                # Get current branch
                branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'main'

                return {
                    'is_github_repo': True,
                    'owner': owner,
                    'repo': repo,
                    'branch': branch,
                    'remote_url': url
                }

    except Exception as e:
        if logger:
            logger.debug(f"Git context detection failed: {e}")

    return {'is_github_repo': False}


def detect_github_claude_flow_needs(prompt: str, github_context: dict[str, Any], logger: logging.Logger | None = None) -> dict[str, Any]:
    """
    Detect if GitHub operations need Claude Flow orchestration
    """
    prompt_lower = prompt.lower()

    analysis = {
        'needs_github_flow': False,
        'suggested_operations': [],
        'confidence': 0.0,
        'reasoning': []
    }

    # GitHub Flow indicators
    github_flow_patterns = {
        'repo_management': ['manage repo', 'repository maintenance', 'clean up repo'],
        'pr_workflow': ['review all', 'merge multiple', 'process prs', 'handle pull requests'],
        'issue_triage': ['triage issues', 'organize issues', 'label issues', 'process issues'],
        'release_flow': ['create release', 'deploy', 'tag release', 'publish version'],
        'multi_repo': ['across repos', 'multiple repositories', 'sync repos']
    }

    for category, patterns in github_flow_patterns.items():
        for pattern in patterns:
            if pattern in prompt_lower:
                analysis['needs_github_flow'] = True
                analysis['suggested_operations'].append(category)
                analysis['reasoning'].append(f"Found '{pattern}' indicating {category}")
                analysis['confidence'] = min(0.9, analysis['confidence'] + 0.25)

    # If we're in a GitHub repo context, lower the threshold
    if github_context.get('is_github_repo') and any(word in prompt_lower for word in ['automate', 'manage', 'process']):
        analysis['needs_github_flow'] = True
        analysis['confidence'] = max(analysis['confidence'], 0.6)
        analysis['reasoning'].append("GitHub repo context with automation keywords")

    if logger and analysis['needs_github_flow']:
        logger.info(f"GitHub Claude Flow analysis: {analysis}")

    return analysis
