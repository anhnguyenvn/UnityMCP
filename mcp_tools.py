"""MCP Tools Implementation for Unity Operations"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from config import config
from unity_manager import UnityManager


logger = logging.getLogger(__name__)


# Tool Parameter Models
class ProjectScanParams(BaseModel):
    """Parameters for project.scan tool"""
    project_path: str = Field(description="Path to Unity project")
    patterns: List[str] = Field(default=["**/*.cs", "**/*.prefab"], description="File patterns to scan")
    include_assets: bool = Field(default=True, description="Include asset files in scan")
    max_depth: int = Field(default=10, description="Maximum directory depth")


class BuildRunParams(BaseModel):
    """Parameters for build.run tool"""
    project_path: str = Field(description="Path to Unity project")
    target: str = Field(description="Build target (android/ios/win64/osx/webgl)")
    scripting_backend: Optional[str] = Field(default=None, description="Scripting backend (mono/il2cpp)")
    development_build: bool = Field(default=False, description="Enable development build")
    output_path: str = Field(description="Build output directory path")
    timeout_minutes: int = Field(default=30, description="Build timeout in minutes")


class TestRunParams(BaseModel):
    """Parameters for test execution tools"""
    project_path: str = Field(description="Path to Unity project")
    test_mode: str = Field(description="Test mode (playmode/editmode)")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Test filtering options")
    output_path: str = Field(description="JUnit XML output path")
    timeout_minutes: int = Field(default=15, description="Test timeout in minutes")
    collect_coverage: bool = Field(default=False, description="Collect code coverage data")


class SceneValidateParams(BaseModel):
    """Parameters for scene.validate tool"""
    project_path: str = Field(description="Path to Unity project")
    scene_paths: Optional[List[str]] = Field(default=None, description="Specific scene paths to validate")
    check_missing_scripts: bool = Field(default=True, description="Check for missing scripts")
    check_lightmaps: bool = Field(default=True, description="Check lightmap issues")


class AssetAuditParams(BaseModel):
    """Parameters for asset.audit tool"""
    project_path: str = Field(description="Path to Unity project")
    asset_types: Optional[List[str]] = Field(default=None, description="Asset types to audit")
    check_import_settings: bool = Field(default=True, description="Check import settings")
    check_optimization: bool = Field(default=True, description="Check optimization opportunities")


class CodegenApplyParams(BaseModel):
    """Parameters for codegen.apply tool"""
    project_path: str = Field(description="Path to Unity project")
    file_path: str = Field(description="Target C# file path")
    patch_content: str = Field(description="Code patch to apply")
    preview_only: bool = Field(default=False, description="Preview changes without applying")


class EditorExecParams(BaseModel):
    """Parameters for editor.exec tool"""
    project_path: str = Field(description="Path to Unity project")
    method_name: str = Field(description="Unity Editor method to execute")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")
    timeout_minutes: int = Field(default=5, description="Execution timeout in minutes")


class PerfProfileParams(BaseModel):
    """Parameters for perf.profile tool"""
    project_path: str = Field(description="Path to Unity project")
    scene_path: Optional[str] = Field(default=None, description="Scene to profile")
    duration_seconds: int = Field(default=30, description="Profiling duration")
    output_path: str = Field(description="Profiler data output path")


def register_tools(mcp: FastMCP, unity_manager: UnityManager):
    """Register all Unity MCP tools"""
    
    @mcp.tool()
    async def project_scan(params: ProjectScanParams) -> Dict[str, Any]:
        """Scan Unity project structure and return file metadata"""
        try:
            logger.info(f"Scanning Unity project: {params.project_path}")
            
            # Validate project path
            if not config.validate_unity_project_path(params.project_path):
                return {
                    "success": False,
                    "error": f"Invalid Unity project path: {params.project_path}"
                }
            
            # Execute Unity command
            result = await unity_manager.execute_unity_command(
                action="project.scan",
                project_path=params.project_path,
                parameters={
                    "patterns": params.patterns,
                    "includeAssets": params.include_assets,
                    "maxDepth": params.max_depth
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "project_path": params.project_path,
                "patterns": params.patterns
            }
            
        except Exception as e:
            logger.error(f"Project scan failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def build_run(params: BuildRunParams) -> Dict[str, Any]:
        """Execute Unity build for specified platform and configuration"""
        try:
            logger.info(f"Starting Unity build: {params.target} for {params.project_path}")
            
            # Validate project path
            if not config.validate_unity_project_path(params.project_path):
                return {
                    "success": False,
                    "error": f"Invalid Unity project path: {params.project_path}"
                }
            
            # Execute Unity build command
            result = await unity_manager.execute_unity_command(
                action="build.run",
                project_path=params.project_path,
                parameters={
                    "target": params.target,
                    "scriptingBackend": params.scripting_backend,
                    "developmentBuild": params.development_build,
                    "outputPath": params.output_path
                },
                timeout=params.timeout_minutes * 60
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "target": params.target,
                "output_path": params.output_path
            }
            
        except Exception as e:
            logger.error(f"Unity build failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def test_playmode(params: TestRunParams) -> Dict[str, Any]:
        """Run Unity PlayMode tests and return results"""
        try:
            logger.info(f"Running PlayMode tests for {params.project_path}")
            
            test_params = params.dict()
            test_params["test_mode"] = "playmode"
            
            result = await unity_manager.execute_unity_command(
                action="test.run",
                project_path=params.project_path,
                parameters=test_params,
                timeout=params.timeout_minutes * 60
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "test_mode": "playmode",
                "output_path": params.output_path
            }
            
        except Exception as e:
            logger.error(f"PlayMode tests failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def test_editmode(params: TestRunParams) -> Dict[str, Any]:
        """Run Unity EditMode tests and return results"""
        try:
            logger.info(f"Running EditMode tests for {params.project_path}")
            
            test_params = params.dict()
            test_params["test_mode"] = "editmode"
            
            result = await unity_manager.execute_unity_command(
                action="test.run",
                project_path=params.project_path,
                parameters=test_params,
                timeout=params.timeout_minutes * 60
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "test_mode": "editmode",
                "output_path": params.output_path
            }
            
        except Exception as e:
            logger.error(f"EditMode tests failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_validate(params: SceneValidateParams) -> Dict[str, Any]:
        """Validate Unity scenes for common issues and missing references"""
        try:
            logger.info(f"Validating scenes for {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.validate",
                project_path=params.project_path,
                parameters={
                    "scenePaths": params.scene_paths,
                    "checkMissingScripts": params.check_missing_scripts,
                    "checkLightmaps": params.check_lightmaps
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_paths": params.scene_paths
            }
            
        except Exception as e:
            logger.error(f"Scene validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_audit(params: AssetAuditParams) -> Dict[str, Any]:
        """Audit Unity assets for optimization opportunities"""
        try:
            logger.info(f"Auditing assets for {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.audit",
                project_path=params.project_path,
                parameters={
                    "assetTypes": params.asset_types,
                    "checkImportSettings": params.check_import_settings,
                    "checkOptimization": params.check_optimization
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "asset_types": params.asset_types
            }
            
        except Exception as e:
            logger.error(f"Asset audit failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def codegen_apply(params: CodegenApplyParams) -> Dict[str, Any]:
        """Apply code generation patches to Unity C# scripts"""
        try:
            logger.info(f"Applying code patch to {params.file_path}")
            
            result = await unity_manager.execute_unity_command(
                action="codegen.apply",
                project_path=params.project_path,
                parameters={
                    "filePath": params.file_path,
                    "patchContent": params.patch_content,
                    "previewOnly": params.preview_only
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "file_path": params.file_path,
                "preview_only": params.preview_only
            }
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def editor_exec(params: EditorExecParams) -> Dict[str, Any]:
        """Execute Unity Editor methods and custom tools safely"""
        try:
            logger.info(f"Executing Unity Editor method: {params.method_name}")
            
            result = await unity_manager.execute_unity_command(
                action="editor.exec",
                project_path=params.project_path,
                parameters={
                    "methodName": params.method_name,
                    "parameters": params.parameters or {}
                },
                timeout=params.timeout_minutes * 60
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "method_name": params.method_name
            }
            
        except Exception as e:
            logger.error(f"Editor execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def perf_profile(params: PerfProfileParams) -> Dict[str, Any]:
        """Capture Unity profiler data and performance snapshots"""
        try:
            logger.info(f"Starting performance profiling for {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="perf.profile",
                project_path=params.project_path,
                parameters={
                    "scenePath": params.scene_path,
                    "durationSeconds": params.duration_seconds,
                    "outputPath": params.output_path
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_path": params.scene_path,
                "output_path": params.output_path
            }
            
        except Exception as e:
            logger.error(f"Performance profiling failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    logger.info("Unity MCP tools registered successfully")