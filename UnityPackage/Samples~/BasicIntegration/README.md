# Basic MCP Integration Sample

This sample demonstrates basic usage of the Unity MCP Bridge package.

## What's Included

- **MCPSampleController.cs**: Example script showing how to use MCP Runtime
- **SampleScene.unity**: Pre-configured scene with MCP components
- **README.md**: This documentation file

## Setup Instructions

1. Import this sample through Package Manager:
   - Open Package Manager
   - Find "Unity MCP Bridge" package
   - Expand "Samples" section
   - Click "Import" next to "Basic MCP Integration"

2. Open the sample scene:
   - Navigate to `Assets/Samples/Unity MCP Bridge/[version]/BasicIntegration/`
   - Open `SampleScene.unity`

3. Play the scene to see MCP integration in action

## Sample Features

### MCP Runtime Integration
The sample scene includes a GameObject with the `UnityMCPRuntime` component pre-configured with:
- MCP integration enabled
- Debug logging enabled
- Sample endpoint configuration

### Sample Controller Script
The `MCPSampleController` demonstrates:
- Subscribing to MCP events
- Sending MCP messages
- Handling connection status changes
- Basic error handling

## Code Example

```csharp
using UnityEngine;
using UnityMCP.Runtime;

public class MCPSampleController : MonoBehaviour
{
    void Start()
    {
        // Subscribe to MCP events
        UnityMCPRuntime.OnMCPMessage += HandleMCPMessage;
        UnityMCPRuntime.OnMCPConnectionChanged += HandleConnectionChange;
        
        // Send a test message
        UnityMCPRuntime.SendMCPMessage("Hello from Unity!");
    }
    
    void HandleMCPMessage(string message)
    {
        Debug.Log($"[MCP Sample] Received: {message}");
    }
    
    void HandleConnectionChange(bool connected)
    {
        Debug.Log($"[MCP Sample] Connection: {(connected ? "Connected" : "Disconnected")}");
    }
}
```

## Next Steps

1. **Explore the MCP Bridge Window**: `Window > Unity MCP > MCP Bridge Window`
2. **Run a project scan**: Click "Scan Project" to see comprehensive project analysis
3. **Check the output**: View results in `Temp/MCP/` folder
4. **Customize settings**: Modify MCP server endpoint and other settings
5. **Integrate with your project**: Use this sample as a starting point for your own MCP integration

## Troubleshooting

If the sample doesn't work as expected:

1. Check Unity Console for error messages
2. Verify the Unity MCP Bridge package is properly installed
3. Ensure Unity version is 2022.3.0f1 or later
4. Enable debug logging in the MCP Bridge Window for detailed information

## Support

For questions about this sample or the Unity MCP Bridge package:
- Visit the [GitHub repository](https://github.com/anhnguyenvn/UnityMCP)
- Check the [documentation](https://github.com/anhnguyenvn/UnityMCP/wiki)
- Open an [issue](https://github.com/anhnguyenvn/UnityMCP/issues) if you find bugs