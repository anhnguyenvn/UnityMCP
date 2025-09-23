#!/usr/bin/env python3.11
"""Unity MCP Server - Main Entry Point

This is the main entry point for the Unity MCP Server.
It sets up the FastMCP server with all Unity-specific tools, resources, and prompts.

Usage:
    python main.py
    
The server will run in stdio mode for local MCP client communication.
"""

import asyncio
import logging
import sys
from pathlib import Path

from config import config
from server import MCPServer


def setup_logging():
    """Configure logging for the MCP server"""
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=config.log_format,
        stream=sys.stderr,  # MCP servers must log to stderr
        force=True
    )
    
    # Set specific logger levels
    logging.getLogger("fastmcp").setLevel(logging.INFO)
    logging.getLogger("unity_mcp").setLevel(logging.DEBUG)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Unity MCP Server starting with log level: {config.log_level}")
    logger.info(f"Unity Editor path: {config.unity_editor_path}")
    logger.info(f"Unity project path: {config.unity_project_path}")
    
    return logger


def validate_environment():
    """Validate the environment and configuration"""
    logger = logging.getLogger(__name__)
    
    # Check Unity Editor path
    if config.unity_editor_path and not Path(config.unity_editor_path).exists():
        logger.warning(f"Unity Editor not found at: {config.unity_editor_path}")
        logger.warning("Some Unity operations may fail. Please check your Unity installation.")
    
    # Check Unity project path if specified
    if config.unity_project_path:
        if not config.validate_unity_project_path(config.unity_project_path):
            logger.warning(f"Invalid Unity project path: {config.unity_project_path}")
            logger.warning("Please ensure the path points to a valid Unity project.")
        else:
            logger.info(f"Unity project validated: {config.unity_project_path}")
    
    # Check security settings
    if config.allowed_paths:
        logger.info(f"Security: Allowed paths configured: {len(config.allowed_paths)} paths")
    else:
        logger.warning("Security: No allowed paths configured - all paths will be accessible")
    
    if config.blocked_extensions:
        logger.info(f"Security: Blocked extensions: {config.blocked_extensions}")
    
    logger.info(f"Security: Max operation time: {config.max_operation_time}s")


def print_server_info():
    """Print server information to stderr for debugging"""
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Unity MCP Server - Model Context Protocol Integration")
    logger.info("=" * 60)
    logger.info(f"Server Name: {config.server_name}")
    logger.info(f"Server Version: {config.server_version}")
    logger.info(f"Transport: stdio (JSON-RPC 2.0)")
    logger.info("")
    logger.info("Available MCP Tools:")
    for tool in config.enabled_tools:
        logger.info(f"  - {tool}")
    logger.info("")
    logger.info("Available MCP Resources:")
    for resource in config.enabled_resources:
        logger.info(f"  - {resource}")
    logger.info("")
    logger.info("Available MCP Prompts:")
    for prompt in config.enabled_prompts:
        logger.info(f"  - {prompt}")
    logger.info("")
    logger.info("Unity Integration:")
    logger.info(f"  - Editor Path: {config.unity_editor_path or 'Auto-detect'}")
    logger.info(f"  - Project Path: {config.unity_project_path or 'Not specified'}")
    logger.info(f"  - Log File: {config.unity_log_file}")
    logger.info("=" * 60)


async def main():
    """Main entry point for the Unity MCP Server"""
    try:
        # Setup logging first
        logger = setup_logging()
        
        # Print server information
        print_server_info()
        
        # Validate environment
        validate_environment()
        
        # Create and start the MCP server
        logger.info("Initializing Unity MCP Server...")
        server = MCPServer()
        logger.info("Unity MCP Server setup completed")
        
        # Run the server
        logger.info("Starting Unity MCP Server (stdio mode)...")
        logger.info("Server is ready to accept MCP client connections")
        
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in Unity MCP Server: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)
    finally:
        # Cleanup
        logger.info("Unity MCP Server shutdown complete")


def cli_main():
    """Command-line interface entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unity MCP Server - Model Context Protocol integration for Unity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Start server with default config
  python main.py --unity-editor /path/to/Unity.exe  # Specify Unity Editor path
  python main.py --project /path/to/project         # Specify Unity project path
  python main.py --log-level DEBUG                  # Enable debug logging

For Claude Desktop integration, add this server to your claude_desktop_config.json:
{
  "mcpServers": {
    "unity-mcp": {
      "command": "python",
      "args": ["/path/to/unity-mcp/main.py"],
      "env": {
        "UNITY_EDITOR_PATH": "/path/to/Unity/Editor",
        "UNITY_PROJECT_PATH": "/path/to/your/unity/project"
      }
    }
  }
}
"""
    )
    
    parser.add_argument(
        "--unity-editor",
        help="Path to Unity Editor executable"
    )
    
    parser.add_argument(
        "--project",
        help="Path to Unity project directory"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"Unity MCP Server {config.server_version}"
    )
    
    args = parser.parse_args()
    
    # Override config with command line arguments
    if args.unity_editor:
        config.unity_editor_path = args.unity_editor
    
    if args.project:
        config.unity_project_path = args.project
    
    if args.log_level:
        config.log_level = args.log_level
    
    # Setup logging with potentially updated level
    logger = setup_logging()
    
    if args.validate_only:
        logger.info("Validating configuration...")
        validate_environment()
        logger.info("Configuration validation complete")
        return
    
    # Run the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()