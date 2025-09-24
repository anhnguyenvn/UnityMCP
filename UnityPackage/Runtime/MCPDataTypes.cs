using System;
using System.Collections.Generic;
using UnityEngine;

namespace UnityMCP.Runtime
{
    /// <summary>
    /// Data structures for MCP communication
    /// </summary>
    
    [Serializable]
    public class MCPMessage
    {
        public string id;
        public string type;
        public string action;
        public Dictionary<string, object> parameters;
        public DateTime timestamp;
        
        public MCPMessage()
        {
            id = Guid.NewGuid().ToString();
            timestamp = DateTime.Now;
            parameters = new Dictionary<string, object>();
        }
        
        public MCPMessage(string messageType, string messageAction) : this()
        {
            type = messageType;
            action = messageAction;
        }
    }
    
    [Serializable]
    public class MCPResponse
    {
        public string messageId;
        public bool success;
        public string error;
        public Dictionary<string, object> data;
        public DateTime timestamp;
        
        public MCPResponse()
        {
            timestamp = DateTime.Now;
            data = new Dictionary<string, object>();
        }
        
        public MCPResponse(string msgId, bool isSuccess) : this()
        {
            messageId = msgId;
            success = isSuccess;
        }
    }
    
    [Serializable]
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
        
        public ProjectInfo()
        {
            projectName = Application.productName;
            companyName = Application.companyName;
            version = Application.version;
            unityVersion = Application.unityVersion;
            lastModified = DateTime.Now;
        }
    }
    
    [Serializable]
    public class BuildInfo
    {
        public string buildTarget;
        public string outputPath;
        public bool developmentBuild;
        public bool autoConnectProfiler;
        public bool deepProfiling;
        public DateTime buildTime;
        public bool success;
        public string errorMessage;
        
        public BuildInfo()
        {
            buildTime = DateTime.Now;
            success = false;
        }
    }
    
    [Serializable]
    public class TestResult
    {
        public string testName;
        public string testType; // "PlayMode" or "EditMode"
        public bool passed;
        public float duration;
        public string errorMessage;
        public DateTime executionTime;
        
        public TestResult()
        {
            executionTime = DateTime.Now;
        }
    }
    
    [Serializable]
    public class AssetInfo
    {
        public string assetPath;
        public string assetType;
        public long fileSize;
        public DateTime lastModified;
        public string guid;
        public List<string> dependencies;
        
        public AssetInfo()
        {
            dependencies = new List<string>();
            lastModified = DateTime.Now;
        }
    }
    
    [Serializable]
    public class SceneInfo
    {
        public string sceneName;
        public string scenePath;
        public bool isEnabled;
        public int buildIndex;
        public int gameObjectCount;
        public List<string> components;
        
        public SceneInfo()
        {
            components = new List<string>();
        }
    }
    
    /// <summary>
    /// MCP Command types
    /// </summary>
    public static class MCPCommands
    {
        public const string PROJECT_SCAN = "project.scan";
        public const string BUILD_RUN = "build.run";
        public const string TEST_PLAYMODE = "test.playmode";
        public const string TEST_EDITMODE = "test.editmode";
        public const string SCENE_VALIDATE = "scene.validate";
        public const string ASSET_AUDIT = "asset.audit";
        public const string CODEGEN_APPLY = "codegen.apply";
        public const string EDITOR_EXEC = "editor.exec";
        public const string PERF_PROFILE = "perf.profile";
    }
    
    /// <summary>
    /// MCP Response types
    /// </summary>
    public static class MCPResponseTypes
    {
        public const string SUCCESS = "success";
        public const string ERROR = "error";
        public const string PROGRESS = "progress";
        public const string INFO = "info";
    }
}