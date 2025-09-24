using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityMCP.Runtime;

namespace UnityMCP.Editor
{
    /// <summary>
    /// Unity Editor window for MCP Bridge management and configuration
    /// </summary>
    public class UnityMCPWindow : EditorWindow
    {
        private Vector2 scrollPosition;
        private bool showConnectionSettings = true;
        private bool showProjectInfo = true;
        private bool showLogs = true;
        
        // Connection settings
        private string mcpServerEndpoint = "localhost:8080";
        private float connectionTimeout = 30f;
        private bool enableDebugLogging = false;
        
        // UI styles
        private GUIStyle headerStyle;
        private GUIStyle boxStyle;
        private bool stylesInitialized = false;
        
        [MenuItem("Window/Unity MCP/MCP Bridge Window")]
        public static void ShowWindow()
        {
            var window = GetWindow<UnityMCPWindow>("Unity MCP Bridge");
            window.minSize = new Vector2(400, 600);
            window.Show();
        }
        
        private void OnEnable()
        {
            LoadSettings();
        }
        
        private void InitializeStyles()
        {
            if (stylesInitialized) return;
            
            headerStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 14,
                normal = { textColor = EditorGUIUtility.isProSkin ? Color.white : Color.black }
            };
            
            boxStyle = new GUIStyle(GUI.skin.box)
            {
                padding = new RectOffset(10, 10, 10, 10),
                margin = new RectOffset(5, 5, 5, 5)
            };
            
            stylesInitialized = true;
        }
        
        private void OnGUI()
        {
            InitializeStyles();
            
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            // Header
            DrawHeader();
            
            GUILayout.Space(10);
            
            // Connection Settings
            DrawConnectionSettings();
            
            GUILayout.Space(10);
            
            // Project Information
            DrawProjectInfo();
            
            GUILayout.Space(10);
            
            // Actions
            DrawActions();
            
            GUILayout.Space(10);
            
            // Logs
            DrawLogs();
            
            EditorGUILayout.EndScrollView();
        }
        
        private void DrawHeader()
        {
            EditorGUILayout.BeginVertical(boxStyle);
            
            GUILayout.Label("Unity MCP Bridge", headerStyle);
            GUILayout.Label($"Package Version: {GetPackageVersion()}", EditorStyles.miniLabel);
            GUILayout.Label($"Unity Version: {Application.unityVersion}", EditorStyles.miniLabel);
            
            // Connection status
            var isConnected = UnityMCPRuntime.IsConnected;
            var statusColor = isConnected ? Color.green : Color.red;
            var statusText = isConnected ? "Connected" : "Disconnected";
            
            var originalColor = GUI.color;
            GUI.color = statusColor;
            GUILayout.Label($"Status: {statusText}", EditorStyles.boldLabel);
            GUI.color = originalColor;
            
            EditorGUILayout.EndVertical();
        }
        
        private void DrawConnectionSettings()
        {
            showConnectionSettings = EditorGUILayout.Foldout(showConnectionSettings, "Connection Settings", true);
            
            if (showConnectionSettings)
            {
                EditorGUILayout.BeginVertical(boxStyle);
                
                EditorGUI.BeginChangeCheck();
                
                mcpServerEndpoint = EditorGUILayout.TextField("MCP Server Endpoint", mcpServerEndpoint);
                connectionTimeout = EditorGUILayout.FloatField("Connection Timeout (s)", connectionTimeout);
                enableDebugLogging = EditorGUILayout.Toggle("Enable Debug Logging", enableDebugLogging);
                
                if (EditorGUI.EndChangeCheck())
                {
                    SaveSettings();
                    ApplySettings();
                }
                
                GUILayout.Space(5);
                
                EditorGUILayout.BeginHorizontal();
                
                if (GUILayout.Button("Test Connection"))
                {
                    TestConnection();
                }
                
                if (GUILayout.Button("Reset to Defaults"))
                {
                    ResetToDefaults();
                }
                
                EditorGUILayout.EndHorizontal();
                
                EditorGUILayout.EndVertical();
            }
        }
        
        private void DrawProjectInfo()
        {
            showProjectInfo = EditorGUILayout.Foldout(showProjectInfo, "Project Information", true);
            
            if (showProjectInfo)
            {
                EditorGUILayout.BeginVertical(boxStyle);
                
                var projectPath = UnityMCPBridge.GetProjectPath();
                var editorPath = UnityMCPBridge.GetUnityEditorPath();
                var isValidProject = UnityMCPBridge.IsValidUnityProject();
                
                EditorGUILayout.LabelField("Project Path:", projectPath);
                EditorGUILayout.LabelField("Unity Editor Path:", editorPath);
                EditorGUILayout.LabelField("Valid Unity Project:", isValidProject ? "Yes" : "No");
                
                if (UnityMCPRuntime.Instance != null)
                {
                    var config = UnityMCPRuntime.GetMCPConfiguration();
                    EditorGUILayout.LabelField("Runtime Component:", "Found");
                    EditorGUILayout.LabelField("Runtime Enabled:", config.ContainsKey("enabled") ? config["enabled"].ToString() : "Unknown");
                }
                else
                {
                    EditorGUILayout.LabelField("Runtime Component:", "Not Found");
                    
                    if (GUILayout.Button("Add MCP Runtime to Scene"))
                    {
                        AddMCPRuntimeToScene();
                    }
                }
                
                EditorGUILayout.EndVertical();
            }
        }
        
        private void DrawActions()
        {
            EditorGUILayout.BeginVertical(boxStyle);
            
            GUILayout.Label("Actions", headerStyle);
            
            EditorGUILayout.BeginHorizontal();
            
            if (GUILayout.Button("Scan Project"))
            {
                UnityMCPBridge.ScanProject();
            }
            
            if (GUILayout.Button("Open Output Folder"))
            {
                OpenOutputFolder();
            }
            
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.BeginHorizontal();
            
            if (GUILayout.Button("Clear Logs"))
            {
                ClearLogs();
            }
            
            if (GUILayout.Button("Export Settings"))
            {
                ExportSettings();
            }
            
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.EndVertical();
        }
        
        private void DrawLogs()
        {
            showLogs = EditorGUILayout.Foldout(showLogs, "Recent Logs", true);
            
            if (showLogs)
            {
                EditorGUILayout.BeginVertical(boxStyle);
                
                // This would show recent log entries in a real implementation
                EditorGUILayout.LabelField("Log functionality would be implemented here");
                EditorGUILayout.LabelField("Recent activity:");
                EditorGUILayout.LabelField("• Unity MCP Bridge initialized");
                EditorGUILayout.LabelField("• Package loaded successfully");
                
                if (GUILayout.Button("View Full Log"))
                {
                    ViewFullLog();
                }
                
                EditorGUILayout.EndVertical();
            }
        }
        
        private string GetPackageVersion()
        {
            var packageInfo = UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UnityMCPBridge).Assembly);
            return packageInfo?.version ?? "1.0.0";
        }
        
        private void LoadSettings()
        {
            mcpServerEndpoint = EditorPrefs.GetString("UnityMCP.ServerEndpoint", "localhost:8080");
            connectionTimeout = EditorPrefs.GetFloat("UnityMCP.ConnectionTimeout", 30f);
            enableDebugLogging = EditorPrefs.GetBool("UnityMCP.DebugLogging", false);
        }
        
        private void SaveSettings()
        {
            EditorPrefs.SetString("UnityMCP.ServerEndpoint", mcpServerEndpoint);
            EditorPrefs.SetFloat("UnityMCP.ConnectionTimeout", connectionTimeout);
            EditorPrefs.SetBool("UnityMCP.DebugLogging", enableDebugLogging);
        }
        
        private void ApplySettings()
        {
            if (UnityMCPRuntime.Instance != null)
            {
                UnityMCPRuntime.SetMCPEndpoint(mcpServerEndpoint);
                UnityMCPRuntime.SetDebugLogging(enableDebugLogging);
            }
        }
        
        private void TestConnection()
        {
            // Placeholder for connection testing
            EditorUtility.DisplayDialog("Test Connection", 
                $"Testing connection to {mcpServerEndpoint}...\n(This is a placeholder - actual implementation would test the connection)", 
                "OK");
        }
        
        private void ResetToDefaults()
        {
            mcpServerEndpoint = "localhost:8080";
            connectionTimeout = 30f;
            enableDebugLogging = false;
            SaveSettings();
            ApplySettings();
        }
        
        private void AddMCPRuntimeToScene()
        {
            var go = new GameObject("Unity MCP Runtime");
            go.AddComponent<UnityMCPRuntime>();
            Selection.activeGameObject = go;
            EditorGUIUtility.PingObject(go);
        }
        
        private void OpenOutputFolder()
        {
            var outputPath = System.IO.Path.Combine(Application.dataPath, "../Temp/MCP");
            if (System.IO.Directory.Exists(outputPath))
            {
                EditorUtility.RevealInFinder(outputPath);
            }
            else
            {
                EditorUtility.DisplayDialog("Output Folder", "Output folder does not exist yet. Run a scan or operation first.", "OK");
            }
        }
        
        private void ClearLogs()
        {
            var logPath = System.IO.Path.Combine(Application.dataPath, "../Temp/MCP/mcp_unity.log");
            if (System.IO.File.Exists(logPath))
            {
                System.IO.File.Delete(logPath);
                Debug.Log("[Unity MCP Bridge] Logs cleared");
            }
        }
        
        private void ExportSettings()
        {
            var settings = new Dictionary<string, object>
            {
                {"serverEndpoint", mcpServerEndpoint},
                {"connectionTimeout", connectionTimeout},
                {"debugLogging", enableDebugLogging},
                {"exportTime", DateTime.Now.ToString()},
                {"unityVersion", Application.unityVersion},
                {"packageVersion", GetPackageVersion()}
            };
            
            var json = JsonUtility.ToJson(settings, true);
            var path = EditorUtility.SaveFilePanel("Export MCP Settings", "", "unity_mcp_settings.json", "json");
            
            if (!string.IsNullOrEmpty(path))
            {
                System.IO.File.WriteAllText(path, json);
                EditorUtility.DisplayDialog("Export Settings", $"Settings exported to:\n{path}", "OK");
            }
        }
        
        private void ViewFullLog()
        {
            var logPath = System.IO.Path.Combine(Application.dataPath, "../Temp/MCP/mcp_unity.log");
            if (System.IO.File.Exists(logPath))
            {
                EditorUtility.RevealInFinder(logPath);
            }
            else
            {
                EditorUtility.DisplayDialog("Log File", "Log file does not exist yet.", "OK");
            }
        }
    }
}