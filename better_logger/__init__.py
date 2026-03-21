__version__ = "0.1.0"

from .analyzers import LLMFailureAnalyzer, OllamaFailureAnalyzer
from .decorators import better_logger_stage, better_logger_story
from .renderer.json_renderer import JsonRenderer
from .stage import stage
from .story import story

try:
    from .middleware import BetterLoggerMiddleware
except ImportError:
    pass

__all__ = [
    "story",
    "stage",
    "better_logger_story",
    "better_logger_stage",
    "LLMFailureAnalyzer",
    "OllamaFailureAnalyzer",
    "BetterLoggerMiddleware",
    "JsonRenderer",
]
