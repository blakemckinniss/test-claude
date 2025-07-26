#!/usr/bin/env python3
"""
Data Science Utils Bridge for User Prompt Processor
This module provides a bridge to the core data science utilities.
"""

import sys
from pathlib import Path

# Add the hooks directory to the path to enable imports
hooks_dir = Path(__file__).parent.parent.parent
if str(hooks_dir) not in sys.path:
    sys.path.insert(0, str(hooks_dir))

# Import all functions from the core data science utils
try:
    from core.utils.data_science_utils import (
        HAS_NUMPY,
        HAS_PANDAS,
        HAS_SKLEARN,
        HAS_TEXTBLOB,
        DataScienceAnalyzer,
        analyze_commands,
        analyze_complexity,
        analyze_sentiment,
        cluster_files,
        get_analyzer,
        predict_category,
    )
    # Mark as available
    HAS_DATA_SCIENCE_UTILS = True
except ImportError:
    # Provide fallback implementations
    HAS_DATA_SCIENCE_UTILS = False
    HAS_PANDAS = False
    HAS_NUMPY = False
    HAS_SKLEARN = False
    HAS_TEXTBLOB = False

    class DataScienceAnalyzer:
        """Fallback analyzer when dependencies are not available"""
        def __init__(self):
            self.available_libs = {
                'pandas': False,
                'numpy': False,
                'sklearn': False,
                'textblob': False
            }

    def get_analyzer():
        """Fallback analyzer getter"""
        return DataScienceAnalyzer()

    def analyze_sentiment(text: str):
        """Fallback sentiment analysis"""
        return {
            'sentiment': 'neutral',
            'polarity': 0.0,
            'subjectivity': 0.5,
            'error': 'Data science libraries not available'
        }

    def analyze_commands(commands: list):
        """Fallback command analysis"""
        return {
            'total_commands': len(commands),
            'unique_commands': len(set(commands)),
            'error': 'Data science libraries not available'
        }

    def cluster_files(file_paths: list, n_clusters: int = 3):
        """Fallback file clustering"""
        return {
            'n_clusters': 1,
            'clusters': {'cluster_0': file_paths},
            'error': 'Data science libraries not available'
        }

    def analyze_complexity(file_stats: list):
        """Fallback complexity analysis"""
        return {
            'total_files': len(file_stats),
            'error': 'Data science libraries not available'
        }

    def predict_category(description: str):
        """Fallback category prediction"""
        # Simple keyword-based fallback
        description_lower = description.lower()
        if any(word in description_lower for word in ['fix', 'bug', 'error']):
            category = 'bug_fix'
        elif any(word in description_lower for word in ['add', 'new', 'feature']):
            category = 'feature'
        elif any(word in description_lower for word in ['test', 'spec']):
            category = 'testing'
        elif any(word in description_lower for word in ['doc', 'readme']):
            category = 'documentation'
        else:
            category = 'general'

        return {
            'predicted_category': category,
            'confidence': 0.5,
            'error': 'Using fallback prediction'
        }

# Export all components
__all__ = [
    'DataScienceAnalyzer',
    'get_analyzer',
    'analyze_sentiment',
    'analyze_commands',
    'cluster_files',
    'analyze_complexity',
    'predict_category',
    'HAS_DATA_SCIENCE_UTILS',
    'HAS_PANDAS',
    'HAS_NUMPY',
    'HAS_SKLEARN',
    'HAS_TEXTBLOB'
]
