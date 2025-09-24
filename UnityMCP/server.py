#!/usr/bin/env python3
"""Unity MCP Server - FastMCP Implementation

This module implements the Unity MCP Server using the FastMCP framework.
It provides Unity Engine integration through the Model Context Protocol (MCP).

The server exposes Unity-specific tools, resources, and prompts to MCP clients
like Claude Desktop, enabling AI assistants to interact with Unity projects.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from config import config
from unity_manager import UnityManager
from mcp_tools import register_tools
from mcp_resources import register_resources
from mcp_prompts import register_prompts


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format=config.log_format,
    stream=sys.stderr  # MCP servers should log to stderr
)
logger = logging.getLogger(__name__)


class MCPServer:
    """Unity MCP Server Implementation"""
    
    def __init__(self):
        self.mcp = FastMCP(config.server_name)
        self.unity_manager = UnityManager()
        self._setup_server()
    
    def _setup_server(self):
        """Setup MCP server with tools, resources, and prompts"""
        logger.info(f"Initializing {config.server_name} v{config.server_version}")
        
        # Register MCP components
        register_tools(self.mcp, self.unity_manager)
        register_resources(self.mcp, self.unity_manager)
        register_prompts(self.mcp)
        
        # Server info is handled automatically by FastMCP
        
        logger.info("MCP server setup completed")
    
    async def run(self):
        """Run the MCP server"""
        try:
            logger.info("Starting Unity MCP Server...")
            await self.mcp.run_stdio_async()
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup server resources"""
        logger.info("Cleaning up server resources...")
        await self.unity_manager.cleanup()
        logger.info("Server cleanup completed")


async def main():
    """Main entry point"""
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())