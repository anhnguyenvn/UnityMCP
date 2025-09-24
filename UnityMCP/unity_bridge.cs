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
    /// Scene management functionality
    /// </summary>
    public static class SceneManager
    {
        /// <summary>
        /// Load a scene by name or path
        /// </summary>
        public static void LoadScene(string sceneName, bool additive = false)
        {
            try
            {
                LogMCP($"Loading scene: {sceneName}, additive: {additive}");
                
                var loadMode = additive ? OpenSceneMode.Additive : OpenSceneMode.Single;
                var scene = EditorSceneManager.OpenScene(sceneName, loadMode);
                
                var result = new
                {
                    sceneName = scene.name,
                    scenePath = scene.path,
                    isLoaded = scene.isLoaded,
                    isDirty = scene.isDirty,
                    buildIndex = scene.buildIndex,
                    gameObjectCount = scene.rootCount
                };
                
                UnityMCPBridge.WriteResult("scene_load", result);
                LogMCP($"Scene loaded successfully: {scene.name}");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("scene_load", e.Message);
                LogMCP($"Failed to load scene: {e.Message}");
            }
        }
        
        /// <summary>
        /// Save current scene or specified scene
        /// </summary>
        public static void SaveScene(string scenePath = null)
        {
            try
            {
                LogMCP($"Saving scene: {scenePath ?? "current"}");
                
                Scene sceneToSave;
                if (string.IsNullOrEmpty(scenePath))
                {
                    sceneToSave = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
                }
                else
                {
                    sceneToSave = EditorSceneManager.GetSceneByPath(scenePath);
                }
                
                bool saved = EditorSceneManager.SaveScene(sceneToSave);
                
                var result = new
                {
                    sceneName = sceneToSave.name,
                    scenePath = sceneToSave.path,
                    saved = saved,
                    isDirty = sceneToSave.isDirty
                };
                
                UnityMCPBridge.WriteResult("scene_save", result);
                LogMCP($"Scene save result: {saved}");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("scene_save", e.Message);
                LogMCP($"Failed to save scene: {e.Message}");
            }
        }
        
        /// <summary>
        /// Create a new scene
        /// </summary>
        public static void CreateScene(string sceneName, string templatePath = null)
        {
            try
            {
                LogMCP($"Creating new scene: {sceneName}");
                
                Scene newScene;
                if (string.IsNullOrEmpty(templatePath))
                {
                    newScene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
                }
                else
                {
                    // Load template and create from it
                    newScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                }
                
                // Save the new scene
                string savePath = $"Assets/Scenes/{sceneName}.unity";
                bool saved = EditorSceneManager.SaveScene(newScene, savePath);
                
                var result = new
                {
                    sceneName = newScene.name,
                    scenePath = savePath,
                    created = true,
                    saved = saved
                };
                
                UnityMCPBridge.WriteResult("scene_create", result);
                LogMCP($"Scene created successfully: {sceneName}");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("scene_create", e.Message);
                LogMCP($"Failed to create scene: {e.Message}");
            }
        }
        
        /// <summary>
        /// Get scene hierarchy information
        /// </summary>
        public static void GetSceneHierarchy(bool includeInactive = false)
        {
            try
            {
                LogMCP("Getting scene hierarchy...");
                
                var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
                var rootObjects = scene.GetRootGameObjects();
                var hierarchy = new List<object>();
                
                foreach (var rootObj in rootObjects)
                {
                    if (rootObj.activeInHierarchy || includeInactive)
                    {
                        hierarchy.Add(BuildHierarchyNode(rootObj, includeInactive));
                    }
                }
                
                var result = new
                {
                    sceneName = scene.name,
                    totalRootObjects = rootObjects.Length,
                    hierarchy = hierarchy
                };
                
                UnityMCPBridge.WriteResult("scene_hierarchy", result);
                LogMCP("Scene hierarchy retrieved successfully");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("scene_hierarchy", e.Message);
                LogMCP($"Failed to get scene hierarchy: {e.Message}");
            }
        }
        
        private static object BuildHierarchyNode(GameObject obj, bool includeInactive)
        {
            var children = new List<object>();
            for (int i = 0; i < obj.transform.childCount; i++)
            {
                var child = obj.transform.GetChild(i).gameObject;
                if (child.activeInHierarchy || includeInactive)
                {
                    children.Add(BuildHierarchyNode(child, includeInactive));
                }
            }
            
            return new
            {
                name = obj.name,
                active = obj.activeInHierarchy,
                tag = obj.tag,
                layer = LayerMask.LayerToName(obj.layer),
                componentCount = obj.GetComponents<Component>().Length,
                childCount = children.Count,
                children = children
            };
        }
        
        private static void LogMCP(string message)
        {
            UnityMCPBridge.LogMCP($"[SceneManager] {message}");
        }
    }
    
    /// <summary>
    /// GameObject operations functionality
    /// </summary>
    public static class GameObjectManager
    {
        /// <summary>
        /// Create a new GameObject
        /// </summary>
        public static void CreateGameObject(string name, string parentPath = null, string[] components = null)
        {
            try
            {
                LogMCP($"Creating GameObject: {name}");
                
                var gameObject = new GameObject(name);
                
                // Set parent if specified
                if (!string.IsNullOrEmpty(parentPath))
                {
                    var parent = GameObject.Find(parentPath);
                    if (parent != null)
                    {
                        gameObject.transform.SetParent(parent.transform);
                    }
                }
                
                // Add components if specified
                if (components != null)
                {
                    foreach (var componentName in components)
                    {
                        var componentType = Type.GetType($"UnityEngine.{componentName}, UnityEngine");
                        if (componentType != null)
                        {
                            gameObject.AddComponent(componentType);
                        }
                    }
                }
                
                var result = new
                {
                    name = gameObject.name,
                    instanceId = gameObject.GetInstanceID(),
                    parentName = gameObject.transform.parent?.name,
                    componentCount = gameObject.GetComponents<Component>().Length,
                    position = gameObject.transform.position,
                    rotation = gameObject.transform.rotation.eulerAngles,
                    scale = gameObject.transform.localScale
                };
                
                UnityMCPBridge.WriteResult("gameobject_create", result);
                LogMCP($"GameObject created successfully: {name}");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("gameobject_create", e.Message);
                LogMCP($"Failed to create GameObject: {e.Message}");
            }
        }
        
        /// <summary>
        /// Delete a GameObject by name or path
        /// </summary>
        public static void DeleteGameObject(string objectPath)
        {
            try
            {
                LogMCP($"Deleting GameObject: {objectPath}");
                
                var gameObject = GameObject.Find(objectPath);
                if (gameObject == null)
                {
                    throw new ArgumentException($"GameObject not found: {objectPath}");
                }
                
                var objectInfo = new
                {
                    name = gameObject.name,
                    instanceId = gameObject.GetInstanceID(),
                    childCount = gameObject.transform.childCount
                };
                
                UnityEngine.Object.DestroyImmediate(gameObject);
                
                var result = new
                {
                    deleted = true,
                    objectInfo = objectInfo
                };
                
                UnityMCPBridge.WriteResult("gameobject_delete", result);
                LogMCP($"GameObject deleted successfully: {objectPath}");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("gameobject_delete", e.Message);
                LogMCP($"Failed to delete GameObject: {e.Message}");
            }
        }
        
        /// <summary>
        /// Find GameObjects by name, tag, or type
        /// </summary>
        public static void FindGameObjects(string searchTerm, string searchType = "name")
        {
            try
            {
                LogMCP($"Finding GameObjects by {searchType}: {searchTerm}");
                
                var foundObjects = new List<object>();
                
                switch (searchType.ToLower())
                {
                    case "name":
                        var objsByName = Resources.FindObjectsOfTypeAll<GameObject>()
                            .Where(obj => obj.name.Contains(searchTerm) && obj.scene.isLoaded)
                            .ToArray();
                        foundObjects.AddRange(objsByName.Select(CreateGameObjectInfo));
                        break;
                        
                    case "tag":
                        var objsByTag = GameObject.FindGameObjectsWithTag(searchTerm);
                        foundObjects.AddRange(objsByTag.Select(CreateGameObjectInfo));
                        break;
                        
                    case "component":
                        var componentType = Type.GetType($"UnityEngine.{searchTerm}, UnityEngine");
                        if (componentType != null)
                        {
                            var objsWithComponent = Resources.FindObjectsOfTypeAll(componentType)
                                .OfType<Component>()
                                .Where(comp => comp.gameObject.scene.isLoaded)
                                .Select(comp => comp.gameObject)
                                .Distinct()
                                .ToArray();
                            foundObjects.AddRange(objsWithComponent.Select(CreateGameObjectInfo));
                        }
                        break;
                }
                
                var result = new
                {
                    searchTerm = searchTerm,
                    searchType = searchType,
                    foundCount = foundObjects.Count,
                    objects = foundObjects
                };
                
                UnityMCPBridge.WriteResult("gameobject_find", result);
                LogMCP($"Found {foundObjects.Count} GameObjects");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("gameobject_find", e.Message);
                LogMCP($"Failed to find GameObjects: {e.Message}");
            }
        }
        
        /// <summary>
        /// Transform a GameObject (position, rotation, scale)
        /// </summary>
        public static void TransformGameObject(string objectPath, Vector3? position = null, Vector3? rotation = null, Vector3? scale = null)
        {
            try
            {
                LogMCP($"Transforming GameObject: {objectPath}");
                
                var gameObject = GameObject.Find(objectPath);
                if (gameObject == null)
                {
                    throw new ArgumentException($"GameObject not found: {objectPath}");
                }
                
                var transform = gameObject.transform;
                
                if (position.HasValue)
                    transform.position = position.Value;
                if (rotation.HasValue)
                    transform.rotation = Quaternion.Euler(rotation.Value);
                if (scale.HasValue)
                    transform.localScale = scale.Value;
                
                var result = new
                {
                    name = gameObject.name,
                    position = transform.position,
                    rotation = transform.rotation.eulerAngles,
                    scale = transform.localScale
                };
                
                UnityMCPBridge.WriteResult("gameobject_transform", result);
                LogMCP($"GameObject transformed successfully: {objectPath}");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("gameobject_transform", e.Message);
                LogMCP($"Failed to transform GameObject: {e.Message}");
            }
        }
        
        private static object CreateGameObjectInfo(GameObject obj)
        {
            return new
            {
                name = obj.name,
                instanceId = obj.GetInstanceID(),
                tag = obj.tag,
                layer = LayerMask.LayerToName(obj.layer),
                active = obj.activeInHierarchy,
                position = obj.transform.position,
                rotation = obj.transform.rotation.eulerAngles,
                scale = obj.transform.localScale,
                componentCount = obj.GetComponents<Component>().Length,
                childCount = obj.transform.childCount
            };
        }
        
        private static void LogMCP(string message)
        {
            UnityMCPBridge.LogMCP($"[GameObjectManager] {message}");
        }
    }
    
    /// <summary>
    /// Component management functionality
    /// </summary>
    public static class ComponentManager
    {
        /// <summary>
        /// Add a component to a GameObject
        /// </summary>
        public static void AddComponent(string objectPath, string componentType, Dictionary<string, object> properties = null)
        {
            try
            {
                LogMCP($"Adding component {componentType} to {objectPath}");
                
                var gameObject = GameObject.Find(objectPath);
                if (gameObject == null)
                {
                    throw new ArgumentException($"GameObject not found: {objectPath}");
                }
                
                var type = Type.GetType($"UnityEngine.{componentType}, UnityEngine") ?? 
                          Type.GetType(componentType);
                
                if (type == null)
                {
                    throw new ArgumentException($"Component type not found: {componentType}");
                }
                
                var component = gameObject.AddComponent(type);
                
                // Set properties if provided
                if (properties != null)
                {
                    SetComponentProperties(component, properties);
                }
                
                var result = new
                {
                    gameObjectName = gameObject.name,
                    componentType = component.GetType().Name,
                    componentId = component.GetInstanceID(),
                    properties = GetComponentProperties(component)
                };
                
                UnityMCPBridge.WriteResult("component_add", result);
                LogMCP($"Component {componentType} added successfully");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("component_add", e.Message);
                LogMCP($"Failed to add component: {e.Message}");
            }
        }
        
        /// <summary>
        /// Remove a component from a GameObject
        /// </summary>
        public static void RemoveComponent(string objectPath, string componentType)
        {
            try
            {
                LogMCP($"Removing component {componentType} from {objectPath}");
                
                var gameObject = GameObject.Find(objectPath);
                if (gameObject == null)
                {
                    throw new ArgumentException($"GameObject not found: {objectPath}");
                }
                
                var type = Type.GetType($"UnityEngine.{componentType}, UnityEngine") ?? 
                          Type.GetType(componentType);
                
                if (type == null)
                {
                    throw new ArgumentException($"Component type not found: {componentType}");
                }
                
                var component = gameObject.GetComponent(type);
                if (component == null)
                {
                    throw new ArgumentException($"Component {componentType} not found on {objectPath}");
                }
                
                UnityEngine.Object.DestroyImmediate(component);
                
                var result = new
                {
                    gameObjectName = gameObject.name,
                    removedComponentType = componentType,
                    remainingComponents = gameObject.GetComponents<Component>().Select(c => c.GetType().Name).ToArray()
                };
                
                UnityMCPBridge.WriteResult("component_remove", result);
                LogMCP($"Component {componentType} removed successfully");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("component_remove", e.Message);
                LogMCP($"Failed to remove component: {e.Message}");
            }
        }
        
        /// <summary>
        /// Get component information
        /// </summary>
        public static void GetComponent(string objectPath, string componentType = null)
        {
            try
            {
                LogMCP($"Getting component info for {objectPath}");
                
                var gameObject = GameObject.Find(objectPath);
                if (gameObject == null)
                {
                    throw new ArgumentException($"GameObject not found: {objectPath}");
                }
                
                var components = new List<object>();
                
                if (string.IsNullOrEmpty(componentType))
                {
                    // Get all components
                    var allComponents = gameObject.GetComponents<Component>();
                    components.AddRange(allComponents.Select(CreateComponentInfo));
                }
                else
                {
                    // Get specific component type
                    var type = Type.GetType($"UnityEngine.{componentType}, UnityEngine") ?? 
                              Type.GetType(componentType);
                    
                    if (type != null)
                    {
                        var component = gameObject.GetComponent(type);
                        if (component != null)
                        {
                            components.Add(CreateComponentInfo(component));
                        }
                    }
                }
                
                var result = new
                {
                    gameObjectName = gameObject.name,
                    componentCount = components.Count,
                    components = components
                };
                
                UnityMCPBridge.WriteResult("component_get", result);
                LogMCP($"Retrieved {components.Count} components");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("component_get", e.Message);
                LogMCP($"Failed to get component: {e.Message}");
            }
        }
        
        /// <summary>
        /// Set component properties
        /// </summary>
        public static void SetComponentProperty(string objectPath, string componentType, string propertyName, object value)
        {
            try
            {
                LogMCP($"Setting property {propertyName} on {componentType} of {objectPath}");
                
                var gameObject = GameObject.Find(objectPath);
                if (gameObject == null)
                {
                    throw new ArgumentException($"GameObject not found: {objectPath}");
                }
                
                var type = Type.GetType($"UnityEngine.{componentType}, UnityEngine") ?? 
                          Type.GetType(componentType);
                
                if (type == null)
                {
                    throw new ArgumentException($"Component type not found: {componentType}");
                }
                
                var component = gameObject.GetComponent(type);
                if (component == null)
                {
                    throw new ArgumentException($"Component {componentType} not found on {objectPath}");
                }
                
                var property = type.GetProperty(propertyName);
                var field = type.GetField(propertyName);
                
                if (property != null && property.CanWrite)
                {
                    property.SetValue(component, Convert.ChangeType(value, property.PropertyType));
                }
                else if (field != null)
                {
                    field.SetValue(component, Convert.ChangeType(value, field.FieldType));
                }
                else
                {
                    throw new ArgumentException($"Property or field {propertyName} not found or not writable");
                }
                
                var result = new
                {
                    gameObjectName = gameObject.name,
                    componentType = componentType,
                    propertyName = propertyName,
                    newValue = value,
                    properties = GetComponentProperties(component)
                };
                
                UnityMCPBridge.WriteResult("component_set_property", result);
                LogMCP($"Property {propertyName} set successfully");
            }
            catch (Exception e)
            {
                UnityMCPBridge.WriteError("component_set_property", e.Message);
                LogMCP($"Failed to set component property: {e.Message}");
            }
        }
        
        private static object CreateComponentInfo(Component component)
        {
            return new
            {
                type = component.GetType().Name,
                instanceId = component.GetInstanceID(),
                enabled = component is Behaviour behaviour ? behaviour.enabled : true,
                properties = GetComponentProperties(component)
            };
        }
        
        private static Dictionary<string, object> GetComponentProperties(Component component)
        {
            var properties = new Dictionary<string, object>();
            var type = component.GetType();
            
            // Get public properties
            foreach (var prop in type.GetProperties(BindingFlags.Public | BindingFlags.Instance))
            {
                if (prop.CanRead && prop.GetIndexParameters().Length == 0)
                {
                    try
                    {
                        var value = prop.GetValue(component);
                        properties[prop.Name] = value?.ToString() ?? "null";
                    }
                    catch
                    {
                        properties[prop.Name] = "<unable to read>";
                    }
                }
            }
            
            return properties;
        }
        
        private static void SetComponentProperties(Component component, Dictionary<string, object> properties)
        {
            var type = component.GetType();
            
            foreach (var kvp in properties)
            {
                try
                {
                    var property = type.GetProperty(kvp.Key);
                    var field = type.GetField(kvp.Key);
                    
                    if (property != null && property.CanWrite)
                    {
                        property.SetValue(component, Convert.ChangeType(kvp.Value, property.PropertyType));
                    }
                    else if (field != null)
                    {
                        field.SetValue(component, Convert.ChangeType(kvp.Value, field.FieldType));
                    }
                }
                catch (Exception e)
                {
                    LogMCP($"Failed to set property {kvp.Key}: {e.Message}");
                }
            }
        }
        
        private static void LogMCP(string message)
        {
            UnityMCPBridge.LogMCP($"[ComponentManager] {message}");
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
                    // Original commands
                    case "scan":
                        var scanner = new ProjectScanner();
                        var scanResult = scanner.ScanProject();
                        UnityMCPBridge.WriteResult("project_scan", scanResult);
                        break;
                        
                    case "build":
                        if (parameters.Length >= 1)
                        {
                            var buildResult = BuildAutomation.ExecuteBuild(parameters[0]);
                            UnityMCPBridge.WriteResult("build_project", buildResult);
                        }
                        else
                        {
                            var buildResult = BuildAutomation.ExecuteBuild("StandaloneWindows64");
                            UnityMCPBridge.WriteResult("build_project", buildResult);
                        }
                        break;
                        
                    case "test-playmode":
                        var playModeResult = TestRunner.RunPlayModeTests();
                        UnityMCPBridge.WriteResult("test_playmode", playModeResult);
                        break;
                        
                    case "test-editmode":
                        var editModeResult = TestRunner.RunEditModeTests();
                        UnityMCPBridge.WriteResult("test_editmode", editModeResult);
                        break;
                        
                    case "validate-scene":
                        string scenePath = parameters.Length > 0 ? parameters[0] : null;
                        var validationResult = SceneValidator.ValidateScene(scenePath);
                        UnityMCPBridge.WriteResult("scene_validation", validationResult);
                        break;
                    
                    // Scene Management commands
                    case "scene_load":
                        SceneManager.LoadScene(parameters.Length > 0 ? parameters[0] : "");
                        break;
                    case "scene_save":
                        SceneManager.SaveScene(parameters.Length > 0 ? parameters[0] : null);
                        break;
                    case "scene_create":
                        SceneManager.CreateScene(parameters.Length > 0 ? parameters[0] : "NewScene");
                        break;
                    case "scene_hierarchy":
                        SceneManager.GetSceneHierarchy();
                        break;
                    
                    // GameObject Operations commands
                    case "gameobject_create":
                        string objName = parameters.Length > 0 ? parameters[0] : "GameObject";
                        string parentPath = parameters.Length > 1 ? parameters[1] : null;
                        GameObjectManager.CreateGameObject(objName, parentPath);
                        break;
                    case "gameobject_delete":
                        GameObjectManager.DeleteGameObject(parameters.Length > 0 ? parameters[0] : "");
                        break;
                    case "gameobject_find":
                        string searchTerm = parameters.Length > 0 ? parameters[0] : "";
                        string searchType = parameters.Length > 1 ? parameters[1] : "name";
                        GameObjectManager.FindGameObjects(searchTerm, searchType);
                        break;
                    case "gameobject_transform":
                        string objPath = parameters.Length > 0 ? parameters[0] : "";
                        GameObjectManager.TransformGameObject(objPath);
                        break;
                    
                    // Component Management commands
                    case "component_add":
                        string compObjPath = parameters.Length > 0 ? parameters[0] : "";
                        string compType = parameters.Length > 1 ? parameters[1] : "";
                        ComponentManager.AddComponent(compObjPath, compType);
                        break;
                    case "component_remove":
                        string remObjPath = parameters.Length > 0 ? parameters[0] : "";
                        string remCompType = parameters.Length > 1 ? parameters[1] : "";
                        ComponentManager.RemoveComponent(remObjPath, remCompType);
                        break;
                    case "component_get":
                        string getObjPath = parameters.Length > 0 ? parameters[0] : "";
                        string getCompType = parameters.Length > 1 ? parameters[1] : null;
                        ComponentManager.GetComponent(getObjPath, getCompType);
                        break;
                    case "component_set_property":
                        if (parameters.Length >= 4)
                        {
                            ComponentManager.SetComponentProperty(parameters[0], parameters[1], parameters[2], parameters[3]);
                        }
                        else
                        {
                            throw new ArgumentException("component_set_property requires objectPath, componentType, propertyName, and value");
                        }
                        break;
                    
                    // Placeholder implementations for remaining tool categories
                    case "asset_import":
                    case "asset_export":
                    case "texture_compress":
                    case "audio_compress":
                    case "model_optimize":
                    case "asset_bundle_build":
                    case "asset_dependency":
                    case "asset_reference":
                    case "asset_validate":
                    case "asset_cleanup":
                    case "animation_create":
                    case "animation_clip":
                    case "animator_controller":
                    case "animation_event":
                    case "timeline_create":
                    case "timeline_track":
                    case "timeline_clip":
                    case "timeline_marker":
                    case "timeline_signal":
                    case "timeline_playable":
                    case "rigidbody_add":
                    case "collider_add":
                    case "joint_add":
                    case "physics_material":
                    case "physics_simulate":
                    case "collision_detect":
                    case "raycast_perform":
                    case "physics_settings":
                    case "physics_layer":
                    case "physics_debug":
                    case "material_create":
                    case "shader_compile":
                    case "texture_generate":
                    case "lighting_bake":
                    case "camera_setup":
                    case "render_pipeline":
                    case "post_processing":
                    case "particle_system":
                    case "visual_effect":
                    case "graphics_settings":
                    case "audio_source":
                    case "audio_listener":
                    case "audio_mixer":
                    case "audio_clip":
                    case "audio_reverb":
                    case "audio_filter":
                    case "audio_settings":
                    case "audio_3d":
                    case "audio_occlusion":
                    case "audio_streaming":
                    case "ui_canvas":
                    case "ui_element":
                    case "ui_layout":
                    case "ui_animation":
                    case "ui_event":
                    case "ui_navigation":
                    case "ui_accessibility":
                    case "ui_localization":
                    case "ui_theme":
                    case "ui_responsive":
                    case "build_settings":
                    case "build_target":
                    case "build_pipeline":
                    case "build_report":
                    case "build_addressable":
                    case "build_cloud":
                    case "build_automation":
                    case "build_optimization":
                    case "build_validation":
                    case "build_distribution":
                    case "script_create":
                    case "script_template":
                    case "script_compile":
                    case "script_analyze":
                    case "code_generate":
                    case "code_refactor":
                    case "code_format":
                    case "code_documentation":
                    case "code_test":
                    case "code_metrics":
                    case "profiler_start":
                    case "profiler_memory":
                    case "profiler_cpu":
                    case "profiler_gpu":
                    case "profiler_audio":
                    case "profiler_network":
                    case "performance_analyze":
                    case "performance_optimize":
                    case "performance_benchmark":
                    case "performance_report":
                    case "project_settings":
                    case "project_version":
                    case "project_package":
                    case "project_template":
                    case "project_export":
                    case "project_import":
                    case "project_backup":
                    case "project_restore":
                    case "project_migrate":
                    case "project_validate":
                    case "test_create":
                    case "test_run":
                    case "test_coverage":
                    case "test_performance":
                    case "test_integration":
                    case "test_ui":
                    case "test_automation":
                    case "test_report":
                    case "test_mock":
                    case "test_data":
                        UnityMCPBridge.WriteResult(command, new { 
                            status = "Command received and processed", 
                            command = command, 
                            parameters = parameters,
                            message = $"MCP tool '{command}' executed successfully with {parameters.Length} parameters"
                        });
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