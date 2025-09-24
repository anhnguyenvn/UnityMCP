# Unity MCP Server

A Model Context Protocol (MCP) server that provides Unity Engine integration for AI assistants like Claude Desktop. This server exposes Unity project management, build automation, testing, and development tools through the MCP protocol.

## Features

### MCP Tools
- **project.scan** - Scan Unity project structure and metadata
- **build.run** - Build Unity projects with various configurations
- **test.playmode** - Run Unity Play Mode tests
- **test.editmode** - Run Unity Edit Mode tests
- **scene.validate** - Validate Unity scenes for issues
- **asset.audit** - Audit Unity assets and dependencies
- **codegen.apply** - Apply code generation to Unity projects
- **editor.exec** - Execute custom Unity Editor commands
- **perf.profile** - Profile Unity project performance

### MCP Resources
- **unity://project/{path}** - Access Unity project metadata and configuration
- **unity://scenes/{path}** - Browse Unity scene data and hierarchy
- **unity://assets/{path}** - Access Unity asset database
- **unity://logs/{path}** - Access Unity console logs

### MCP Prompts
- **unity.build** - Build configuration and troubleshooting guidance
- **unity.debug** - Debugging strategies and diagnostic guidance
- **unity.optimize** - Performance optimization recommendations

## Installation

### Prerequisites
- **Python 3.10 or higher** (Required for MCP framework)
- Unity Editor (2023.3.0f1 or higher recommended)
- Claude Desktop or other MCP client

⚠️ **Important**: The MCP (Model Context Protocol) framework requires Python 3.10+. Please upgrade if you're using an older version.

### Quick Setup

1. **Clone the Unity MCP Server:**
   ```bash
   git clone https://github.com/anhnguyenvn/UnityMCP.git
   cd UnityMCP
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Unity paths:**
   Create a `.env` file in the project root:
   ```bash
   UNITY_MCP_UNITY_EDITOR_PATH=/Applications/Unity/Hub/Editor/2023.3.0f1/Unity.app/Contents/MacOS/Unity
   UNITY_MCP_UNITY_PROJECT_PATH=/path/to/your/unity/project
   UNITY_MCP_LOG_LEVEL=INFO
   ```

4. **Copy Unity Bridge script to your Unity project:**
   ```bash
   cp unity_bridge.cs /path/to/your/unity/project/Assets/Scripts/
   ```

📖 **For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md)**

## Configuration

The server can be configured through environment variables, `.env` file, or command-line arguments:

### Environment Variables (with UNITY_MCP_ prefix)
- `UNITY_MCP_UNITY_EDITOR_PATH` - Path to Unity Editor executable
- `UNITY_MCP_UNITY_PROJECT_PATH` - Default Unity project path
- `UNITY_MCP_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `UNITY_MCP_MAX_OPERATION_TIME` - Maximum operation timeout in seconds
- `UNITY_MCP_ALLOWED_PATHS` - Comma-separated list of allowed file paths
- `UNITY_MCP_BLOCKED_EXTENSIONS` - Comma-separated list of blocked file extensions

### Command Line Arguments
```bash
python main.py --help
```

Options:
- `--unity-editor PATH` - Path to Unity Editor executable
- `--project PATH` - Path to Unity project directory
- `--log-level LEVEL` - Set logging level
- `--validate-only` - Validate configuration and exit
- `--version` - Show version information

## Usage

### Standalone Mode
Run the server directly for testing:
```bash
python main.py
```

### Claude Desktop Integration

Add the Unity MCP Server to your Claude Desktop configuration:

1. **Locate your Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add the Unity MCP Server configuration:**
   ```json
   {
     "mcpServers": {
       "unity-mcp": {
         "command": "python",
         "args": ["/absolute/path/to/UnityMCP/main.py"],
         "env": {
           "UNITY_MCP_UNITY_EDITOR_PATH": "/Applications/Unity/Hub/Editor/2023.3.0f1/Unity.app/Contents/MacOS/Unity",
           "UNITY_MCP_UNITY_PROJECT_PATH": "/path/to/your/unity/project",
           "UNITY_MCP_LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

3. **Use the provided example config:**
   ```bash
   cp claude_desktop_config.example.json claude_desktop_config.json
   # Edit the paths in claude_desktop_config.json
   ```

4. **Restart Claude Desktop** to load the new MCP server.

📖 **For detailed Claude Desktop setup, see [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)**

### Unity Project Setup

For full functionality, copy the Unity Bridge script to your Unity project:

1. **Copy the Unity Bridge script:**
   ```bash
   cp unity_bridge.cs /path/to/your/unity/project/Assets/Editor/
   ```

2. **The script will be automatically compiled by Unity** and provide enhanced MCP integration.

### Running the Server

#### Test the server (standalone mode)
```bash
python main.py
```

#### With specific Unity project
```bash
python main.py --project /path/to/unity/project
```

#### With custom Unity Editor
```bash
python main.py --unity-editor /path/to/Unity.app/Contents/MacOS/Unity
```

#### Validate configuration
```bash
python main.py --validate-only
```

## Examples

### Using MCP Tools in Claude Desktop

Once configured, you can use Unity MCP tools in Claude Desktop:

**Scan a Unity project:**
```
Can you scan my Unity project and tell me about its structure?
```

**Build the project:**
```
Please build my Unity project for Windows 64-bit with development build enabled.
```

**Run tests:**
```
Run all the Play Mode tests in my Unity project and show me the results.
```

**Validate scenes:**
```
Check my Unity scenes for any missing references or validation issues.
```

**Access project resources:**
```
Show me the project settings and package dependencies.
```

### Direct MCP Protocol Usage

For advanced users, you can interact with the server using the MCP protocol directly:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def example_usage():
    server_params = StdioServerParameters(
        command="python",
        args=["main.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool("project.scan", {
                "project_path": "/path/to/unity/project",
                "include_assets": True,
                "include_scripts": True
            })
            print(f"Scan result: {result.content}")
```

## Architecture

The Unity MCP Server consists of several key components:

### Core Components
- **server.py** - Main FastMCP server implementation
- **config.py** - Configuration management
- **unity_manager.py** - Unity process management and communication

### MCP Integration
- **mcp_tools.py** - Unity-specific MCP tools
- **mcp_resources.py** - Unity project resource access
- **mcp_prompts.py** - Unity development prompt templates

### Unity Integration
- **unity_bridge.cs** - C# Unity Editor script for enhanced integration
- **Unity Editor Batch Mode** - Command-line Unity operations
- **Unity Log Parsing** - Real-time log monitoring and analysis

### Communication Flow
1. **MCP Client** (Claude Desktop) connects via stdio transport
2. **FastMCP Server** handles JSON-RPC 2.0 protocol communication
3. **Unity Manager** executes Unity Editor commands in batch mode
4. **Unity Bridge** (C# script) provides enhanced Unity integration
5. **Results** are returned through the MCP protocol to the client

## Security

The Unity MCP Server includes several security features:

- **Path Validation** - Restricts file access to allowed paths
- **Extension Blocking** - Prevents access to sensitive file types
- **Operation Timeouts** - Limits maximum execution time
- **Process Isolation** - Unity operations run in separate processes
- **Logging** - Comprehensive audit trail of all operations

### Security Configuration

```python
# Example security settings in config.py
allowed_paths = [
    "/path/to/unity/projects",
    "/path/to/safe/directory"
]

blocked_extensions = [
    ".exe", ".dll", ".so", ".dylib",
    ".bat", ".sh", ".ps1"
]

max_operation_time_seconds = 300  # 5 minutes
```

## Troubleshooting

### Common Issues

**Unity Editor not found:**
```
WARNING: Unity Editor not found at: /path/to/unity
```
- Solution: Set the correct `UNITY_EDITOR_PATH` environment variable
- Use `--unity-editor` command line argument
- Ensure Unity is installed and accessible

**Invalid Unity project:**
```
WARNING: Invalid Unity project path: /path/to/project
```
- Solution: Ensure the path contains `Assets/` and `ProjectSettings/` folders
- Verify the project is a valid Unity project

**Permission denied:**
```
ERROR: Permission denied accessing: /restricted/path
```
- Solution: Add the path to `allowed_paths` configuration
- Check file system permissions

**Operation timeout:**
```
ERROR: Operation timed out after 300 seconds
```
- Solution: Increase `max_operation_time_seconds` setting
- Optimize Unity project for faster operations

### Debug Mode

Enable debug logging for detailed troubleshooting:
```bash
python main.py --log-level DEBUG
```

Or set environment variable:
```bash
export UNITY_LOG_LEVEL=DEBUG
python main.py
```

### Validation

Validate your configuration without starting the server:
```bash
python main.py --validate-only
```

## Development

### Project Structure
```
unity-mcp-server/
├── main.py              # Main entry point
├── server.py            # FastMCP server implementation
├── config.py            # Configuration management
├── unity_manager.py     # Unity process management
├── mcp_tools.py         # MCP tools implementation
├── mcp_resources.py     # MCP resources implementation
├── mcp_prompts.py       # MCP prompts implementation
├── unity_bridge.cs      # Unity C# integration script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Tools

To add a new MCP tool:

1. **Define the tool in `mcp_tools.py`:**
   ```python
   @app.tool()
   async def my_new_tool(param1: str, param2: int) -> str:
       """Description of the new tool"""
       # Implementation
       return "Result"
   ```

2. **Add to enabled tools in `config.py`:**
   ```python
   enabled_tools = [
       # ... existing tools
       "my.new.tool"
   ]
   ```

3. **Test the new tool:**
   ```bash
   python main.py --validate-only
   ```

### Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=. tests/
```

### Code Quality

Format code:
```bash
black .
```

Lint code:
```bash
flake8 .
```

Type checking:
```bash
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Enable debug logging for detailed error information

## Changelog

### Version 1.0.0
- Initial release
- Full MCP protocol support
- Unity Editor integration
- Comprehensive tool set
- Security features
- Claude Desktop integration