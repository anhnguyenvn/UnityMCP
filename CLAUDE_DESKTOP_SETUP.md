# Claude Desktop Integration Guide

This guide provides step-by-step instructions for integrating the Unity MCP Server with Claude Desktop.

## Prerequisites

- Claude Desktop application installed
- Python 3.8+ installed
- Unity Editor installed (2020.3 LTS or higher recommended)
- Unity MCP Server downloaded and dependencies installed

## Step 1: Install Unity MCP Server

1. **Navigate to the Unity MCP Server directory:**
   ```bash
   cd /path/to/unity-mcp-server
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the server (optional):**
   ```bash
   python main.py --validate-only
   ```

## Step 2: Locate Claude Desktop Configuration

Find your Claude Desktop configuration file based on your operating system:

### macOS
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

### Linux
```bash
~/.config/Claude/claude_desktop_config.json
```

## Step 3: Configure Claude Desktop

1. **Open the configuration file** in your preferred text editor.

2. **If the file doesn't exist**, create it with the following basic structure:
   ```json
   {
     "mcpServers": {}
   }
   ```

3. **Add the Unity MCP Server configuration** inside the `mcpServers` object:
   ```json
   {
     "mcpServers": {
       "unity-mcp": {
         "command": "python",
         "args": ["/absolute/path/to/unity-mcp-server/main.py"],
         "env": {
           "UNITY_EDITOR_PATH": "/Applications/Unity/Hub/Editor/2022.3.0f1/Unity.app/Contents/MacOS/Unity",
           "UNITY_PROJECT_PATH": "/path/to/your/unity/project",
           "UNITY_LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

## Step 4: Customize Configuration

### Required Settings

**Update these paths to match your system:**

- **`args`**: Replace `/absolute/path/to/unity-mcp-server/main.py` with the actual path to your Unity MCP Server
- **`UNITY_EDITOR_PATH`**: Path to your Unity Editor executable
- **`UNITY_PROJECT_PATH`**: Path to your default Unity project (optional)

### Unity Editor Path Examples

**macOS:**
```json
"UNITY_EDITOR_PATH": "/Applications/Unity/Hub/Editor/2022.3.0f1/Unity.app/Contents/MacOS/Unity"
```

**Windows:**
```json
"UNITY_EDITOR_PATH": "C:\\Program Files\\Unity\\Hub\\Editor\\2022.3.0f1\\Editor\\Unity.exe"
```

**Linux:**
```json
"UNITY_EDITOR_PATH": "/opt/Unity/Editor/Unity"
```

### Optional Security Settings

For enhanced security, add these environment variables:

```json
"env": {
  "UNITY_EDITOR_PATH": "/path/to/unity",
  "UNITY_PROJECT_PATH": "/path/to/project",
  "UNITY_LOG_LEVEL": "INFO",
  "MCP_MAX_OPERATION_TIME": "300",
  "MCP_ALLOWED_PATHS": "/Users/username/UnityProjects,/Users/username/Documents/Unity",
  "MCP_BLOCKED_EXTENSIONS": ".exe,.dll,.so,.dylib,.bat,.sh,.ps1"
}
```

## Step 5: Install Unity Bridge (Optional)

For enhanced functionality, copy the Unity Bridge script to your Unity project:

1. **Copy the script:**
   ```bash
   cp unity_bridge.cs /path/to/your/unity/project/Assets/Editor/
   ```

2. **Open your Unity project** - the script will be automatically compiled.

## Step 6: Restart Claude Desktop

1. **Quit Claude Desktop** completely
2. **Restart Claude Desktop**
3. **Wait for initialization** - the Unity MCP Server will be loaded automatically

## Step 7: Verify Integration

Test the integration by asking Claude Desktop to interact with Unity:

### Example Prompts

**Check if Unity MCP is available:**
```
Can you scan my Unity project?
```

**List Unity tools:**
```
What Unity development tools do you have available?
```

**Project analysis:**
```
Analyze my Unity project structure and tell me about any issues.
```

## Troubleshooting

### Common Issues

**1. "Unity MCP Server not found"**
- Verify the path in `args` is correct and absolute
- Ensure Python is in your system PATH
- Check that `main.py` exists at the specified location

**2. "Unity Editor not found"**
- Verify `UNITY_EDITOR_PATH` points to the correct Unity executable
- Ensure Unity is properly installed
- Check file permissions

**3. "Permission denied"**
- Ensure the Unity MCP Server directory has proper permissions
- Add your project paths to `MCP_ALLOWED_PATHS`
- Check that Unity Editor has necessary permissions

**4. "Server initialization failed"**
- Test the server standalone: `python main.py --validate-only`
- Check Claude Desktop logs for detailed error messages
- Verify all Python dependencies are installed

### Debug Mode

Enable debug logging by changing the log level:
```json
"UNITY_LOG_LEVEL": "DEBUG"
```

### Validation

Test your configuration before using it with Claude Desktop:
```bash
cd /path/to/unity-mcp-server
python main.py --validate-only
```

## Advanced Configuration

### Multiple Unity Versions

You can configure multiple Unity MCP servers for different Unity versions:

```json
{
  "mcpServers": {
    "unity-mcp-2022": {
      "command": "python",
      "args": ["/path/to/unity-mcp-server/main.py"],
      "env": {
        "UNITY_EDITOR_PATH": "/Applications/Unity/Hub/Editor/2022.3.0f1/Unity.app/Contents/MacOS/Unity"
      }
    },
    "unity-mcp-2023": {
      "command": "python",
      "args": ["/path/to/unity-mcp-server/main.py"],
      "env": {
        "UNITY_EDITOR_PATH": "/Applications/Unity/Hub/Editor/2023.2.0f1/Unity.app/Contents/MacOS/Unity"
      }
    }
  }
}
```

### Project-Specific Configuration

Create different configurations for different projects:

```json
{
  "mcpServers": {
    "unity-mcp-project-a": {
      "command": "python",
      "args": ["/path/to/unity-mcp-server/main.py"],
      "env": {
        "UNITY_PROJECT_PATH": "/path/to/project-a",
        "UNITY_EDITOR_PATH": "/path/to/unity"
      }
    },
    "unity-mcp-project-b": {
      "command": "python",
      "args": ["/path/to/unity-mcp-server/main.py"],
      "env": {
        "UNITY_PROJECT_PATH": "/path/to/project-b",
        "UNITY_EDITOR_PATH": "/path/to/unity"
      }
    }
  }
}
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Enable debug logging
3. Test the server in standalone mode
4. Review Claude Desktop logs
5. Create an issue on the project repository

## Example Complete Configuration

Here's a complete example configuration file:

```json
{
  "mcpServers": {
    "unity-mcp": {
      "command": "python",
      "args": ["/Users/developer/unity-mcp-server/main.py"],
      "env": {
        "UNITY_EDITOR_PATH": "/Applications/Unity/Hub/Editor/2022.3.0f1/Unity.app/Contents/MacOS/Unity",
        "UNITY_PROJECT_PATH": "/Users/developer/UnityProjects/MyGame",
        "UNITY_LOG_LEVEL": "INFO",
        "MCP_MAX_OPERATION_TIME": "300",
        "MCP_ALLOWED_PATHS": "/Users/developer/UnityProjects,/Users/developer/Documents/Unity",
        "MCP_BLOCKED_EXTENSIONS": ".exe,.dll,.so,.dylib,.bat,.sh,.ps1"
      }
    }
  }
}
```

Save this configuration, restart Claude Desktop, and you're ready to use Unity MCP with Claude Desktop!