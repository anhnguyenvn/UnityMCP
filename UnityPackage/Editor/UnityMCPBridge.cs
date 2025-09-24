/*
 * Unity MCP Bridge - Package Version
 * 
 * Enhanced version of the Unity MCP Bridge integrated into the Unity Package.
 * Provides seamless communication between Unity Editor and MCP servers.
 * 
 * Features:
 * - Automatic initialization through package system
 * - Enhanced error handling and logging
 * - Integration with Unity MCP Runtime
 * - Improved project analysis and automation tools
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
using UnityMCP.Runtime;

namespace UnityMCP.Editor
{
    /// <summary>
    /// Main Unity MCP Bridge class for handling MCP server communication
    /// Enhanced package version with improved functionality
    /// </summary>
    public static class UnityMCPBridge
    {
        private const string MCP_OUTPUT_DIR = "Temp/MCP";
        private const string MCP_LOG_FILE = "Temp/MCP/mcp_unity.log";
        private const string PACKAGE_NAME = "com.unitymcp.bridge";
        
        // Package-specific settings
        private static bool _isInitialized = false;
        private static string _packagePath = "";
        
        /// <summary>
        /// Initialize MCP bridge when package loads
        /// </summary>
        [InitializeOnLoadMethod]
        private static void Initialize()
        {
            if (_isInitialized) return;
            
            try
            {
                // Find package path
                _packagePath = GetPackagePath();
                
                // Create MCP output directory
                if (!Directory.Exists(MCP_OUTPUT_DIR))
                {
                    Directory.CreateDirectory(MCP_OUTPUT_DIR);
                }
                
                // Initialize package-specific settings
                InitializePackageSettings();
                
                _isInitialized = true;
                LogMCP($"Unity MCP Bridge Package initialized (v{GetPackageVersion()})");
                LogMCP($"Package path: {_packagePath}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[Unity MCP Bridge] Initialization failed: {e.Message}");
            }
        }
        
        /// <summary>
        /// Get the package installation path
        /// </summary>
        private static string GetPackagePath()
        {
            var packageInfo = UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UnityMCPBridge).Assembly);
            return packageInfo?.assetPath ?? "Packages/com.unitymcp.bridge";
        }
        
        /// <summary>
        /// Get package version
        /// </summary>
        private static string GetPackageVersion()
        {
            var packageInfo = UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UnityMCPBridge).Assembly);
            return packageInfo?.version ?? "1.0.0";
        }
        
        /// <summary>
        /// Initialize package-specific settings
        /// </summary>
        private static void InitializePackageSettings()
        {
            // Auto-detect Unity Editor path
            var editorPath = EditorApplication.applicationPath;
            LogMCP($"Unity Editor detected at: {editorPath}");
            
            // Check for MCP Runtime component
            var runtimeInstance = UnityMCPRuntime.Instance;
            if (runtimeInstance != null)
            {
                LogMCP("Unity MCP Runtime component found and connected");
            }
            else
            {
                LogMCP("Unity MCP Runtime component not found - runtime features will be limited");
            }
        }
        
        /// <summary>
        /// Enhanced logging with package context
        /// </summary>
        private static void LogMCP(string message)
        {
            try
            {
                var logEntry = $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] [Unity MCP Bridge] {message}";
                File.AppendAllText(MCP_LOG_FILE, logEntry + Environment.NewLine);
                Debug.Log($"[Unity MCP Bridge] {message}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[Unity MCP Bridge] Failed to write log: {e.Message}");
            }
        }
        
        /// <summary>
        /// Write result data to JSON file for MCP server consumption
        /// Enhanced with package metadata
        /// </summary>
        public static void WriteResult(string operation, object data)
        {
            try
            {
                var result = new
                {
                    operation = operation,
                    timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                    success = true,
                    packageVersion = GetPackageVersion(),
                    unityVersion = Application.unityVersion,
                    data = data
                };
                
                var json = JsonUtility.ToJson(result, true);
                var outputFile = Path.Combine(MCP_OUTPUT_DIR, $"{operation}_result.json");
                File.WriteAllText(outputFile, json);
                
                LogMCP($"Result written for operation: {operation}");
                
                // Notify runtime if available
                if (UnityMCPRuntime.Instance != null)
                {
                    UnityMCPRuntime.SendMCPMessage($"Operation completed: {operation}");
                }
            }
            catch (Exception e)
            {
                WriteError(operation, e.Message);
            }
        }
        
        /// <summary>
        /// Write error result to JSON file
        /// Enhanced with package context
        /// </summary>
        public static void WriteError(string operation, string error)
        {
            try
            {
                var result = new
                {
                    operation = operation,
                    timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                    success = false,
                    packageVersion = GetPackageVersion(),
                    unityVersion = Application.unityVersion,
                    error = error
                };
                
                var json = JsonUtility.ToJson(result, true);
                var outputFile = Path.Combine(MCP_OUTPUT_DIR, $"{operation}_error.json");
                File.WriteAllText(outputFile, json);
                
                LogMCP($"Error written for operation: {operation} - {error}");
                Debug.LogError($"[Unity MCP Bridge] Operation failed: {operation} - {error}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[Unity MCP Bridge] Failed to write error: {e.Message}");
            }
        }
        
        /// <summary>
        /// Get Unity Editor executable path
        /// Enhanced auto-detection
        /// </summary>
        public static string GetUnityEditorPath()
        {
            return EditorApplication.applicationPath;
        }
        
        /// <summary>
        /// Get current project path
        /// </summary>
        public static string GetProjectPath()
        {
            return Directory.GetCurrentDirectory();
        }
        
        /// <summary>
        /// Validate if current directory is a Unity project
        /// </summary>
        public static bool IsValidUnityProject(string path = null)
        {
            var projectPath = path ?? GetProjectPath();
            return Directory.Exists(Path.Combine(projectPath, "Assets")) &&
                   Directory.Exists(Path.Combine(projectPath, "ProjectSettings"));
        }
        
        /// <summary>
        /// Get comprehensive project information
        /// Enhanced with package-specific data
        /// </summary>
        public static ProjectInfo GetProjectInfo()
        {
            var projectInfo = new ProjectInfo();
            
            // Add package-specific information
            var packageInfo = UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UnityMCPBridge).Assembly);
            if (packageInfo != null)
            {
                // This would be added to ProjectInfo if we extend it
                LogMCP($"Package info: {packageInfo.displayName} v{packageInfo.version}");
            }
            
            return projectInfo;
        }
        
        /// <summary>
        /// Menu item for manual project scan
        /// </summary>
        [MenuItem("Window/Unity MCP/Scan Project")]
        public static void ScanProject()
        {
            try
            {
                LogMCP("Starting enhanced project scan...");
                
                var projectInfo = GetProjectInfo();
                var sceneInfo = GetSceneInfo();
                var assetInfo = GetAssetInfo();
                var scriptInfo = GetScriptInfo();
                var buildSettings = GetBuildSettings();
                var packageInfo = GetInstalledPackages();
                
                var scanResult = new
                {
                    project = projectInfo,
                    scenes = sceneInfo,
                    assets = assetInfo,
                    scripts = scriptInfo,
                    buildSettings = buildSettings,
                    packages = packageInfo,
                    mcpBridgeVersion = GetPackageVersion(),
                    scanTime = DateTime.Now
                };
                
                WriteResult("project_scan", scanResult);
                LogMCP("Enhanced project scan completed successfully");
                
                // Show completion dialog
                EditorUtility.DisplayDialog("Unity MCP Bridge", 
                    "Project scan completed successfully!\nResults saved to Temp/MCP/project_scan_result.json", 
                    "OK");
            }
            catch (Exception e)
            {
                WriteError("project_scan", e.Message);
                LogMCP($"Project scan failed: {e.Message}");
                
                EditorUtility.DisplayDialog("Unity MCP Bridge", 
                    $"Project scan failed: {e.Message}", 
                    "OK");
            }
        }
        
        // Helper methods (simplified versions - full implementation would be more comprehensive)
        
        private static object GetSceneInfo()
        {
            var scenes = new List<object>();
            
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
            var assetCount = assetGuids.Length;
            
            return new
            {
                totalAssets = assetCount,
                lastRefresh = DateTime.Now
            };
        }
        
        private static object GetScriptInfo()
        {
            var scriptGuids = AssetDatabase.FindAssets("t:MonoScript");
            
            return new
            {
                totalScripts = scriptGuids.Length,
                lastCompile = DateTime.Now
            };
        }
        
        private static object GetBuildSettings()
        {
            return new
            {
                target = EditorUserBuildSettings.activeBuildTarget.ToString(),
                developmentBuild = EditorUserBuildSettings.development,
                autoConnectProfiler = EditorUserBuildSettings.connectProfiler
            };
        }
        
        private static object GetInstalledPackages()
        {
            // This would require async package manager calls in a real implementation
            return new
            {
                mcpBridgeInstalled = true,
                mcpBridgeVersion = GetPackageVersion()
            };
        }
    }
}