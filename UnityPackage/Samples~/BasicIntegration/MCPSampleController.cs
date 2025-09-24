using System.Collections;
using UnityEngine;
using UnityMCP.Runtime;

namespace UnityMCP.Samples
{
    /// <summary>
    /// Sample controller demonstrating basic Unity MCP Bridge integration
    /// </summary>
    public class MCPSampleController : MonoBehaviour
    {
        [Header("Sample Configuration")]
        [SerializeField] private bool sendTestMessages = true;
        [SerializeField] private float messageInterval = 5f;
        [SerializeField] private bool logMCPEvents = true;
        
        [Header("UI References")]
        [SerializeField] private UnityEngine.UI.Text statusText;
        [SerializeField] private UnityEngine.UI.Button sendMessageButton;
        [SerializeField] private UnityEngine.UI.Button scanProjectButton;
        
        private Coroutine messageCoroutine;
        private int messageCount = 0;
        
        void Start()
        {
            InitializeMCPIntegration();
            SetupUI();
            
            if (sendTestMessages)
            {
                StartSendingTestMessages();
            }
        }
        
        void OnDestroy()
        {
            // Unsubscribe from events to prevent memory leaks
            UnityMCPRuntime.OnMCPMessage -= HandleMCPMessage;
            UnityMCPRuntime.OnMCPConnectionChanged -= HandleConnectionChange;
        }
        
        /// <summary>
        /// Initialize MCP integration and subscribe to events
        /// </summary>
        private void InitializeMCPIntegration()
        {
            Debug.Log("[MCP Sample] Initializing MCP integration...");
            
            // Subscribe to MCP events
            UnityMCPRuntime.OnMCPMessage += HandleMCPMessage;
            UnityMCPRuntime.OnMCPConnectionChanged += HandleConnectionChange;
            
            // Log current configuration
            var config = UnityMCPRuntime.GetMCPConfiguration();
            Debug.Log($"[MCP Sample] MCP Configuration: {string.Join(", ", config)}");
            
            // Send initial message
            UnityMCPRuntime.SendMCPMessage("MCP Sample Controller initialized");
        }
        
        /// <summary>
        /// Setup UI elements if available
        /// </summary>
        private void SetupUI()
        {
            if (sendMessageButton != null)
            {
                sendMessageButton.onClick.AddListener(SendTestMessage);
            }
            
            if (scanProjectButton != null)
            {
                scanProjectButton.onClick.AddListener(TriggerProjectScan);
            }
            
            UpdateStatusUI();
        }
        
        /// <summary>
        /// Handle incoming MCP messages
        /// </summary>
        /// <param name="message">Received message</param>
        private void HandleMCPMessage(string message)
        {
            if (logMCPEvents)
            {
                Debug.Log($"[MCP Sample] Received MCP message: {message}");
            }
            
            // You can add custom logic here to handle specific messages
            if (message.Contains("scan"))
            {
                Debug.Log("[MCP Sample] Project scan message detected");
            }
        }
        
        /// <summary>
        /// Handle MCP connection status changes
        /// </summary>
        /// <param name="connected">Connection status</param>
        private void HandleConnectionChange(bool connected)
        {
            string status = connected ? "Connected" : "Disconnected";
            Debug.Log($"[MCP Sample] MCP connection status changed: {status}");
            
            UpdateStatusUI();
            
            if (connected)
            {
                UnityMCPRuntime.SendMCPMessage("Connection established from sample controller");
            }
        }
        
        /// <summary>
        /// Start sending periodic test messages
        /// </summary>
        private void StartSendingTestMessages()
        {
            if (messageCoroutine != null)
            {
                StopCoroutine(messageCoroutine);
            }
            
            messageCoroutine = StartCoroutine(SendPeriodicMessages());
        }
        
        /// <summary>
        /// Coroutine for sending periodic test messages
        /// </summary>
        private IEnumerator SendPeriodicMessages()
        {
            while (sendTestMessages)
            {
                yield return new WaitForSeconds(messageInterval);
                
                messageCount++;
                string message = $"Test message #{messageCount} from Unity at {System.DateTime.Now:HH:mm:ss}";
                UnityMCPRuntime.SendMCPMessage(message);
                
                Debug.Log($"[MCP Sample] Sent periodic message: {message}");
            }
        }
        
        /// <summary>
        /// Send a single test message (called by UI button)
        /// </summary>
        public void SendTestMessage()
        {
            string message = $"Manual test message sent at {System.DateTime.Now:HH:mm:ss}";
            UnityMCPRuntime.SendMCPMessage(message);
            Debug.Log($"[MCP Sample] Manual message sent: {message}");
        }
        
        /// <summary>
        /// Trigger a project scan (called by UI button)
        /// </summary>
        public void TriggerProjectScan()
        {
            Debug.Log("[MCP Sample] Triggering project scan...");
            
            #if UNITY_EDITOR
            // In editor, we can call the bridge directly
            UnityMCP.Editor.UnityMCPBridge.ScanProject();
            #else
            // In runtime, send a message requesting scan
            UnityMCPRuntime.SendMCPMessage("REQUEST_PROJECT_SCAN");
            #endif
        }
        
        /// <summary>
        /// Update UI status display
        /// </summary>
        private void UpdateStatusUI()
        {
            if (statusText != null)
            {
                bool isConnected = UnityMCPRuntime.IsConnected;
                string status = isConnected ? "Connected" : "Disconnected";
                string color = isConnected ? "green" : "red";
                
                statusText.text = $"MCP Status: <color={color}>{status}</color>\n" +
                                 $"Messages Sent: {messageCount}\n" +
                                 $"Runtime Available: {(UnityMCPRuntime.Instance != null ? "Yes" : "No")}";
            }
        }
        
        /// <summary>
        /// Toggle periodic message sending
        /// </summary>
        public void TogglePeriodicMessages()
        {
            sendTestMessages = !sendTestMessages;
            
            if (sendTestMessages)
            {
                StartSendingTestMessages();
                Debug.Log("[MCP Sample] Periodic messages enabled");
            }
            else
            {
                if (messageCoroutine != null)
                {
                    StopCoroutine(messageCoroutine);
                    messageCoroutine = null;
                }
                Debug.Log("[MCP Sample] Periodic messages disabled");
            }
        }
        
        /// <summary>
        /// Get sample statistics for debugging
        /// </summary>
        public void LogSampleStatistics()
        {
            var config = UnityMCPRuntime.GetMCPConfiguration();
            
            Debug.Log($"[MCP Sample] Statistics:\n" +
                     $"- Messages sent: {messageCount}\n" +
                     $"- Periodic messaging: {sendTestMessages}\n" +
                     $"- Message interval: {messageInterval}s\n" +
                     $"- MCP Runtime available: {UnityMCPRuntime.Instance != null}\n" +
                     $"- MCP connected: {UnityMCPRuntime.IsConnected}\n" +
                     $"- Configuration: {string.Join(", ", config)}");
        }
        
        // Public methods for external control
        
        /// <summary>
        /// Set message interval
        /// </summary>
        public void SetMessageInterval(float interval)
        {
            messageInterval = Mathf.Max(1f, interval);
            Debug.Log($"[MCP Sample] Message interval set to {messageInterval}s");
        }
        
        /// <summary>
        /// Enable or disable event logging
        /// </summary>
        public void SetEventLogging(bool enabled)
        {
            logMCPEvents = enabled;
            Debug.Log($"[MCP Sample] Event logging {(enabled ? "enabled" : "disabled")}");
        }
    }
}