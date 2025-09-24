"""Unity MCP Server Configuration"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class MCPConfig(BaseSettings):
    """Configuration for Unity MCP Server"""
    
    # Server Information
    server_name: str = Field(default="unity-mcp-server", description="MCP Server name")
    server_version: str = Field(default="1.0.0", description="Server version")
    
    # Unity Integration Settings
    unity_editor_path: Optional[str] = Field(
        default=None,
        description="Path to Unity Editor executable"
    )
    unity_project_path: Optional[str] = Field(
        default=None,
        description="Default Unity project path"
    )
    unity_log_file: str = Field(
        default="/tmp/unity_mcp.log",
        description="Unity log file path"
    )
    
    # MCP Transport Settings
    transport: str = Field(default="stdio", description="Transport type (stdio|sse)")
    
    # Security Settings
    allowed_paths: List[str] = Field(
        default_factory=lambda: [],
        description="Allowed file system paths"
    )
    blocked_extensions: List[str] = Field(
        default_factory=lambda: [".exe", ".dll", ".so", ".dylib"],
        description="Blocked file extensions"
    )
    max_operation_time: int = Field(
        default=300,
        description="Maximum operation timeout in seconds"
    )
    
    # Tool Configuration
    enabled_tools: List[str] = Field(
        default_factory=lambda: [
            "project.scan",
            "build.run",
            "test.playmode",
            "test.editmode",
            "scene.validate",
            "asset.audit",
            "codegen.apply",
            "editor.exec",
            "perf.profile"
        ],
        description="Enabled MCP tools"
    )
    
    # Resource Configuration
    enabled_resources: List[str] = Field(
        default_factory=lambda: [
            "unity://project",
            "unity://scenes",
            "unity://assets",
            "unity://logs"
        ],
        description="Enabled MCP resources"
    )
    
    # Prompt Configuration
    enabled_prompts: List[str] = Field(
        default_factory=lambda: [
            "unity.build",
            "unity.debug",
            "unity.optimize"
        ],
        description="Enabled MCP prompts"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    
    class Config:
        env_file = ".env"
        env_prefix = "UNITY_MCP_"
    
    def get_unity_editor_path(self) -> str:
        """Get Unity Editor path with platform-specific defaults"""
        if self.unity_editor_path:
            return self.unity_editor_path
            
        # Platform-specific default paths
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return "/Applications/Unity/Hub/Editor/2023.3.0f1/Unity.app/Contents/MacOS/Unity"
        elif system == "Windows":
            return "C:\\Program Files\\Unity\\Hub\\Editor\\2023.3.0f1\\Editor\\Unity.exe"
        elif system == "Linux":
            return "/opt/Unity/Editor/Unity"
        else:
            raise ValueError(f"Unsupported platform: {system}")
    
    def validate_unity_project_path(self, path: str) -> bool:
        """Validate if path is a valid Unity project"""
        project_path = Path(path)
        return (
            project_path.exists() and
            project_path.is_dir() and
            (project_path / "Assets").exists() and
            (project_path / "ProjectSettings").exists()
        )


# Global configuration instance
config = MCPConfig()