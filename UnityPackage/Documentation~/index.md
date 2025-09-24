# Unity MCP Bridge Package Documentation

## Overview

Unity MCP Bridge Package provides seamless integration between Unity Editor and MCP (Model Context Protocol) servers, enabling AI-assisted Unity development workflows. This package eliminates the need for manual path configuration and provides a robust, user-friendly interface for MCP operations.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Features](#features)
4. [API Reference](#api-reference)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

## Installation

### Method 1: Package Manager (Recommended)

1. Open Unity Package Manager (`Window > Package Manager`)
2. Click the `+` button in the top-left corner
3. Select `Add package from git URL`
4. Enter the repository URL: `https://github.com/anhnguyenvn/UnityMCP.git?path=/UnityPackage`
5. Click `Add`

### Method 2: Local Installation

1. Download or clone the repository
2. In Unity Package Manager, click `+` and select `Add package from disk`
3. Navigate to the `UnityPackage` folder
4. Select `package.json`

### Method 3: Manual Installation

1. Copy the entire `UnityPackage` folder to your project's `Packages` directory
2. Unity will automatically detect and import the package

## Quick Start

### 1. Package Initialization

The package automatically initializes when Unity loads. You'll see initialization messages in the Console:

```
[Unity MCP Bridge] Unity MCP Bridge Package initialized (v1.0.0)
[Unity MCP Bridge] Package path: Packages/com.unitymcp.bridge
```

### 2. Open MCP Bridge Window

Access the main interface via:
`Window > Unity MCP > MCP Bridge Window`

### 3. Add Runtime Component (Optional)

For runtime MCP functionality, add the MCP Runtime component to a GameObject:

1. Create an empty GameObject
2. Add the `UnityMCPRuntime` component
3. Configure settings in the Inspector

### 4. Run Your First Scan

1. In the MCP Bridge Window, click `Scan Project`
2. Results will be saved to `Temp/MCP/project_scan_result.json`
3. View results in the output folder

## Features

### 🔄 Automatic Configuration
- **Auto-detection**: Automatically detects Unity Editor path
- **No manual setup**: Eliminates need for path configuration
- **Cross-platform**: Works on Windows, macOS, and Linux

### 🛠️ Project Analysis
- **Comprehensive scanning**: Analyzes scenes, assets, scripts, and settings
- **JSON output**: Structured data for MCP server consumption
- **Real-time updates**: Live project information

### 🏗️ Build Integration
- **Automated builds**: Trigger builds through MCP commands
- **Build reporting**: Detailed build results and error reporting
- **Multi-platform support**: Support for various build targets

### 🧪 Test Management
- **PlayMode tests**: Run and manage PlayMode tests
- **EditMode tests**: Execute EditMode test suites
- **Test reporting**: Comprehensive test result reporting

### ⚙️ Editor Integration
- **Native menus**: Integrated Unity Editor menu items
- **Settings window**: User-friendly configuration interface
- **Real-time status**: Live connection and operation status

## API Reference

### UnityMCPBridge (Static Class)

Main bridge class for MCP server communication.

#### Methods

```csharp
// Get Unity Editor executable path
public static string GetUnityEditorPath()

// Get current project path
public static string GetProjectPath()

// Validate Unity project
public static bool IsValidUnityProject(string path = null)

// Get project information
public static ProjectInfo GetProjectInfo()

// Write operation result
public static void WriteResult(string operation, object data)

// Write operation error
public static void WriteError(string operation, string error)

// Manual project scan
[MenuItem("Window/Unity MCP/Scan Project")]
public static void ScanProject()
```

### UnityMCPRuntime (MonoBehaviour)

Runtime component for MCP integration.

#### Properties

```csharp
// Singleton instance
public static UnityMCPRuntime Instance { get; private set; }

// Connection status
public static bool IsConnected { get; private set; }
```

#### Methods

```csharp
// Send message to MCP server
public static void SendMCPMessage(string message)

// Get current configuration
public static Dictionary<string, object> GetMCPConfiguration()

// Set MCP server endpoint
public static void SetMCPEndpoint(string endpoint)

// Enable/disable debug logging
public static void SetDebugLogging(bool enabled)
```

#### Events

```csharp
// MCP message received
public static event Action<string> OnMCPMessage;

// Connection status changed
public static event Action<bool> OnMCPConnectionChanged;
```

### Data Types

#### MCPMessage
```csharp
public class MCPMessage
{
    public string id;
    public string type;
    public string action;
    public Dictionary<string, object> parameters;
    public DateTime timestamp;
}
```

#### ProjectInfo
```csharp
public class ProjectInfo
{
    public string projectName;
    public string companyName;
    public string version;
    public string unityVersion;
    public string platform;
    public int sceneCount;
    public int assetCount;
    public int scriptCount;
    public DateTime lastModified;
}
```

## Configuration

### Editor Settings

Configure the package through the MCP Bridge Window:

1. **Connection Settings**
   - MCP Server Endpoint
   - Connection Timeout
   - Debug Logging

2. **Project Information**
   - Project Path
   - Unity Editor Path
   - Validation Status

### Runtime Settings

Configure runtime behavior through the UnityMCPRuntime component:

- **Enable MCP Integration**: Toggle MCP functionality
- **MCP Server Endpoint**: Server connection URL
- **Connection Timeout**: Timeout for server connections
- **Enable Debug Logging**: Verbose logging for debugging

### Persistent Settings

Settings are automatically saved using EditorPrefs:

- `UnityMCP.ServerEndpoint`
- `UnityMCP.ConnectionTimeout`
- `UnityMCP.DebugLogging`

## Troubleshooting

### Common Issues

#### Package Not Loading
**Problem**: Package doesn't appear in Package Manager
**Solution**: 
1. Check Unity version compatibility (2022.3+)
2. Verify package.json syntax
3. Restart Unity Editor

#### MCP Bridge Window Not Opening
**Problem**: Menu item doesn't appear or window won't open
**Solution**:
1. Check Console for initialization errors
2. Verify assembly definitions are correct
3. Reimport package

#### Runtime Component Not Found
**Problem**: UnityMCPRuntime.Instance returns null
**Solution**:
1. Add UnityMCPRuntime component to a GameObject
2. Ensure GameObject is active in scene
3. Check for script compilation errors

#### Connection Issues
**Problem**: Cannot connect to MCP server
**Solution**:
1. Verify MCP server is running
2. Check endpoint URL and port
3. Review firewall settings
4. Enable debug logging for details

### Debug Information

Enable debug logging to get detailed information:

1. Open MCP Bridge Window
2. Enable "Enable Debug Logging"
3. Check Console and log files in `Temp/MCP/`

### Log Files

- **Unity Console**: Real-time debug messages
- **Temp/MCP/mcp_unity.log**: Detailed operation logs
- **Temp/MCP/*_result.json**: Operation results
- **Temp/MCP/*_error.json**: Error details

## Advanced Usage

### Custom MCP Commands

Extend functionality by implementing custom MCP commands:

```csharp
public static class CustomMCPCommands
{
    [MenuItem("Window/Unity MCP/Custom Command")]
    public static void ExecuteCustomCommand()
    {
        try
        {
            // Your custom logic here
            var result = new { customData = "example" };
            UnityMCPBridge.WriteResult("custom_command", result);
        }
        catch (Exception e)
        {
            UnityMCPBridge.WriteError("custom_command", e.Message);
        }
    }
}
```

### Runtime Event Handling

Subscribe to MCP events for custom behavior:

```csharp
void Start()
{
    UnityMCPRuntime.OnMCPMessage += HandleMCPMessage;
    UnityMCPRuntime.OnMCPConnectionChanged += HandleConnectionChange;
}

void HandleMCPMessage(string message)
{
    Debug.Log($"Received MCP message: {message}");
}

void HandleConnectionChange(bool connected)
{
    Debug.Log($"MCP connection status: {connected}");
}
```

### Integration with Build Pipeline

Integrate with Unity's build pipeline:

```csharp
public class MCPBuildProcessor : IPreprocessBuildWithReport, IPostprocessBuildWithReport
{
    public int callbackOrder => 0;

    public void OnPreprocessBuild(BuildReport report)
    {
        UnityMCPBridge.WriteResult("build_started", new { 
            target = report.summary.platform,
            time = DateTime.Now 
        });
    }

    public void OnPostprocessBuild(BuildReport report)
    {
        UnityMCPBridge.WriteResult("build_completed", new { 
            result = report.summary.result,
            duration = report.summary.totalTime 
        });
    }
}
```

## Support and Contributing

- **Documentation**: [Unity MCP Wiki](https://github.com/anhnguyenvn/UnityMCP/wiki)
- **Issues**: [GitHub Issues](https://github.com/anhnguyenvn/UnityMCP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/anhnguyenvn/UnityMCP/discussions)
- **Contributing**: See CONTRIBUTING.md in the main repository

## License

This package is licensed under the MIT License. See LICENSE.md for details.