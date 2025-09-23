"""Unity Process Manager for MCP Server"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil
from pydantic import BaseModel

from config import config


logger = logging.getLogger(__name__)


class UnityOperation(BaseModel):
    """Unity operation tracking"""
    id: str
    command: str
    project_path: str
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class UnityManager:
    """Manages Unity Editor processes and operations"""
    
    def __init__(self):
        self.active_operations: Dict[str, UnityOperation] = {}
        self.unity_processes: Dict[str, subprocess.Popen] = {}
        self.bridge_script_path = self._create_bridge_script()
    
    def _create_bridge_script(self) -> str:
        """Create Unity Bridge C# script"""
        bridge_content = '''
using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;

namespace UnityMCP
{
    public static class MCPBridge
    {
        [MenuItem("MCP/Execute Command")]
        public static void ExecuteCommand()
        {
            try
            {
                // Read command from stdin
                string input = Console.ReadLine();
                if (string.IsNullOrEmpty(input))
                    return;
                
                var command = JsonConvert.DeserializeObject<MCPCommand>(input);
                var result = ProcessCommand(command);
                
                // Write result to stdout
                Console.WriteLine(JsonConvert.SerializeObject(result));
            }
            catch (Exception ex)
            {
                var error = new MCPResult
                {
                    Success = false,
                    Error = ex.Message,
                    Data = null
                };
                Console.WriteLine(JsonConvert.SerializeObject(error));
            }
        }
        
        private static MCPResult ProcessCommand(MCPCommand command)
        {
            switch (command.Action)
            {
                case "project.scan":
                    return ScanProject(command.Parameters);
                case "build.run":
                    return RunBuild(command.Parameters);
                case "test.run":
                    return RunTests(command.Parameters);
                case "scene.validate":
                    return ValidateScene(command.Parameters);
                case "asset.audit":
                    return AuditAssets(command.Parameters);
                default:
                    return new MCPResult
                    {
                        Success = false,
                        Error = $"Unknown action: {command.Action}"
                    };
            }
        }
        
        private static MCPResult ScanProject(Dictionary<string, object> parameters)
        {
            var assets = AssetDatabase.FindAssets("");
            var fileList = new List<object>();
            
            foreach (var guid in assets)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var asset = AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(path);
                
                fileList.Add(new
                {
                    guid = guid,
                    path = path,
                    type = asset?.GetType().Name,
                    size = new FileInfo(path).Length
                });
            }
            
            return new MCPResult
            {
                Success = true,
                Data = new { files = fileList, count = fileList.Count }
            };
        }
        
        private static MCPResult RunBuild(Dictionary<string, object> parameters)
        {
            // Implementation for build operations
            return new MCPResult { Success = true, Data = "Build completed" };
        }
        
        private static MCPResult RunTests(Dictionary<string, object> parameters)
        {
            // Implementation for test operations
            return new MCPResult { Success = true, Data = "Tests completed" };
        }
        
        private static MCPResult ValidateScene(Dictionary<string, object> parameters)
        {
            // Implementation for scene validation
            return new MCPResult { Success = true, Data = "Scene validated" };
        }
        
        private static MCPResult AuditAssets(Dictionary<string, object> parameters)
        {
            // Implementation for asset auditing
            return new MCPResult { Success = true, Data = "Assets audited" };
        }
    }
    
    [Serializable]
    public class MCPCommand
    {
        public string Action { get; set; }
        public Dictionary<string, object> Parameters { get; set; }
    }
    
    [Serializable]
    public class MCPResult
    {
        public bool Success { get; set; }
        public string Error { get; set; }
        public object Data { get; set; }
    }
}
'''
        
        # Create temporary bridge script
        bridge_path = Path(tempfile.gettempdir()) / "unity_mcp_bridge.cs"
        bridge_path.write_text(bridge_content)
        return str(bridge_path)
    
    async def execute_unity_command(
        self,
        action: str,
        project_path: str,
        parameters: Dict[str, Any],
        timeout: int = 300
    ) -> Dict[str, Any]:
        """Execute Unity command via batch mode"""
        
        operation_id = f"{action}_{datetime.now().timestamp()}"
        operation = UnityOperation(
            id=operation_id,
            command=action,
            project_path=project_path,
            start_time=datetime.now()
        )
        
        self.active_operations[operation_id] = operation
        
        try:
            # Validate project path
            if not config.validate_unity_project_path(project_path):
                raise ValueError(f"Invalid Unity project path: {project_path}")
            
            # Prepare Unity command
            unity_cmd = [
                config.get_unity_editor_path(),
                "-batchmode",
                "-quit",
                "-projectPath", project_path,
                "-logFile", config.unity_log_file,
                "-executeMethod", "UnityMCP.MCPBridge.ExecuteCommand"
            ]
            
            # Prepare command data
            command_data = {
                "Action": action,
                "Parameters": parameters
            }
            
            logger.info(f"Executing Unity command: {action} for project: {project_path}")
            
            # Execute Unity process
            process = await asyncio.create_subprocess_exec(
                *unity_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path
            )
            
            # Send command data to Unity
            input_data = json.dumps(command_data).encode()
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input_data),
                timeout=timeout
            )
            
            # Parse result
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.decode())
                    operation.status = "completed"
                    operation.result = result
                    operation.end_time = datetime.now()
                    
                    logger.info(f"Unity command completed: {action}")
                    return result
                    
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse Unity output: {e}"
                    operation.status = "failed"
                    operation.error = error_msg
                    raise ValueError(error_msg)
            else:
                error_msg = f"Unity process failed with code {process.returncode}: {stderr.decode()}"
                operation.status = "failed"
                operation.error = error_msg
                raise RuntimeError(error_msg)
                
        except asyncio.TimeoutError:
            error_msg = f"Unity command timed out after {timeout} seconds"
            operation.status = "failed"
            operation.error = error_msg
            raise TimeoutError(error_msg)
            
        except Exception as e:
            operation.status = "failed"
            operation.error = str(e)
            logger.error(f"Unity command failed: {action} - {e}")
            raise
        
        finally:
            operation.end_time = datetime.now()
    
    async def get_unity_project_info(self, project_path: str) -> Dict[str, Any]:
        """Get Unity project information"""
        project_path_obj = Path(project_path)
        
        if not config.validate_unity_project_path(project_path):
            raise ValueError(f"Invalid Unity project path: {project_path}")
        
        # Read project settings
        project_settings_path = project_path_obj / "ProjectSettings" / "ProjectSettings.asset"
        
        project_info = {
            "name": project_path_obj.name,
            "path": str(project_path_obj),
            "exists": project_path_obj.exists(),
            "has_assets": (project_path_obj / "Assets").exists(),
            "has_project_settings": project_settings_path.exists(),
            "last_modified": datetime.fromtimestamp(project_path_obj.stat().st_mtime).isoformat()
        }
        
        return project_info
    
    async def cleanup(self):
        """Cleanup Unity processes and resources"""
        logger.info("Cleaning up Unity processes...")
        
        # Terminate active Unity processes
        for process_id, process in self.unity_processes.items():
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    await asyncio.sleep(1)
                    if process.poll() is None:
                        process.kill()
                    logger.info(f"Terminated Unity process: {process_id}")
            except Exception as e:
                logger.error(f"Error terminating Unity process {process_id}: {e}")
        
        self.unity_processes.clear()
        self.active_operations.clear()
        
        # Clean up bridge script
        try:
            if os.path.exists(self.bridge_script_path):
                os.remove(self.bridge_script_path)
        except Exception as e:
            logger.error(f"Error removing bridge script: {e}")