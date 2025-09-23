/*
 * Unity MCP Bridge Script
 * 
 * This C# script provides integration between Unity Editor and the MCP server.
 * It handles command execution, project analysis, and data exchange.
 * 
 * Installation:
 * 1. Copy this script to your Unity project's Assets/Editor/ folder
 * 2. The script will automatically create menu items and handle MCP communication
 * 
 * Usage:
 * - The MCP server will communicate with Unity through batch mode commands
 * - This script provides utilities for project analysis and automation
 * - Results are written to files that the MCP server can read
 */

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace UnityMCP
{
    /// <summary>
    /// Main Unity MCP Bridge class for handling MCP server communication
    /// </summary>
    public static class UnityMCPBridge
    {
        private const string MCP_OUTPUT_DIR = "Temp/MCP";
        private const string MCP_LOG_FILE = "Temp/MCP/mcp_unity.log";
        
        /// <summary>
        /// Initialize MCP bridge and create necessary directories
        /// </summary>
        [InitializeOnLoadMethod]
        private static void Initialize()
        {
            // Create MCP output directory
            if (!Directory.Exists(MCP_OUTPUT_DIR))
            {
                Directory.CreateDirectory(MCP_OUTPUT_DIR);
            }
            
            LogMCP("Unity MCP Bridge initialized");
        }
        
        /// <summary>
        /// Log message to MCP log file
        /// </summary>
        private static void LogMCP(string message)
        {
            try
            {
                var logEntry = $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {message}";
                File.AppendAllText(MCP_LOG_FILE, logEntry + Environment.NewLine);
                Debug.Log($"[MCP] {message}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[MCP] Failed to write log: {e.Message}");
            }
        }
        
        /// <summary>
        /// Write result data to JSON file for MCP server consumption
        /// </summary>
        private static void WriteResult(string operation, object data)
        {
            try
            {
                var result = new
                {
                    operation = operation,
                    timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                    success = true,
                    data = data
                };
                
                var json = JsonUtility.ToJson(result, true);
                var outputFile = Path.Combine(MCP_OUTPUT_DIR, $"{operation}_result.json");
                File.WriteAllText(outputFile, json);
                
                LogMCP($"Result written for operation: {operation}");
            }
            catch (Exception e)
            {
                WriteError(operation, e.Message);
            }
        }
        
        /// <summary>
        /// Write error result to JSON file
        /// </summary>
        private static void WriteError(string operation, string error)
        {
            try
            {
                var result = new
                {
                    operation = operation,
                    timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                    success = false,
                    error = error
                };
                
                var json = JsonUtility.ToJson(result, true);
                var outputFile = Path.Combine(MCP_OUTPUT_DIR, $"{operation}_result.json");
                File.WriteAllText(outputFile, json);
                
                LogMCP($"Error written for operation {operation}: {error}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[MCP] Failed to write error: {e.Message}");
            }
        }
    }
    
    /// <summary>
    /// Project analysis and scanning functionality
    /// </summary>
    public static class ProjectScanner
    {
        /// <summary>
        /// Scan Unity project and generate comprehensive report
        /// </summary>
        [MenuItem("MCP/Scan Project")]
        public static void ScanProject()
        {
            try
            {
                LogMCP("Starting project scan...");
                
                var projectInfo = new
                {
                    projectName = Application.productName,
                    companyName = Application.companyName,
                    version = Application.version,
                    unityVersion = Application.unityVersion,
                    platform = EditorUserBuildSettings.activeBuildTarget.ToString(),
                    
                    // Scene information
                    scenes = GetSceneInfo(),
                    
                    // Asset information
                    assets = GetAssetInfo(),
                    
                    // Script information
                    scripts = GetScriptInfo(),
                    
                    // Build settings
                    buildSettings = GetBuildSettings(),
                    
                    // Project settings
                    projectSettings = GetProjectSettings(),
                    
                    // Package information
                    packages = GetPackageInfo()
                };
                
                UnityMCPBridge.WriteResult("project_scan", projectInfo);
                LogMCP("Project scan completed successfully");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("project_scan", e.Message);
                LogMCP($"Project scan failed: {e.Message}");
            }
        }
        
        private static object GetSceneInfo()
        {
            var scenes = new List<object>();
            
            // Get scenes in build settings
            for (int i = 0; i < EditorBuildSettings.scenes.Length; i++)
            {
                var scene = EditorBuildSettings.scenes[i];
                scenes.Add(new
                {
                    path = scene.path,
                    enabled = scene.enabled,
                    buildIndex = i
                });
            }
            
            return new
            {
                totalScenes = scenes.Count,
                enabledScenes = scenes.Count(s => ((dynamic)s).enabled),
                currentScene = SceneManager.GetActiveScene().name,
                scenes = scenes
            };
        }
        
        private static object GetAssetInfo()
        {
            var assetGuids = AssetDatabase.FindAssets("");
            var assetTypes = new Dictionary<string, int>();
            var totalSize = 0L;
            
            foreach (var guid in assetGuids)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var asset = AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(path);
                
                if (asset != null)
                {
                    var typeName = asset.GetType().Name;
                    assetTypes[typeName] = assetTypes.GetValueOrDefault(typeName, 0) + 1;
                    
                    // Try to get file size
                    if (File.Exists(path))
                    {
                        totalSize += new FileInfo(path).Length;
                    }
                }
            }
            
            return new
            {
                totalAssets = assetGuids.Length,
                totalSizeBytes = totalSize,
                assetTypes = assetTypes
            };
        }
        
        private static object GetScriptInfo()
        {
            var scriptGuids = AssetDatabase.FindAssets("t:MonoScript");
            var scripts = new List<object>();
            var namespaces = new HashSet<string>();
            
            foreach (var guid in scriptGuids)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var script = AssetDatabase.LoadAssetAtPath<MonoScript>(path);
                
                if (script != null && script.GetClass() != null)
                {
                    var type = script.GetClass();
                    scripts.Add(new
                    {
                        name = type.Name,
                        @namespace = type.Namespace ?? "Global",
                        path = path,
                        isMonoBehaviour = typeof(MonoBehaviour).IsAssignableFrom(type),
                        isScriptableObject = typeof(ScriptableObject).IsAssignableFrom(type),
                        isEditor = path.Contains("/Editor/")
                    });
                    
                    if (!string.IsNullOrEmpty(type.Namespace))
                    {
                        namespaces.Add(type.Namespace);
                    }
                }
            }
            
            return new
            {
                totalScripts = scripts.Count,
                namespaces = namespaces.ToList(),
                scripts = scripts
            };
        }
        
        private static object GetBuildSettings()
        {
            return new
            {
                activeBuildTarget = EditorUserBuildSettings.activeBuildTarget.ToString(),
                developmentBuild = EditorUserBuildSettings.development,
                allowDebugging = EditorUserBuildSettings.allowDebugging,
                connectProfiler = EditorUserBuildSettings.connectProfiler,
                buildAppBundle = EditorUserBuildSettings.buildAppBundle,
                exportAsGoogleAndroidProject = EditorUserBuildSettings.exportAsGoogleAndroidProject
            };
        }
        
        private static object GetProjectSettings()
        {
            return new
            {
                productName = PlayerSettings.productName,
                companyName = PlayerSettings.companyName,
                version = PlayerSettings.bundleVersion,
                defaultIcon = PlayerSettings.defaultIcon != null ? AssetDatabase.GetAssetPath(PlayerSettings.defaultIcon) : null,
                colorSpace = PlayerSettings.colorSpace.ToString(),
                apiCompatibilityLevel = PlayerSettings.GetApiCompatibilityLevel(EditorUserBuildSettings.selectedBuildTargetGroup).ToString()
            };
        }
        
        private static object GetPackageInfo()
        {
            var packages = new List<object>();
            
            try
            {
                var manifestPath = Path.Combine(Application.dataPath, "../Packages/manifest.json");
                if (File.Exists(manifestPath))
                {
                    var manifestContent = File.ReadAllText(manifestPath);
                    // Simple JSON parsing for dependencies
                    var lines = manifestContent.Split('\n');
                    foreach (var line in lines)
                    {
                        if (line.Trim().StartsWith('"') && line.Contains(':'))
                        {
                            var parts = line.Split(':');
                            if (parts.Length >= 2)
                            {
                                var packageName = parts[0].Trim().Trim('"', ',');
                                var version = parts[1].Trim().Trim('"', ',');
                                if (!string.IsNullOrEmpty(packageName) && !string.IsNullOrEmpty(version))
                                {
                                    packages.Add(new { name = packageName, version = version });
                                }
                            }
                        }
                    }
                }
            }
            catch (Exception e)
            {
                LogMCP($"Failed to read package manifest: {e.Message}");
            }
            
            return packages;
        }
        
        private static void LogMCP(string message)
        {
            UnityMCPBridge.LogMCP($"[ProjectScanner] {message}");
        }
    }
    
    /// <summary>
    /// Build automation functionality
    /// </summary>
    public static class BuildAutomation
    {
        /// <summary>
        /// Execute build with specified parameters
        /// </summary>
        public static void ExecuteBuild(string targetPlatform, string buildOptions, string outputPath)
        {
            try
            {
                LogMCP($"Starting build for platform: {targetPlatform}");
                
                // Parse build target
                if (!Enum.TryParse<BuildTarget>(targetPlatform, out var buildTarget))
                {
                    throw new ArgumentException($"Invalid build target: {targetPlatform}");
                }
                
                // Parse build options
                var options = BuildOptions.None;
                if (!string.IsNullOrEmpty(buildOptions) && buildOptions != "None")
                {
                    if (Enum.TryParse<BuildOptions>(buildOptions, out var parsedOptions))
                    {
                        options = parsedOptions;
                    }
                }
                
                // Set up build player options
                var buildPlayerOptions = new BuildPlayerOptions
                {
                    scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray(),
                    locationPathName = outputPath,
                    target = buildTarget,
                    options = options
                };
                
                // Execute build
                var report = BuildPipeline.BuildPlayer(buildPlayerOptions);
                
                var buildResult = new
                {
                    result = report.summary.result.ToString(),
                    totalTime = report.summary.totalTime.TotalSeconds,
                    totalSize = report.summary.totalSize,
                    outputPath = report.summary.outputPath,
                    platform = report.summary.platform.ToString(),
                    errors = report.steps.SelectMany(s => s.messages.Where(m => m.type == LogType.Error).Select(m => m.content)).ToArray(),
                    warnings = report.steps.SelectMany(s => s.messages.Where(m => m.type == LogType.Warning).Select(m => m.content)).ToArray()
                };
                
                UnityMCPBridge.WriteResult("build_run", buildResult);
                LogMCP($"Build completed with result: {report.summary.result}");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("build_run", e.Message);
                LogMCP($"Build failed: {e.Message}");
            }
        }
        
        private static void LogMCP(string message)
        {
            UnityMCPBridge.LogMCP($"[BuildAutomation] {message}");
        }
    }
    
    /// <summary>
    /// Test execution functionality
    /// </summary>
    public static class TestRunner
    {
        /// <summary>
        /// Run play mode tests
        /// </summary>
        public static void RunPlayModeTests()
        {
            try
            {
                LogMCP("Starting play mode tests...");
                
                // This would integrate with Unity Test Runner
                // For now, we'll create a placeholder result
                var testResult = new
                {
                    testMode = "PlayMode",
                    totalTests = 0,
                    passedTests = 0,
                    failedTests = 0,
                    skippedTests = 0,
                    executionTime = 0.0,
                    message = "Test runner integration not fully implemented. Use Unity Test Runner window for detailed testing."
                };
                
                UnityMCPBridge.WriteResult("test_playmode", testResult);
                LogMCP("Play mode test execution completed");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("test_playmode", e.Message);
                LogMCP($"Play mode tests failed: {e.Message}");
            }
        }
        
        /// <summary>
        /// Run edit mode tests
        /// </summary>
        public static void RunEditModeTests()
        {
            try
            {
                LogMCP("Starting edit mode tests...");
                
                // This would integrate with Unity Test Runner
                // For now, we'll create a placeholder result
                var testResult = new
                {
                    testMode = "EditMode",
                    totalTests = 0,
                    passedTests = 0,
                    failedTests = 0,
                    skippedTests = 0,
                    executionTime = 0.0,
                    message = "Test runner integration not fully implemented. Use Unity Test Runner window for detailed testing."
                };
                
                UnityMCPBridge.WriteResult("test_editmode", testResult);
                LogMCP("Edit mode test execution completed");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("test_editmode", e.Message);
                LogMCP($"Edit mode tests failed: {e.Message}");
            }
        }
        
        private static void LogMCP(string message)
        {
            UnityMCPBridge.LogMCP($"[TestRunner] {message}");
        }
    }
    
    /// <summary>
    /// Scene validation functionality
    /// </summary>
    public static class SceneValidator
    {
        /// <summary>
        /// Validate current scene for common issues
        /// </summary>
        public static void ValidateScene()
        {
            try
            {
                LogMCP("Starting scene validation...");
                
                var scene = SceneManager.GetActiveScene();
                var issues = new List<object>();
                var warnings = new List<object>();
                var info = new List<object>();
                
                // Check for missing references
                var allObjects = scene.GetRootGameObjects();
                foreach (var rootObj in allObjects)
                {
                    CheckGameObjectRecursively(rootObj, issues, warnings, info);
                }
                
                // Check scene settings
                CheckSceneSettings(scene, issues, warnings, info);
                
                var validationResult = new
                {
                    sceneName = scene.name,
                    scenePath = scene.path,
                    totalGameObjects = GetTotalGameObjectCount(allObjects),
                    issues = issues,
                    warnings = warnings,
                    info = info,
                    isValid = issues.Count == 0
                };
                
                UnityMCPBridge.WriteResult("scene_validate", validationResult);
                LogMCP($"Scene validation completed. Found {issues.Count} issues, {warnings.Count} warnings");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("scene_validate", e.Message);
                LogMCP($"Scene validation failed: {e.Message}");
            }
        }
        
        private static void CheckGameObjectRecursively(GameObject obj, List<object> issues, List<object> warnings, List<object> info)
        {
            // Check for missing components
            var components = obj.GetComponents<Component>();
            for (int i = 0; i < components.Length; i++)
            {
                if (components[i] == null)
                {
                    issues.Add(new
                    {
                        type = "MissingComponent",
                        gameObject = GetGameObjectPath(obj),
                        message = "Missing component detected"
                    });
                }
            }
            
            // Check for missing references in MonoBehaviours
            var monoBehaviours = obj.GetComponents<MonoBehaviour>();
            foreach (var mb in monoBehaviours)
            {
                if (mb != null)
                {
                    CheckMonoBehaviourReferences(mb, obj, issues, warnings);
                }
            }
            
            // Check children recursively
            for (int i = 0; i < obj.transform.childCount; i++)
            {
                CheckGameObjectRecursively(obj.transform.GetChild(i).gameObject, issues, warnings, info);
            }
        }
        
        private static void CheckMonoBehaviourReferences(MonoBehaviour mb, GameObject obj, List<object> issues, List<object> warnings)
        {
            var type = mb.GetType();
            var fields = type.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
            
            foreach (var field in fields)
            {
                if (field.GetCustomAttribute<SerializeField>() != null || field.IsPublic)
                {
                    if (typeof(UnityEngine.Object).IsAssignableFrom(field.FieldType))
                    {
                        var value = field.GetValue(mb);
                        if (value == null || value.Equals(null))
                        {
                            warnings.Add(new
                            {
                                type = "MissingReference",
                                gameObject = GetGameObjectPath(obj),
                                component = type.Name,
                                field = field.Name,
                                message = $"Missing reference in {type.Name}.{field.Name}"
                            });
                        }
                    }
                }
            }
        }
        
        private static void CheckSceneSettings(Scene scene, List<object> issues, List<object> warnings, List<object> info)
        {
            // Check if scene is in build settings
            var sceneInBuild = EditorBuildSettings.scenes.Any(s => s.path == scene.path);
            if (!sceneInBuild)
            {
                warnings.Add(new
                {
                    type = "SceneNotInBuild",
                    message = "Scene is not added to build settings"
                });
            }
            
            // Add scene info
            info.Add(new
            {
                type = "SceneInfo",
                message = $"Scene '{scene.name}' loaded and validated"
            });
        }
        
        private static string GetGameObjectPath(GameObject obj)
        {
            var path = obj.name;
            var parent = obj.transform.parent;
            while (parent != null)
            {
                path = parent.name + "/" + path;
                parent = parent.parent;
            }
            return path;
        }
        
        private static int GetTotalGameObjectCount(GameObject[] rootObjects)
        {
            int count = 0;
            foreach (var root in rootObjects)
            {
                count += CountGameObjectsRecursively(root);
            }
            return count;
        }
        
        private static int CountGameObjectsRecursively(GameObject obj)
        {
            int count = 1; // Count this object
            for (int i = 0; i < obj.transform.childCount; i++)
            {
                count += CountGameObjectsRecursively(obj.transform.GetChild(i).gameObject);
            }
            return count;
        }
        
        private static void LogMCP(string message)
        {
            UnityMCPBridge.LogMCP($"[SceneValidator] {message}");
        }
    }
    
    /// <summary>
    /// Command line interface for MCP operations
    /// </summary>
    public static class MCPCommandLine
    {
        /// <summary>
        /// Process command line arguments for MCP operations
        /// </summary>
        public static void ProcessMCPCommand()
        {
            var args = Environment.GetCommandLineArgs();
            
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "-mcpCommand" && i + 1 < args.Length)
                {
                    var command = args[i + 1];
                    ExecuteMCPCommand(command, args.Skip(i + 2).ToArray());
                    break;
                }
            }
        }
        
        private static void ExecuteMCPCommand(string command, string[] parameters)
        {
            try
            {
                UnityMCPBridge.LogMCP($"Executing MCP command: {command}");
                
                switch (command.ToLower())
                {
                    case "scan":
                        ProjectScanner.ScanProject();
                        break;
                        
                    case "build":
                        if (parameters.Length >= 3)
                        {
                            BuildAutomation.ExecuteBuild(parameters[0], parameters[1], parameters[2]);
                        }
                        else
                        {
                            throw new ArgumentException("Build command requires platform, options, and output path");
                        }
                        break;
                        
                    case "test-playmode":
                        TestRunner.RunPlayModeTests();
                        break;
                        
                    case "test-editmode":
                        TestRunner.RunEditModeTests();
                        break;
                        
                    case "validate-scene":
                        SceneValidator.ValidateScene();
                        break;
                        
                    default:
                        throw new ArgumentException($"Unknown MCP command: {command}");
                }
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError($"command_{command}", e.Message);
                UnityMCPBridge.LogMCP($"MCP command failed: {e.Message}");
            }
        }
        
        /// <summary>
        /// Initialize command line processing
        /// </summary>
        [InitializeOnLoadMethod]
        private static void InitializeCommandLine()
        {
            EditorApplication.delayCall += ProcessMCPCommand;
        }
    }
}