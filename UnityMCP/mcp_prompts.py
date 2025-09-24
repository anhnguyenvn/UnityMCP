"""MCP Prompts Implementation for Unity Development Templates"""

import logging
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from config import config


logger = logging.getLogger(__name__)


class PromptArgument(BaseModel):
    """Prompt argument definition"""
    name: str
    description: str
    required: bool = True


class UnityPrompt(BaseModel):
    """Unity prompt template model"""
    name: str
    description: str
    arguments: List[PromptArgument]
    template: str


def register_prompts(mcp: FastMCP):
    """Register all Unity MCP prompts"""
    
    @mcp.prompt("unity.build")
    async def unity_build_prompt(
        project_path: str,
        target_platform: str = "StandaloneWindows64",
        build_options: str = "None",
        output_path: str = ""
    ) -> Dict[str, str]:
        """Generate Unity build configuration and troubleshooting guidance"""
        
        template = f"""# Unity Build Configuration and Guidance

## Project Information
- **Project Path**: {project_path}
- **Target Platform**: {target_platform}
- **Build Options**: {build_options}
- **Output Path**: {output_path or "Default build location"}

## Build Process Steps

### 1. Pre-Build Validation
```bash
# Validate Unity project structure
# Check for:
# - Valid Unity project (Assets/, ProjectSettings/ folders)
# - No compilation errors in scripts
# - All required assets are present
# - Build settings are configured correctly
```

### 2. Build Configuration
```csharp
// Unity Build Settings Configuration
// Platform: {target_platform}
// Build Options: {build_options}

// Recommended build pipeline:
// 1. Clean previous builds
// 2. Refresh asset database
// 3. Run pre-build validation
// 4. Execute build with specified options
// 5. Post-build verification
```

### 3. Common Build Issues and Solutions

#### Compilation Errors
- **Issue**: Script compilation failures
- **Solution**: Check Console for error details, fix syntax/reference errors
- **Command**: Use `project.scan` tool to identify issues

#### Asset Import Issues
- **Issue**: Missing or corrupted assets
- **Solution**: Reimport assets, check import settings
- **Command**: Use `asset.audit` tool for asset validation

#### Platform-Specific Issues
- **Issue**: Platform compatibility problems
- **Solution**: Verify platform-specific settings and dependencies
- **Command**: Check Player Settings for target platform

#### Build Size Optimization
- **Issue**: Large build size
- **Solution**: Enable asset compression, remove unused assets
- **Command**: Use `perf.profile` tool for optimization analysis

### 4. Build Verification
```bash
# Post-build checks:
# - Verify build output exists
# - Check build log for warnings/errors
# - Test executable functionality
# - Validate asset loading
```

### 5. Recommended MCP Tools for Build Process
- `project.scan`: Validate project before building
- `build.run`: Execute the actual build process
- `asset.audit`: Check asset integrity
- `perf.profile`: Analyze build performance
- `editor.exec`: Run custom build scripts

## Build Command Template
```bash
# Use the build.run MCP tool:
# Parameters:
# - project_path: "{project_path}"
# - target_platform: "{target_platform}"
# - build_options: "{build_options}"
# - output_path: "{output_path}"
```

## Troubleshooting Checklist
- [ ] Unity Editor version compatibility
- [ ] All scripts compile without errors
- [ ] Required packages are installed
- [ ] Build settings are correctly configured
- [ ] Sufficient disk space for build output
- [ ] No file permission issues
- [ ] Platform-specific requirements met
"""
        
        return {
            "description": f"Unity build guidance for {target_platform} platform",
            "content": template
        }
    
    @mcp.prompt("unity.debug")
    async def unity_debug_prompt(
        issue_type: str = "general",
        error_message: str = "",
        context: str = ""
    ) -> Dict[str, str]:
        """Generate Unity debugging strategies and diagnostic guidance"""
        
        template = f"""# Unity Debugging and Diagnostic Guide

## Issue Analysis
- **Issue Type**: {issue_type}
- **Error Message**: {error_message or "No specific error provided"}
- **Context**: {context or "General debugging"}

## Debugging Strategy

### 1. Initial Diagnosis
```csharp
// Unity Console Analysis
// Check for:
// - Compilation errors (red messages)
// - Runtime exceptions (red messages)
// - Warnings (yellow messages)
// - Info messages (white messages)
```

### 2. Common Unity Issues and Solutions

#### Script Compilation Errors
```csharp
// Common causes:
// - Missing using statements
// - Incorrect class/method signatures
// - Missing references or assemblies
// - Syntax errors

// Debugging steps:
// 1. Check Console for specific error details
// 2. Verify all required namespaces are imported
// 3. Check assembly references in .asmdef files
// 4. Ensure Unity API compatibility
```

#### Runtime Exceptions
```csharp
// Common runtime issues:
// - NullReferenceException
// - IndexOutOfRangeException
// - MissingReferenceException
// - Component not found errors

// Debugging approach:
// 1. Use Debug.Log() for variable inspection
// 2. Set breakpoints in IDE (if available)
// 3. Check object references in Inspector
// 4. Validate scene setup and prefab connections
```

#### Performance Issues
```csharp
// Performance debugging:
// - Use Unity Profiler
// - Check frame rate in Game view
// - Monitor memory usage
// - Analyze draw calls and batching

// Tools to use:
// - perf.profile MCP tool
// - Unity Profiler window
// - Frame Debugger
```

#### Asset Loading Issues
```csharp
// Asset-related problems:
// - Missing asset references
// - Incorrect asset paths
// - Import setting conflicts
// - Platform-specific asset issues

// Debugging steps:
// 1. Use asset.audit MCP tool
// 2. Check asset import settings
// 3. Verify file paths and naming
// 4. Test asset loading in different contexts
```

### 3. Debugging Tools and Techniques

#### Unity Built-in Tools
- **Console Window**: Error messages and logs
- **Inspector**: Object state and references
- **Scene View**: Visual debugging
- **Game View**: Runtime behavior
- **Profiler**: Performance analysis

#### MCP Tools for Debugging
- `project.scan`: Comprehensive project analysis
- `test.playmode`: Runtime testing
- `test.editmode`: Editor-time testing
- `scene.validate`: Scene integrity checks
- `asset.audit`: Asset validation
- `editor.exec`: Custom diagnostic scripts

### 4. Systematic Debugging Process

#### Step 1: Reproduce the Issue
```bash
# Document:
# - Exact steps to reproduce
# - Expected vs actual behavior
# - Environment details (Unity version, platform)
# - Recent changes or modifications
```

#### Step 2: Isolate the Problem
```bash
# Techniques:
# - Binary search (disable half of components)
# - Minimal reproduction case
# - Test in empty scene
# - Compare with working version
```

#### Step 3: Gather Information
```bash
# Use MCP tools:
# - project.scan for overall health
# - Check logs with unity://logs resource
# - Validate assets with asset.audit
# - Run targeted tests
```

#### Step 4: Apply Fixes
```bash
# Fix strategies:
# - Address root cause, not symptoms
# - Test fix in isolation
# - Verify no regression introduced
# - Document solution for future reference
```

### 5. Specific Issue Type Guidance

{self._get_specific_debug_guidance(issue_type, error_message)}

## Debugging Checklist
- [ ] Console cleared of all errors and warnings
- [ ] All object references properly assigned
- [ ] Scene setup matches expected configuration
- [ ] Asset import settings are correct
- [ ] Platform-specific settings verified
- [ ] Performance within acceptable limits
- [ ] Tests pass (if available)
"""
        
        return {
            "description": f"Unity debugging guidance for {issue_type} issues",
            "content": template
        }
    
    @mcp.prompt("unity.optimize")
    async def unity_optimize_prompt(
        optimization_target: str = "performance",
        platform: str = "general",
        current_metrics: str = ""
    ) -> Dict[str, str]:
        """Generate Unity optimization strategies and performance improvement guidance"""
        
        template = f"""# Unity Optimization and Performance Guide

## Optimization Target
- **Focus Area**: {optimization_target}
- **Target Platform**: {platform}
- **Current Metrics**: {current_metrics or "Baseline measurement needed"}

## Performance Optimization Strategy

### 1. Performance Profiling and Analysis
```csharp
// Use Unity Profiler to identify bottlenecks:
// - CPU usage patterns
// - Memory allocation and garbage collection
// - Rendering performance (draw calls, batching)
// - Physics simulation overhead
// - Audio processing load
```

### 2. Rendering Optimization

#### Draw Call Reduction
```csharp
// Techniques:
// - Static batching for non-moving objects
// - Dynamic batching for small moving objects
// - GPU Instancing for identical objects
// - Texture atlasing to reduce material count
// - LOD (Level of Detail) systems

// Implementation:
// 1. Mark static objects as "Static"
// 2. Use same materials for similar objects
// 3. Combine meshes where appropriate
// 4. Implement LOD groups for complex models
```

#### Shader and Material Optimization
```csharp
// Best practices:
// - Use mobile-friendly shaders for mobile platforms
// - Minimize texture samples in shaders
// - Avoid complex calculations in fragment shaders
// - Use texture compression appropriate for platform
// - Implement shader variants judiciously
```

#### Lighting Optimization
```csharp
// Lighting strategies:
// - Use baked lighting for static scenes
// - Limit real-time lights (especially shadows)
// - Use Light Probes for dynamic objects
// - Implement culling for lights
// - Consider forward vs deferred rendering
```

### 3. Memory Optimization

#### Asset Memory Management
```csharp
// Memory reduction techniques:
// - Compress textures appropriately
// - Use audio compression
// - Optimize mesh vertex counts
// - Remove unused assets
// - Implement asset streaming for large worlds
```

#### Runtime Memory Management
```csharp
// Code optimization:
// - Minimize garbage collection
// - Use object pooling for frequently created/destroyed objects
// - Cache component references
// - Avoid string concatenation in Update loops
// - Use StringBuilder for dynamic strings
```

### 4. CPU Optimization

#### Script Performance
```csharp
// Optimization techniques:
// - Minimize Update() calls
// - Use coroutines for spread-out operations
// - Cache expensive calculations
// - Use events instead of polling
// - Implement spatial partitioning for collision detection
```

#### Physics Optimization
```csharp
// Physics performance:
// - Reduce physics timestep if appropriate
// - Use simpler colliders where possible
// - Implement physics layers for selective collision
// - Consider kinematic rigidbodies for UI elements
// - Optimize mesh colliders or avoid them
```

### 5. Platform-Specific Optimizations

#### Mobile Optimization
```csharp
// Mobile-specific considerations:
// - Target 30 FPS for better battery life
// - Use PVRTC/ETC texture compression
// - Minimize overdraw
// - Reduce particle effects complexity
// - Implement aggressive LOD systems
```

#### PC/Console Optimization
```csharp
// Desktop/console considerations:
// - Target 60+ FPS
// - Utilize multi-threading where possible
// - Implement advanced rendering features
// - Use higher quality assets
// - Consider ray tracing on supported hardware
```

### 6. Optimization Tools and Workflow

#### Unity Built-in Tools
- **Profiler**: Performance analysis
- **Frame Debugger**: Rendering analysis
- **Memory Profiler**: Memory usage analysis
- **Physics Debugger**: Physics performance

#### MCP Tools for Optimization
- `perf.profile`: Automated performance analysis
- `asset.audit`: Asset optimization opportunities
- `project.scan`: Overall project health
- `build.run`: Build size analysis

### 7. Optimization Checklist

#### Rendering
- [ ] Draw calls minimized through batching
- [ ] Appropriate LOD levels implemented
- [ ] Texture compression optimized for platform
- [ ] Shader complexity appropriate for target hardware
- [ ] Lighting setup optimized (baked vs real-time)

#### Memory
- [ ] Asset sizes optimized for target platform
- [ ] Unused assets removed from build
- [ ] Object pooling implemented for frequent allocations
- [ ] Memory leaks identified and fixed

#### CPU
- [ ] Update loops optimized
- [ ] Expensive operations cached or spread out
- [ ] Physics simulation optimized
- [ ] Garbage collection minimized

#### Platform-Specific
- [ ] Platform-specific settings configured
- [ ] Target frame rate achievable
- [ ] Battery usage optimized (mobile)
- [ ] Loading times acceptable

### 8. Performance Monitoring
```csharp
// Continuous monitoring:
// - Set up automated performance tests
// - Monitor key metrics (FPS, memory, draw calls)
// - Use Unity Analytics for production monitoring
// - Implement in-game performance displays for development
```

## Optimization Command Templates
```bash
# Use MCP tools for optimization analysis:
# perf.profile - Comprehensive performance analysis
# asset.audit - Asset optimization opportunities
# project.scan - Overall project health check
```

{self._get_specific_optimization_guidance(optimization_target, platform)}
"""
        
        return {
            "description": f"Unity optimization guidance for {optimization_target} on {platform}",
            "content": template
        }
    
    def _get_specific_debug_guidance(self, issue_type: str, error_message: str) -> str:
        """Get specific debugging guidance based on issue type"""
        
        guidance_map = {
            "compilation": """
#### Compilation Error Specific Guidance
- Check for missing semicolons, brackets, or parentheses
- Verify all using statements are correct
- Ensure class and method names follow C# conventions
- Check for circular dependencies between scripts
- Validate Unity API usage for current Unity version
""",
            "runtime": """
#### Runtime Error Specific Guidance
- Use try-catch blocks to handle exceptions gracefully
- Add null checks before accessing objects
- Validate array/list bounds before access
- Check GameObject and Component references in Inspector
- Use Debug.Log to trace execution flow
""",
            "performance": """
#### Performance Issue Specific Guidance
- Use Unity Profiler to identify bottlenecks
- Check for expensive operations in Update loops
- Monitor garbage collection frequency
- Analyze draw calls and rendering performance
- Review physics simulation complexity
""",
            "ui": """
#### UI Issue Specific Guidance
- Check Canvas settings and render modes
- Verify UI element anchoring and positioning
- Test UI scaling across different resolutions
- Check for UI raycast blocking issues
- Validate event system configuration
"""
        }
        
        return guidance_map.get(issue_type, """
#### General Debugging Guidance
- Start with Unity Console for error messages
- Use systematic elimination to isolate issues
- Test in minimal reproduction scenarios
- Check Unity documentation for API changes
- Consider recent project modifications
""")
    
    def _get_specific_optimization_guidance(self, target: str, platform: str) -> str:
        """Get specific optimization guidance based on target and platform"""
        
        target_guidance = {
            "rendering": """
## Rendering-Specific Optimization
- Implement occlusion culling for complex scenes
- Use texture streaming for large textures
- Optimize shadow rendering (cascade count, resolution)
- Implement dynamic resolution scaling
- Use GPU-based particle systems
""",
            "memory": """
## Memory-Specific Optimization
- Implement asset bundles for content streaming
- Use compressed audio formats
- Optimize texture memory usage
- Implement garbage collection optimization
- Use native collections for large datasets
""",
            "loading": """
## Loading Time Optimization
- Implement asynchronous scene loading
- Use asset bundles for modular content
- Optimize asset import settings
- Implement progressive loading systems
- Use addressable assets system
"""
        }
        
        return target_guidance.get(target, """
## General Performance Optimization
- Profile regularly during development
- Set performance budgets and monitor them
- Implement scalable quality settings
- Use platform-appropriate optimization techniques
- Test on target hardware frequently
""")
    
    logger.info("Unity MCP prompts registered successfully")