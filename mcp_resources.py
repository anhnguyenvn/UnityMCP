"""MCP Resources Implementation for Unity Data Access"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from config import config
from unity_manager import UnityManager


logger = logging.getLogger(__name__)


class UnityResource(BaseModel):
    """Unity resource data model"""
    uri: str
    name: str
    description: str
    mime_type: str
    content: Any
    last_updated: Optional[str] = None


def register_resources(mcp: FastMCP, unity_manager: UnityManager):
    """Register all Unity MCP resources"""
    
    @mcp.resource("unity://project/{path}")
    async def unity_project_resource(path: str) -> Dict[str, Any]:
        """Provide Unity project metadata and configuration"""
        try:
            logger.info(f"Accessing Unity project resource: {path}")
            
            # Validate project path
            if not config.validate_unity_project_path(path):
                return {
                    "error": f"Invalid Unity project path: {path}",
                    "content": None
                }
            
            # Get project information
            project_info = await unity_manager.get_unity_project_info(path)
            
            # Read project settings
            project_path_obj = Path(path)
            project_settings = {}
            
            # Read ProjectSettings.asset if available
            project_settings_file = project_path_obj / "ProjectSettings" / "ProjectSettings.asset"
            if project_settings_file.exists():
                try:
                    # Parse Unity asset file (simplified)
                    with open(project_settings_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Extract basic project info
                        if "companyName:" in content:
                            company_line = [line for line in content.split('\n') if 'companyName:' in line]
                            if company_line:
                                project_settings["companyName"] = company_line[0].split(':')[-1].strip()
                        
                        if "productName:" in content:
                            product_line = [line for line in content.split('\n') if 'productName:' in line]
                            if product_line:
                                project_settings["productName"] = product_line[0].split(':')[-1].strip()
                except Exception as e:
                    logger.warning(f"Could not parse ProjectSettings.asset: {e}")
            
            # Get Unity version from ProjectVersion.txt
            unity_version = "Unknown"
            version_file = project_path_obj / "ProjectSettings" / "ProjectVersion.txt"
            if version_file.exists():
                try:
                    version_content = version_file.read_text()
                    for line in version_content.split('\n'):
                        if line.startswith('m_EditorVersion:'):
                            unity_version = line.split(':')[-1].strip()
                            break
                except Exception as e:
                    logger.warning(f"Could not read Unity version: {e}")
            
            # Scan directory structure
            directories = {
                "Assets": (project_path_obj / "Assets").exists(),
                "ProjectSettings": (project_path_obj / "ProjectSettings").exists(),
                "Packages": (project_path_obj / "Packages").exists(),
                "Library": (project_path_obj / "Library").exists(),
                "Logs": (project_path_obj / "Logs").exists()
            }
            
            resource_data = {
                "project_info": project_info,
                "project_settings": project_settings,
                "unity_version": unity_version,
                "directories": directories,
                "resource_type": "unity_project"
            }
            
            return {
                "content": json.dumps(resource_data, indent=2),
                "mimeType": "application/json"
            }
            
        except Exception as e:
            logger.error(f"Failed to access Unity project resource: {e}")
            return {
                "error": str(e),
                "content": None
            }
    
    @mcp.resource("unity://scenes/{path}")
    async def unity_scenes_resource(path: str) -> Dict[str, Any]:
        """Access Unity scene data and hierarchy information"""
        try:
            logger.info(f"Accessing Unity scenes resource: {path}")
            
            # Validate project path
            if not config.validate_unity_project_path(path):
                return {
                    "error": f"Invalid Unity project path: {path}",
                    "content": None
                }
            
            project_path_obj = Path(path)
            assets_path = project_path_obj / "Assets"
            
            # Find all scene files
            scene_files = []
            if assets_path.exists():
                for scene_file in assets_path.rglob("*.unity"):
                    try:
                        scene_info = {
                            "name": scene_file.stem,
                            "path": str(scene_file.relative_to(project_path_obj)),
                            "full_path": str(scene_file),
                            "size_bytes": scene_file.stat().st_size,
                            "last_modified": scene_file.stat().st_mtime
                        }
                        
                        # Try to extract basic scene info
                        try:
                            with open(scene_file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(1000)  # Read first 1KB
                                scene_info["has_content"] = len(content) > 0
                                scene_info["preview"] = content[:200] + "..." if len(content) > 200 else content
                        except Exception:
                            scene_info["has_content"] = False
                            scene_info["preview"] = "Could not read scene content"
                        
                        scene_files.append(scene_info)
                    except Exception as e:
                        logger.warning(f"Could not process scene file {scene_file}: {e}")
            
            # Read build settings to find scenes in build
            build_scenes = []
            build_settings_file = project_path_obj / "ProjectSettings" / "EditorBuildSettings.asset"
            if build_settings_file.exists():
                try:
                    with open(build_settings_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Simple parsing for scene paths
                        lines = content.split('\n')
                        for line in lines:
                            if 'path:' in line and '.unity' in line:
                                scene_path = line.split('path:')[-1].strip()
                                if scene_path:
                                    build_scenes.append(scene_path)
                except Exception as e:
                    logger.warning(f"Could not parse EditorBuildSettings: {e}")
            
            resource_data = {
                "scene_files": scene_files,
                "build_scenes": build_scenes,
                "total_scenes": len(scene_files),
                "scenes_in_build": len(build_scenes),
                "resource_type": "unity_scenes"
            }
            
            return {
                "content": json.dumps(resource_data, indent=2),
                "mimeType": "application/json"
            }
            
        except Exception as e:
            logger.error(f"Failed to access Unity scenes resource: {e}")
            return {
                "error": str(e),
                "content": None
            }
    
    @mcp.resource("unity://assets/{path}")
    async def unity_assets_resource(path: str) -> Dict[str, Any]:
        """Browse Unity asset database and import settings"""
        try:
            logger.info(f"Accessing Unity assets resource: {path}")
            
            # Validate project path
            if not config.validate_unity_project_path(path):
                return {
                    "error": f"Invalid Unity project path: {path}",
                    "content": None
                }
            
            project_path_obj = Path(path)
            assets_path = project_path_obj / "Assets"
            
            # Scan asset files
            asset_summary = {
                "scripts": [],
                "prefabs": [],
                "materials": [],
                "textures": [],
                "audio": [],
                "models": [],
                "other": []
            }
            
            asset_extensions = {
                "scripts": [".cs"],
                "prefabs": [".prefab"],
                "materials": [".mat"],
                "textures": [".png", ".jpg", ".jpeg", ".tga", ".psd", ".tiff"],
                "audio": [".wav", ".mp3", ".ogg", ".aiff"],
                "models": [".fbx", ".obj", ".dae", ".3ds", ".blend"]
            }
            
            total_size = 0
            total_files = 0
            
            if assets_path.exists():
                for asset_file in assets_path.rglob("*"):
                    if asset_file.is_file() and not asset_file.name.startswith('.'):
                        try:
                            file_info = {
                                "name": asset_file.name,
                                "path": str(asset_file.relative_to(assets_path)),
                                "extension": asset_file.suffix.lower(),
                                "size_bytes": asset_file.stat().st_size,
                                "last_modified": asset_file.stat().st_mtime
                            }
                            
                            total_size += file_info["size_bytes"]
                            total_files += 1
                            
                            # Categorize asset
                            categorized = False
                            for category, extensions in asset_extensions.items():
                                if file_info["extension"] in extensions:
                                    asset_summary[category].append(file_info)
                                    categorized = True
                                    break
                            
                            if not categorized:
                                asset_summary["other"].append(file_info)
                                
                        except Exception as e:
                            logger.warning(f"Could not process asset file {asset_file}: {e}")
            
            # Generate statistics
            statistics = {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "by_category": {
                    category: len(files) for category, files in asset_summary.items()
                }
            }
            
            # Limit file lists to prevent huge responses
            max_files_per_category = 50
            for category in asset_summary:
                if len(asset_summary[category]) > max_files_per_category:
                    asset_summary[category] = asset_summary[category][:max_files_per_category]
                    asset_summary[category].append({
                        "note": f"... and {len(asset_summary[category]) - max_files_per_category} more files"
                    })
            
            resource_data = {
                "asset_summary": asset_summary,
                "statistics": statistics,
                "resource_type": "unity_assets"
            }
            
            return {
                "content": json.dumps(resource_data, indent=2),
                "mimeType": "application/json"
            }
            
        except Exception as e:
            logger.error(f"Failed to access Unity assets resource: {e}")
            return {
                "error": str(e),
                "content": None
            }
    
    @mcp.resource("unity://logs/{path}")
    async def unity_logs_resource(path: str) -> Dict[str, Any]:
        """Access Unity console logs and build output"""
        try:
            logger.info(f"Accessing Unity logs resource: {path}")
            
            project_path_obj = Path(path)
            logs_path = project_path_obj / "Logs"
            
            log_files = []
            if logs_path.exists():
                for log_file in logs_path.rglob("*.log"):
                    try:
                        log_info = {
                            "name": log_file.name,
                            "path": str(log_file.relative_to(project_path_obj)),
                            "size_bytes": log_file.stat().st_size,
                            "last_modified": log_file.stat().st_mtime
                        }
                        
                        # Read last few lines of log
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                log_info["last_lines"] = lines[-10:] if len(lines) > 10 else lines
                        except Exception:
                            log_info["last_lines"] = ["Could not read log content"]
                        
                        log_files.append(log_info)
                    except Exception as e:
                        logger.warning(f"Could not process log file {log_file}: {e}")
            
            # Also check for Unity log file specified in config
            unity_log_path = Path(config.unity_log_file)
            if unity_log_path.exists():
                try:
                    log_info = {
                        "name": unity_log_path.name,
                        "path": str(unity_log_path),
                        "size_bytes": unity_log_path.stat().st_size,
                        "last_modified": unity_log_path.stat().st_mtime,
                        "is_mcp_log": True
                    }
                    
                    with open(unity_log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        log_info["last_lines"] = lines[-20:] if len(lines) > 20 else lines
                    
                    log_files.append(log_info)
                except Exception as e:
                    logger.warning(f"Could not read Unity MCP log: {e}")
            
            resource_data = {
                "log_files": log_files,
                "total_logs": len(log_files),
                "resource_type": "unity_logs"
            }
            
            return {
                "content": json.dumps(resource_data, indent=2),
                "mimeType": "application/json"
            }
            
        except Exception as e:
            logger.error(f"Failed to access Unity logs resource: {e}")
            return {
                "error": str(e),
                "content": None
            }
    
    logger.info("Unity MCP resources registered successfully")