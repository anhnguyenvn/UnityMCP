using System;
using System.Collections.Generic;
using UnityEngine;

namespace UnityMCP.Runtime
{
    /// <summary>
    /// Runtime component for Unity MCP Bridge integration
    /// Provides runtime access to MCP functionality
    /// </summary>
    public class UnityMCPRuntime : MonoBehaviour
    {
        [Header("MCP Configuration")]
        [SerializeField] private bool enableMCPIntegration = true;
        [SerializeField] private string mcpServerEndpoint = "localhost:8080";
        [SerializeField] private float connectionTimeout = 30f;
        
        [Header("Logging")]
        [SerializeField] private bool enableDebugLogging = false;
        
        // Events
        public static event Action<string> OnMCPMessage;
        public static event Action<bool> OnMCPConnectionChanged;
        
        // Properties
        public static bool IsConnected { get; private set; }
        public static UnityMCPRuntime Instance { get; private set; }
        
        private void Awake()
        {
            // Singleton pattern
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeMCP();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        private void InitializeMCP()
        {
            if (!enableMCPIntegration)
            {
                LogDebug("MCP Integration is disabled");
                return;
            }
            
            LogDebug("Initializing Unity MCP Runtime");
            
            // Initialize MCP connection (placeholder for future implementation)
            // This would connect to the MCP server in a real implementation
            IsConnected = false;
            OnMCPConnectionChanged?.Invoke(IsConnected);
        }
        
        /// <summary>
        /// Send a message to the MCP server
        /// </summary>
        /// <param name="message">Message to send</param>
        public static void SendMCPMessage(string message)
        {
            if (Instance == null || !Instance.enableMCPIntegration)
            {
                Debug.LogWarning("MCP Runtime not initialized or disabled");
                return;
            }
            
            Instance.LogDebug($"Sending MCP message: {message}");
            
            // Placeholder for actual MCP communication
            // In a real implementation, this would send the message to the MCP server
            OnMCPMessage?.Invoke(message);
        }
        
        /// <summary>
        /// Get current MCP configuration
        /// </summary>
        /// <returns>Dictionary containing current configuration</returns>
        public static Dictionary<string, object> GetMCPConfiguration()
        {
            if (Instance == null)
                return new Dictionary<string, object>();
                
            return new Dictionary<string, object>
            {
                {"enabled", Instance.enableMCPIntegration},
                {"endpoint", Instance.mcpServerEndpoint},
                {"timeout", Instance.connectionTimeout},
                {"connected", IsConnected},
                {"debugLogging", Instance.enableDebugLogging}
            };
        }
        
        /// <summary>
        /// Update MCP server endpoint
        /// </summary>
        /// <param name="endpoint">New endpoint URL</param>
        public static void SetMCPEndpoint(string endpoint)
        {
            if (Instance != null)
            {
                Instance.mcpServerEndpoint = endpoint;
                Instance.LogDebug($"MCP endpoint updated to: {endpoint}");
            }
        }
        
        /// <summary>
        /// Enable or disable debug logging
        /// </summary>
        /// <param name="enabled">Whether to enable debug logging</param>
        public static void SetDebugLogging(bool enabled)
        {
            if (Instance != null)
            {
                Instance.enableDebugLogging = enabled;
                Instance.LogDebug($"Debug logging {(enabled ? "enabled" : "disabled")}");
            }
        }
        
        private void LogDebug(string message)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"[Unity MCP Runtime] {message}");
            }
        }
        
        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
                IsConnected = false;
                OnMCPConnectionChanged?.Invoke(IsConnected);
            }
        }
    }
}