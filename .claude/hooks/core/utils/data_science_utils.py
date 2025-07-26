#!/usr/bin/env python3
"""
Data Science Utility Functions for Claude Hooks
Provides utility functions using pandas, numpy, scikit-learn, and textblob
"""

import logging
from typing import Any

# Data science imports with graceful fallback
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import sklearn
    from sklearn import metrics, model_selection, preprocessing
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LinearRegression, LogisticRegression
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    sklearn = None

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    TextBlob = None

# Setup logging
logger = logging.getLogger(__name__)


class DataScienceAnalyzer:
    """Utility class for data science operations in Claude hooks"""

    def __init__(self):
        self.available_libs = {
            'pandas': HAS_PANDAS,
            'numpy': HAS_NUMPY,
            'sklearn': HAS_SKLEARN,
            'textblob': HAS_TEXTBLOB
        }
        logger.info(f"DataScienceAnalyzer initialized with libs: {self.available_libs}")

    def analyze_prompt_sentiment(self, prompt: str) -> dict[str, Any]:
        """
        Analyze the sentiment of a user prompt using TextBlob

        Args:
            prompt: The user prompt text

        Returns:
            Dict containing sentiment analysis results
        """
        if not HAS_TEXTBLOB:
            return {
                'error': 'TextBlob not available',
                'sentiment': None,
                'polarity': 0.0,
                'subjectivity': 0.0
            }

        try:
            blob = TextBlob(prompt)
            sentiment = blob.sentiment

            # Classify sentiment
            if sentiment.polarity > 0.1:
                sentiment_class = 'positive'
            elif sentiment.polarity < -0.1:
                sentiment_class = 'negative'
            else:
                sentiment_class = 'neutral'

            return {
                'sentiment': sentiment_class,
                'polarity': sentiment.polarity,
                'subjectivity': sentiment.subjectivity,
                'noun_phrases': list(blob.noun_phrases)
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                'error': str(e),
                'sentiment': None,
                'polarity': 0.0,
                'subjectivity': 0.0
            }

    def analyze_command_patterns(self, commands: list[str]) -> dict[str, Any]:
        """
        Analyze patterns in bash commands using pandas and numpy

        Args:
            commands: List of bash command strings

        Returns:
            Dict containing command pattern analysis
        """
        if not HAS_PANDAS or not HAS_NUMPY:
            return {'error': 'pandas or numpy not available'}

        try:
            # Create DataFrame from commands
            df = pd.DataFrame({'command': commands})

            # Extract command names
            df['cmd_name'] = df['command'].str.split().str[0]

            # Command frequency analysis
            cmd_freq = df['cmd_name'].value_counts().to_dict()

            # Command length statistics
            df['cmd_length'] = df['command'].str.len()
            length_stats = {
                'mean_length': float(df['cmd_length'].mean()),
                'std_length': float(df['cmd_length'].std()),
                'max_length': int(df['cmd_length'].max()),
                'min_length': int(df['cmd_length'].min())
            }

            # Identify potentially dangerous commands
            dangerous_patterns = ['rm -rf', 'dd if=', 'chmod 777', '> /dev/']
            dangerous_cmds = []
            for idx, cmd in enumerate(commands):
                for pattern in dangerous_patterns:
                    if pattern in cmd:
                        dangerous_cmds.append({'index': idx, 'command': cmd, 'pattern': pattern})

            return {
                'total_commands': len(commands),
                'unique_commands': len(df['cmd_name'].unique()),
                'command_frequency': cmd_freq,
                'length_statistics': length_stats,
                'potentially_dangerous': dangerous_cmds
            }
        except Exception as e:
            logger.error(f"Error in command pattern analysis: {e}")
            return {'error': str(e)}

    def cluster_similar_files(self, file_paths: list[str], n_clusters: int = 3) -> dict[str, Any]:
        """
        Cluster files based on their path similarity using sklearn

        Args:
            file_paths: List of file paths
            n_clusters: Number of clusters to create

        Returns:
            Dict containing clustering results
        """
        if not HAS_SKLEARN or not HAS_NUMPY:
            return {'error': 'sklearn or numpy not available'}

        if len(file_paths) < n_clusters:
            return {'error': f'Not enough files ({len(file_paths)}) for {n_clusters} clusters'}

        try:
            # Vectorize file paths
            vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
            X = vectorizer.fit_transform(file_paths)

            # Perform clustering
            kmeans = KMeans(n_clusters=min(n_clusters, len(file_paths)), random_state=42)
            clusters = kmeans.fit_predict(X)

            # Group files by cluster
            clustered_files = {}
            for idx, cluster_id in enumerate(clusters):
                cluster_key = f'cluster_{cluster_id}'
                if cluster_key not in clustered_files:
                    clustered_files[cluster_key] = []
                clustered_files[cluster_key].append(file_paths[idx])

            return {
                'n_clusters': len(clustered_files),
                'clusters': clustered_files,
                'cluster_sizes': {k: len(v) for k, v in clustered_files.items()}
            }
        except Exception as e:
            logger.error(f"Error in file clustering: {e}")
            return {'error': str(e)}

    def analyze_code_complexity(self, file_stats: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Analyze code complexity metrics using pandas

        Args:
            file_stats: List of dicts containing file statistics
                       (e.g., {'path': str, 'lines': int, 'functions': int})

        Returns:
            Dict containing complexity analysis
        """
        if not HAS_PANDAS or not HAS_NUMPY:
            return {'error': 'pandas or numpy not available'}

        try:
            df = pd.DataFrame(file_stats)

            # Basic statistics
            stats = {
                'total_files': len(df),
                'total_lines': int(df['lines'].sum()) if 'lines' in df else 0,
                'avg_lines_per_file': float(df['lines'].mean()) if 'lines' in df else 0,
                'std_lines_per_file': float(df['lines'].std()) if 'lines' in df else 0
            }

            # Identify complex files (outliers)
            if 'lines' in df and len(df) > 0:
                threshold = df['lines'].mean() + 2 * df['lines'].std()
                complex_files = df[df['lines'] > threshold]['path'].tolist()
                stats['complex_files'] = complex_files
                stats['complexity_threshold'] = float(threshold)

            # File type distribution if extension info available
            if 'path' in df:
                df['extension'] = df['path'].str.extract(r'\.([^.]+)$')
                ext_dist = df['extension'].value_counts().to_dict()
                stats['file_type_distribution'] = ext_dist

            return stats
        except Exception as e:
            logger.error(f"Error in complexity analysis: {e}")
            return {'error': str(e)}

    def predict_task_category(self, task_description: str) -> dict[str, Any]:
        """
        Predict task category based on description using simple ML

        Args:
            task_description: Description of the task

        Returns:
            Dict containing predicted category and confidence
        """
        if not HAS_SKLEARN or not HAS_TEXTBLOB:
            return {'error': 'sklearn or textblob not available'}

        try:
            # Define simple keyword-based categories
            categories = {
                'refactoring': ['refactor', 'clean', 'optimize', 'improve', 'restructure'],
                'bug_fix': ['fix', 'bug', 'error', 'issue', 'problem', 'crash'],
                'feature': ['add', 'new', 'implement', 'create', 'feature', 'functionality'],
                'testing': ['test', 'unit', 'integration', 'coverage', 'spec'],
                'documentation': ['document', 'docs', 'readme', 'comment', 'explain'],
                'analysis': ['analyze', 'investigate', 'understand', 'explore', 'review']
            }

            # Score each category
            task_lower = task_description.lower()
            scores = {}

            for category, keywords in categories.items():
                score = sum(1 for keyword in keywords if keyword in task_lower)
                scores[category] = score

            # Get top category
            if max(scores.values()) > 0:
                predicted_category = max(scores, key=scores.get)
                confidence = scores[predicted_category] / len(categories[predicted_category])
            else:
                predicted_category = 'general'
                confidence = 0.0

            # Use TextBlob for additional insights
            blob = TextBlob(task_description)

            return {
                'predicted_category': predicted_category,
                'confidence': confidence,
                'category_scores': scores,
                'key_phrases': list(blob.noun_phrases)[:5],
                'word_count': len(blob.words)
            }
        except Exception as e:
            logger.error(f"Error in task category prediction: {e}")
            return {'error': str(e)}


# Singleton instance
_analyzer = None

def get_analyzer() -> DataScienceAnalyzer:
    """Get or create the singleton DataScienceAnalyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = DataScienceAnalyzer()
    return _analyzer


# Convenience functions
def analyze_sentiment(text: str) -> dict[str, Any]:
    """Analyze sentiment of text"""
    return get_analyzer().analyze_prompt_sentiment(text)


def analyze_commands(commands: list[str]) -> dict[str, Any]:
    """Analyze command patterns"""
    return get_analyzer().analyze_command_patterns(commands)


def cluster_files(file_paths: list[str], n_clusters: int = 3) -> dict[str, Any]:
    """Cluster similar files"""
    return get_analyzer().cluster_similar_files(file_paths, n_clusters)


def analyze_complexity(file_stats: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze code complexity"""
    return get_analyzer().analyze_code_complexity(file_stats)


def predict_category(description: str) -> dict[str, Any]:
    """Predict task category"""
    return get_analyzer().predict_task_category(description)


if __name__ == "__main__":
    # Test the utilities
    analyzer = get_analyzer()

    # Test sentiment analysis
    test_prompt = "Please help me fix this terrible bug that's causing crashes!"
    print("Sentiment analysis:", analyzer.analyze_prompt_sentiment(test_prompt))

    # Test command analysis
    test_commands = ["git status", "git add .", "git commit -m 'test'", "rm -rf /tmp/test"]
    print("\nCommand analysis:", analyzer.analyze_command_patterns(test_commands))

    # Test file clustering
    test_files = ["src/main.py", "src/utils.py", "tests/test_main.py", "docs/readme.md"]
    print("\nFile clustering:", analyzer.cluster_similar_files(test_files, 2))

    # Test task prediction
    test_task = "Add new authentication feature with JWT tokens"
    print("\nTask prediction:", analyzer.predict_task_category(test_task))
