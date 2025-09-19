"""Backend package initialization."""

from .config import settings
from .openai_integration import openai_client
from .automation_scripts import workflow_engine
from .server import app

__version__ = "1.0.0"
__all__ = ["settings", "openai_client", "workflow_engine", "app"]