"""
Streamware Services Layer
=========================
- core/: Service management and lifecycle
- sandbox/: Isolated execution environments
- orchestration/: Docker/Podman compose management
- context/: Conversation context and LLM memory
- text2sql/: Natural language to SQL
- text2filesystem/: Natural language to file operations
- text2shell/: Natural language to shell commands
"""

from pathlib import Path

SERVICES_DIR = Path(__file__).parent

# Core services
from services.core.service_manager import service_manager, ServiceManager
from services.sandbox.sandbox_manager import sandbox_manager, SandboxManager
from services.orchestration.orchestrator import orchestrator, Orchestrator

# Context management
from services.context.conversation_context import context_manager, ConversationContextManager

# App configuration
from services.config.app_config_manager import app_config_manager, AppConfigManager

# Text conversion services
from services.text2sql.converter import text2sql, sql2text, Text2SQL, SQL2Text
from services.text2filesystem.converter import text2filesystem, filesystem2text, Text2Filesystem, Filesystem2Text
from services.text2shell.converter import text2shell, shell2text, Text2Shell, Shell2Text

__all__ = [
    # Core
    "service_manager", "ServiceManager",
    "sandbox_manager", "SandboxManager",
    "orchestrator", "Orchestrator",
    # Context
    "context_manager", "ConversationContextManager",
    # Config
    "app_config_manager", "AppConfigManager",
    # Converters
    "text2sql", "sql2text", "Text2SQL", "SQL2Text",
    "text2filesystem", "filesystem2text", "Text2Filesystem", "Filesystem2Text", 
    "text2shell", "shell2text", "Text2Shell", "Shell2Text",
]
