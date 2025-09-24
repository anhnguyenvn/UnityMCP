"""MCP Tools Implementation for Unity Operations"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

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


# Scene Management Parameters
class SceneLoadParams(BaseModel):
    project_path: str
    scene_path: str
    additive: bool = False

class SceneSaveParams(BaseModel):
    project_path: str
    scene_path: Optional[str] = None
    save_as: Optional[str] = None

class SceneCreateParams(BaseModel):
    project_path: str
    scene_name: str
    template: Optional[str] = None

class SceneHierarchyParams(BaseModel):
    project_path: str
    scene_path: Optional[str] = None
    filter_type: Optional[str] = None

class LightingSettingsParams(BaseModel):
    project_path: str
    scene_path: Optional[str] = None
    settings: Dict[str, Any]

class SceneMergeParams(BaseModel):
    project_path: str
    source_scene: str
    target_scene: str
    merge_mode: str = "additive"

class SceneCompareParams(BaseModel):
    project_path: str
    scene_a: str
    scene_b: str
    compare_type: str = "objects"

class SceneOptimizeParams(BaseModel):
    project_path: str
    scene_path: str
    optimization_level: str = "medium"

class SceneBackupParams(BaseModel):
    project_path: str
    scene_path: str
    backup_path: Optional[str] = None

class SceneStatisticsParams(BaseModel):
    project_path: str
    scene_path: Optional[str] = None
    include_assets: bool = True

# GameObject Operations Parameters
class GameObjectCreateParams(BaseModel):
    project_path: str
    name: str
    parent_path: Optional[str] = None
    primitive_type: Optional[str] = None

class GameObjectDeleteParams(BaseModel):
    project_path: str
    object_path: str
    confirm: bool = False

class GameObjectFindParams(BaseModel):
    project_path: str
    search_query: str
    search_type: str = "name"  # name, tag, component
    scene_path: Optional[str] = None

class GameObjectTransformParams(BaseModel):
    project_path: str
    object_path: str
    position: Optional[List[float]] = None
    rotation: Optional[List[float]] = None
    scale: Optional[List[float]] = None

class GameObjectParentParams(BaseModel):
    project_path: str
    child_path: str
    parent_path: Optional[str] = None  # None means unparent

class GameObjectDuplicateParams(BaseModel):
    project_path: str
    object_path: str
    count: int = 1
    offset: Optional[List[float]] = None

class GameObjectRenameParams(BaseModel):
    project_path: str
    object_path: str
    new_name: str

class GameObjectTagParams(BaseModel):
    project_path: str
    object_path: str
    tag: str

class GameObjectLayerParams(BaseModel):
    project_path: str
    object_path: str
    layer: Union[str, int]

class GameObjectActiveParams(BaseModel):
    project_path: str
    object_path: str
    active: bool

class PrefabCreateParams(BaseModel):
    project_path: str
    object_path: str
    prefab_path: str
    replace_original: bool = False

class PrefabInstantiateParams(BaseModel):
    project_path: str
    prefab_path: str
    parent_path: Optional[str] = None
    position: Optional[List[float]] = None
    rotation: Optional[List[float]] = None

class PrefabUnpackParams(BaseModel):
    project_path: str
    prefab_instance_path: str
    unpack_mode: str = "completely"  # completely, root, outermost

class GameObjectGroupParams(BaseModel):
    project_path: str
    object_paths: List[str]
    group_name: str

class GameObjectAlignParams(BaseModel):
    project_path: str
    object_paths: List[str]
    align_type: str = "center"  # center, left, right, top, bottom


# Component Management Parameters (10 tools)
class ComponentAddParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: str = Field(description="Path to GameObject")
    component_type: str = Field(description="Type of component to add")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Component initialization parameters")

class ComponentRemoveParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: str = Field(description="Path to GameObject")
    component_type: str = Field(description="Type of component to remove")
    confirm: bool = Field(default=False, description="Confirm removal")

class ComponentGetParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: str = Field(description="Path to GameObject")
    component_type: Optional[str] = Field(default=None, description="Specific component type to get")

class ComponentSetPropertyParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: str = Field(description="Path to GameObject")
    component_type: str = Field(description="Type of component")
    property_name: str = Field(description="Property name to set")
    property_value: Any = Field(description="Property value to set")

class ComponentCopyParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    source_object_path: str = Field(description="Source GameObject path")
    target_object_path: str = Field(description="Target GameObject path")
    component_type: str = Field(description="Type of component to copy")

class ComponentSerializeParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: str = Field(description="Path to GameObject")
    component_type: str = Field(description="Type of component to serialize")
    output_path: str = Field(description="Output file path for serialized data")

class ComponentDeserializeParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: str = Field(description="Path to GameObject")
    input_path: str = Field(description="Input file path for serialized data")
    overwrite: bool = Field(default=False, description="Overwrite existing component")

class ComponentValidateParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: Optional[str] = Field(default=None, description="Specific GameObject path to validate")
    component_type: Optional[str] = Field(default=None, description="Specific component type to validate")

class ComponentResetParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: str = Field(description="Path to GameObject")
    component_type: str = Field(description="Type of component to reset")
    confirm: bool = Field(default=False, description="Confirm reset")

class ComponentEnableParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    object_path: str = Field(description="Path to GameObject")
    component_type: str = Field(description="Type of component")
    enabled: bool = Field(description="Enable/disable component")


# Asset Management Parameter Models (15 tools)
class AssetImportParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    asset_path: str = Field(description="Path to asset file")
    import_settings: Optional[Dict[str, Any]] = Field(default=None, description="Import settings")
    force_reimport: bool = Field(default=False, description="Force reimport")

class AssetExportParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    asset_path: str = Field(description="Path to asset in project")
    export_path: str = Field(description="Export destination path")
    export_format: str = Field(description="Export format")
    export_settings: Optional[Dict[str, Any]] = Field(default=None, description="Export settings")

class AssetDatabaseRefreshParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    force_refresh: bool = Field(default=False, description="Force complete refresh")
    import_mode: str = Field(default="synchronous", description="Import mode")

class AssetSearchParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    search_filter: str = Field(description="Search filter string")
    asset_type: Optional[str] = Field(default=None, description="Asset type filter")
    folder_path: Optional[str] = Field(default=None, description="Folder to search in")

class AssetMoveParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    source_path: str = Field(description="Source asset path")
    destination_path: str = Field(description="Destination path")
    overwrite: bool = Field(default=False, description="Overwrite existing")

class AssetDeleteParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    asset_path: str = Field(description="Asset path to delete")
    confirm: bool = Field(default=True, description="Confirm deletion")

class TextureImportParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    texture_path: str = Field(description="Path to texture file")
    texture_type: str = Field(default="Default", description="Texture type")
    max_size: int = Field(default=2048, description="Maximum texture size")
    compression: str = Field(default="Normal", description="Compression format")
    generate_mipmaps: bool = Field(default=True, description="Generate mipmaps")

class MeshImportParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    mesh_path: str = Field(description="Path to mesh file")
    scale_factor: float = Field(default=1.0, description="Scale factor")
    generate_colliders: bool = Field(default=False, description="Generate colliders")
    optimize_mesh: bool = Field(default=True, description="Optimize mesh")
    import_materials: bool = Field(default=True, description="Import materials")

class AudioImportParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    audio_path: str = Field(description="Path to audio file")
    audio_format: str = Field(default="Compressed", description="Audio format")
    quality: float = Field(default=0.7, description="Audio quality")
    load_type: str = Field(default="Decompress On Load", description="Load type")
    force_mono: bool = Field(default=False, description="Force mono")

class AssetBundleCreateParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    bundle_name: str = Field(description="Asset bundle name")
    asset_paths: List[str] = Field(description="List of asset paths")
    build_target: str = Field(default="StandaloneWindows64", description="Build target")
    output_path: str = Field(description="Output path for bundle")

class AssetBundleBuildParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    output_path: str = Field(description="Output path for bundles")
    build_target: str = Field(default="StandaloneWindows64", description="Build target")
    build_options: Optional[List[str]] = Field(default=None, description="Build options")

class AssetDependencyParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    asset_path: str = Field(description="Asset path to analyze")
    include_indirect: bool = Field(default=False, description="Include indirect dependencies")

class AssetMetadataParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    asset_path: str = Field(description="Asset path")
    metadata_key: Optional[str] = Field(default=None, description="Metadata key")
    metadata_value: Optional[str] = Field(default=None, description="Metadata value")

class AssetValidateParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    asset_path: Optional[str] = Field(default=None, description="Specific asset path")
    validation_type: str = Field(default="all", description="Validation type")

class AssetOptimizeParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    asset_path: Optional[str] = Field(default=None, description="Specific asset path")
    optimization_type: str = Field(default="all", description="Optimization type")
    backup: bool = Field(default=True, description="Create backup")


# Animation & Timeline Parameter Models (10 tools)
class AnimationClipCreateParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    clip_name: str = Field(description="Animation clip name")
    duration: float = Field(default=1.0, description="Clip duration in seconds")
    frame_rate: int = Field(default=60, description="Frame rate")
    loop: bool = Field(default=True, description="Loop animation")

class AnimationClipEditParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    clip_path: str = Field(description="Path to animation clip")
    property_path: str = Field(description="Property path to animate")
    keyframes: List[Dict[str, Any]] = Field(description="Keyframe data")
    curve_type: str = Field(default="linear", description="Curve interpolation type")

class AnimatorControllerCreateParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    controller_name: str = Field(description="Animator controller name")
    output_path: str = Field(description="Output path for controller")
    layers: Optional[List[str]] = Field(default=None, description="Layer names")
    parameters: Optional[List[Dict[str, Any]]] = Field(default=None, description="Controller parameters")

class AnimatorStateParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    controller_path: str = Field(description="Path to animator controller")
    layer_name: str = Field(default="Base Layer", description="Layer name")
    state_name: str = Field(description="State name")
    animation_clip: Optional[str] = Field(default=None, description="Animation clip path")
    position: Optional[Dict[str, float]] = Field(default=None, description="State position in graph")

class AnimatorTransitionParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    controller_path: str = Field(description="Path to animator controller")
    layer_name: str = Field(default="Base Layer", description="Layer name")
    from_state: str = Field(description="Source state name")
    to_state: str = Field(description="Target state name")
    conditions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Transition conditions")
    duration: float = Field(default=0.25, description="Transition duration")

class TimelineCreateParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    timeline_name: str = Field(description="Timeline asset name")
    output_path: str = Field(description="Output path for timeline")
    duration: float = Field(default=10.0, description="Timeline duration")
    frame_rate: int = Field(default=60, description="Frame rate")

class TimelineTrackParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    timeline_path: str = Field(description="Path to timeline asset")
    track_name: str = Field(description="Track name")
    track_type: str = Field(description="Track type (Animation, Audio, Control, Playable)")
    binding_object: Optional[str] = Field(default=None, description="Binding object path")

class TimelineClipParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    timeline_path: str = Field(description="Path to timeline asset")
    track_name: str = Field(description="Track name")
    clip_name: str = Field(description="Clip name")
    start_time: float = Field(default=0.0, description="Clip start time")
    duration: float = Field(default=1.0, description="Clip duration")
    asset_path: Optional[str] = Field(default=None, description="Asset path for clip")

class AnimationRecordParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    target_object: str = Field(description="Target GameObject path")
    clip_name: str = Field(description="Animation clip name")
    properties: List[str] = Field(description="Properties to record")
    duration: float = Field(default=5.0, description="Recording duration")
    auto_key: bool = Field(default=True, description="Auto keyframe")

class AnimationBakeParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    source_object: str = Field(description="Source GameObject path")
    target_clip: str = Field(description="Target animation clip path")
    frame_range: Optional[Dict[str, int]] = Field(default=None, description="Frame range to bake")
    sample_rate: int = Field(default=60, description="Sample rate")
    bake_pose: bool = Field(default=True, description="Bake pose")


# Physics & Collision Parameter Models (8 tools)
class RigidbodyParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    mass: float = Field(default=1.0, description="Rigidbody mass")
    drag: float = Field(default=0.0, description="Linear drag")
    angular_drag: float = Field(default=0.05, description="Angular drag")
    use_gravity: bool = Field(default=True, description="Use gravity")
    is_kinematic: bool = Field(default=False, description="Is kinematic")
    freeze_rotation: Optional[List[str]] = Field(default=None, description="Freeze rotation axes")

class ColliderParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    collider_type: str = Field(description="Collider type (Box, Sphere, Capsule, Mesh)")
    is_trigger: bool = Field(default=False, description="Is trigger")
    material: Optional[str] = Field(default=None, description="Physics material path")
    size: Optional[Dict[str, float]] = Field(default=None, description="Collider size parameters")
    center: Optional[Dict[str, float]] = Field(default=None, description="Collider center offset")

class PhysicsMaterialParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    material_name: str = Field(description="Physics material name")
    output_path: str = Field(description="Output path for material")
    dynamic_friction: float = Field(default=0.6, description="Dynamic friction")
    static_friction: float = Field(default=0.6, description="Static friction")
    bounciness: float = Field(default=0.0, description="Bounciness")
    friction_combine: str = Field(default="Average", description="Friction combine mode")
    bounce_combine: str = Field(default="Average", description="Bounce combine mode")

class JointParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    joint_type: str = Field(description="Joint type (Fixed, Hinge, Spring, Character, Configurable)")
    connected_body: Optional[str] = Field(default=None, description="Connected rigidbody path")
    anchor: Optional[Dict[str, float]] = Field(default=None, description="Joint anchor point")
    axis: Optional[Dict[str, float]] = Field(default=None, description="Joint axis")
    limits: Optional[Dict[str, Any]] = Field(default=None, description="Joint limits")
    spring: Optional[Dict[str, float]] = Field(default=None, description="Spring settings")

class PhysicsSimulationParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gravity: Optional[Dict[str, float]] = Field(default=None, description="Gravity vector")
    default_material: Optional[str] = Field(default=None, description="Default physics material")
    bounce_threshold: float = Field(default=2.0, description="Bounce threshold")
    sleep_threshold: float = Field(default=0.005, description="Sleep threshold")
    default_contact_offset: float = Field(default=0.01, description="Default contact offset")
    solver_iterations: int = Field(default=6, description="Solver iterations")
    solver_velocity_iterations: int = Field(default=1, description="Solver velocity iterations")

class RaycastParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    origin: Dict[str, float] = Field(description="Ray origin position")
    direction: Dict[str, float] = Field(description="Ray direction")
    max_distance: float = Field(default=float('inf'), description="Maximum ray distance")
    layer_mask: Optional[int] = Field(default=None, description="Layer mask for filtering")
    query_trigger_interaction: str = Field(default="UseGlobal", description="Query trigger interaction")

class OverlapParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    shape_type: str = Field(description="Shape type (Sphere, Box, Capsule)")
    position: Dict[str, float] = Field(description="Shape position")
    size: Dict[str, float] = Field(description="Shape size parameters")
    layer_mask: Optional[int] = Field(default=None, description="Layer mask for filtering")
    query_trigger_interaction: str = Field(default="UseGlobal", description="Query trigger interaction")

class PhysicsDebugParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    debug_type: str = Field(description="Debug type (Colliders, Contacts, Joints, Raycast)")
    enable: bool = Field(default=True, description="Enable debug visualization")
    color: Optional[Dict[str, float]] = Field(default=None, description="Debug color (RGBA)")
    duration: float = Field(default=1.0, description="Debug display duration")


# Rendering & Graphics Parameter Models (10 tools)
class MaterialParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    material_name: str = Field(description="Material name")
    output_path: str = Field(description="Output path for material")
    shader_name: str = Field(description="Shader name")
    properties: Optional[Dict[str, Any]] = Field(default=None, description="Material properties")
    textures: Optional[Dict[str, str]] = Field(default=None, description="Texture assignments")
    keywords: Optional[List[str]] = Field(default=None, description="Shader keywords")

class ShaderParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    shader_name: str = Field(description="Shader name")
    output_path: str = Field(description="Output path for shader")
    shader_type: str = Field(description="Shader type (Surface, Unlit, PostProcess, Compute)")
    properties: Optional[List[Dict[str, Any]]] = Field(default=None, description="Shader properties")
    passes: Optional[List[Dict[str, Any]]] = Field(default=None, description="Shader passes")
    includes: Optional[List[str]] = Field(default=None, description="Include files")

class CameraParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    clear_flags: str = Field(default="Skybox", description="Clear flags")
    background_color: Optional[Dict[str, float]] = Field(default=None, description="Background color (RGBA)")
    culling_mask: Optional[int] = Field(default=None, description="Culling mask")
    projection: str = Field(default="Perspective", description="Projection type")
    field_of_view: float = Field(default=60.0, description="Field of view")
    near_clip: float = Field(default=0.3, description="Near clipping plane")
    far_clip: float = Field(default=1000.0, description="Far clipping plane")
    render_texture: Optional[str] = Field(default=None, description="Render texture path")

class LightingParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    lighting_type: str = Field(description="Lighting type (Directional, Point, Spot, Area)")
    gameobject_path: Optional[str] = Field(default=None, description="GameObject path for light")
    intensity: float = Field(default=1.0, description="Light intensity")
    color: Optional[Dict[str, float]] = Field(default=None, description="Light color (RGB)")
    range: Optional[float] = Field(default=None, description="Light range")
    spot_angle: Optional[float] = Field(default=None, description="Spot light angle")
    shadows: str = Field(default="Soft", description="Shadow type")
    baking_settings: Optional[Dict[str, Any]] = Field(default=None, description="Light baking settings")

class PostProcessingParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    profile_name: str = Field(description="Post-processing profile name")
    output_path: str = Field(description="Output path for profile")
    effects: Dict[str, Dict[str, Any]] = Field(description="Post-processing effects and settings")
    volume_gameobject: Optional[str] = Field(default=None, description="Volume GameObject path")
    is_global: bool = Field(default=True, description="Is global volume")
    priority: int = Field(default=0, description="Volume priority")

class RenderPipelineParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    pipeline_type: str = Field(description="Pipeline type (Built-in, URP, HDRP)")
    asset_name: str = Field(description="Pipeline asset name")
    output_path: str = Field(description="Output path for pipeline asset")
    settings: Dict[str, Any] = Field(description="Pipeline settings")
    renderer_features: Optional[List[Dict[str, Any]]] = Field(default=None, description="Renderer features")

class TextureParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    texture_path: str = Field(description="Texture file path")
    texture_type: str = Field(default="Default", description="Texture type")
    max_size: int = Field(default=2048, description="Maximum texture size")
    compression: str = Field(default="Compressed", description="Compression format")
    filter_mode: str = Field(default="Bilinear", description="Filter mode")
    wrap_mode: str = Field(default="Repeat", description="Wrap mode")
    generate_mipmaps: bool = Field(default=True, description="Generate mipmaps")
    srgb_texture: bool = Field(default=True, description="sRGB texture")

class MeshParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    mesh_path: str = Field(description="Mesh file path")
    scale_factor: float = Field(default=1.0, description="Scale factor")
    mesh_compression: str = Field(default="Off", description="Mesh compression")
    read_write_enabled: bool = Field(default=False, description="Read/Write enabled")
    optimize_mesh: bool = Field(default=True, description="Optimize mesh")
    generate_colliders: bool = Field(default=False, description="Generate colliders")
    normals: str = Field(default="Import", description="Normals import mode")
    tangents: str = Field(default="CalculateMikk", description="Tangents calculation")

class LODParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    lod_levels: List[Dict[str, Any]] = Field(description="LOD levels configuration")
    fade_mode: str = Field(default="CrossFade", description="LOD fade mode")
    animate_cross_fading: bool = Field(default=False, description="Animate cross fading")

class CullingParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    culling_type: str = Field(description="Culling type (Frustum, Occlusion, Distance)")
    gameobject_path: Optional[str] = Field(default=None, description="GameObject path")
    culling_distance: Optional[float] = Field(default=None, description="Culling distance")
    occlusion_culling: bool = Field(default=True, description="Enable occlusion culling")
    layer_distances: Optional[Dict[str, float]] = Field(default=None, description="Per-layer culling distances")


# Audio System Parameter Models (8 tools)
class AudioSourceParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    audio_clip: Optional[str] = Field(default=None, description="Audio clip path")
    volume: Optional[float] = Field(default=None, description="Audio volume (0-1)")
    pitch: Optional[float] = Field(default=None, description="Audio pitch")
    loop: Optional[bool] = Field(default=None, description="Loop audio")
    play_on_awake: Optional[bool] = Field(default=None, description="Play on awake")
    spatial_blend: Optional[float] = Field(default=None, description="Spatial blend (0=2D, 1=3D)")
    min_distance: Optional[float] = Field(default=None, description="Minimum distance")
    max_distance: Optional[float] = Field(default=None, description="Maximum distance")
    rolloff_mode: Optional[str] = Field(default=None, description="Rolloff mode")

class AudioClipParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    clip_path: str = Field(description="Audio clip file path")
    load_type: Optional[str] = Field(default=None, description="Load type")
    compression_format: Optional[str] = Field(default=None, description="Compression format")
    quality: Optional[float] = Field(default=None, description="Audio quality (0-1)")
    force_to_mono: Optional[bool] = Field(default=None, description="Force to mono")
    normalize: Optional[bool] = Field(default=None, description="Normalize audio")
    load_in_background: Optional[bool] = Field(default=None, description="Load in background")
    ambisonic: Optional[bool] = Field(default=None, description="Ambisonic audio")

class AudioMixerParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    mixer_name: str = Field(description="Audio mixer name")
    output_path: str = Field(description="Output path for mixer")
    groups: Optional[List[Dict[str, Any]]] = Field(default=None, description="Mixer groups")
    snapshots: Optional[List[Dict[str, Any]]] = Field(default=None, description="Mixer snapshots")
    exposed_parameters: Optional[List[str]] = Field(default=None, description="Exposed parameters")
    effects: Optional[List[Dict[str, Any]]] = Field(default=None, description="Audio effects")

class Audio3DParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    doppler_level: Optional[float] = Field(default=None, description="Doppler level")
    spread: Optional[float] = Field(default=None, description="3D spread")
    volume_rolloff: Optional[str] = Field(default=None, description="Volume rolloff")
    min_distance: Optional[float] = Field(default=None, description="Minimum distance")
    max_distance: Optional[float] = Field(default=None, description="Maximum distance")
    reverb_zone_mix: Optional[float] = Field(default=None, description="Reverb zone mix")

class ReverbZoneParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    min_distance: Optional[float] = Field(default=None, description="Minimum distance")
    max_distance: Optional[float] = Field(default=None, description="Maximum distance")
    reverb_preset: Optional[str] = Field(default=None, description="Reverb preset")
    room: Optional[int] = Field(default=None, description="Room parameter")
    room_hf: Optional[int] = Field(default=None, description="Room HF parameter")
    room_lf: Optional[int] = Field(default=None, description="Room LF parameter")
    decay_time: Optional[float] = Field(default=None, description="Decay time")
    decay_hf_ratio: Optional[float] = Field(default=None, description="Decay HF ratio")
    reflections: Optional[int] = Field(default=None, description="Reflections")
    reflections_delay: Optional[float] = Field(default=None, description="Reflections delay")
    reverb: Optional[int] = Field(default=None, description="Reverb")
    reverb_delay: Optional[float] = Field(default=None, description="Reverb delay")
    hf_reference: Optional[float] = Field(default=None, description="HF reference")
    lf_reference: Optional[float] = Field(default=None, description="LF reference")
    diffusion: Optional[float] = Field(default=None, description="Diffusion")
    density: Optional[float] = Field(default=None, description="Density")

class AudioListenerParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    volume_scale: Optional[float] = Field(default=None, description="Volume scale")
    pause_on_audio_focus_loss: Optional[bool] = Field(default=None, description="Pause on audio focus loss")

class AudioStreamingParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    clip_path: str = Field(description="Audio clip path")
    streaming_enabled: bool = Field(description="Enable streaming")
    buffer_size: Optional[int] = Field(default=None, description="Buffer size")
    preload_audio_data: Optional[bool] = Field(default=None, description="Preload audio data")
    load_in_background: Optional[bool] = Field(default=None, description="Load in background")

class AudioCompressionParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    clip_path: str = Field(description="Audio clip path")
    compression_format: str = Field(description="Compression format")
    quality: Optional[float] = Field(default=None, description="Compression quality")
    sample_rate_setting: Optional[str] = Field(default=None, description="Sample rate setting")
    sample_rate_override: Optional[int] = Field(default=None, description="Sample rate override")
    force_to_mono: Optional[bool] = Field(default=None, description="Force to mono")


# UI System Parameter Models (5 tools)
class CanvasParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    render_mode: Optional[str] = Field(default=None, description="Canvas render mode")
    camera: Optional[str] = Field(default=None, description="Camera for Screen Space - Camera mode")
    plane_distance: Optional[float] = Field(default=None, description="Plane distance")
    sorting_layer: Optional[str] = Field(default=None, description="Sorting layer")
    order_in_layer: Optional[int] = Field(default=None, description="Order in layer")
    pixel_perfect: Optional[bool] = Field(default=None, description="Pixel perfect")
    override_sorting: Optional[bool] = Field(default=None, description="Override sorting")
    additional_shader_channels: Optional[List[str]] = Field(default=None, description="Additional shader channels")

class UIElementParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    parent_path: str = Field(description="Parent GameObject path")
    element_type: str = Field(description="UI element type (Button, Text, Image, etc.)")
    element_name: str = Field(description="Element name")
    position: Optional[Dict[str, float]] = Field(default=None, description="Position (x, y, z)")
    size: Optional[Dict[str, float]] = Field(default=None, description="Size (width, height)")
    anchor: Optional[Dict[str, float]] = Field(default=None, description="Anchor settings")
    pivot: Optional[Dict[str, float]] = Field(default=None, description="Pivot point")
    text_content: Optional[str] = Field(default=None, description="Text content for text elements")
    sprite: Optional[str] = Field(default=None, description="Sprite for image elements")
    color: Optional[Dict[str, float]] = Field(default=None, description="Color (r, g, b, a)")
    font: Optional[str] = Field(default=None, description="Font for text elements")
    font_size: Optional[int] = Field(default=None, description="Font size")
    interactable: Optional[bool] = Field(default=None, description="Interactable state")

class EventSystemParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: Optional[str] = Field(default=None, description="GameObject path")
    first_selected: Optional[str] = Field(default=None, description="First selected GameObject")
    send_navigation_events: Optional[bool] = Field(default=None, description="Send navigation events")
    drag_threshold: Optional[int] = Field(default=None, description="Drag threshold")
    input_module_type: Optional[str] = Field(default=None, description="Input module type")

class LayoutGroupParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    layout_type: str = Field(description="Layout group type (Horizontal, Vertical, Grid)")
    padding: Optional[Dict[str, int]] = Field(default=None, description="Padding (left, right, top, bottom)")
    spacing: Optional[float] = Field(default=None, description="Spacing between elements")
    child_alignment: Optional[str] = Field(default=None, description="Child alignment")
    child_control_size: Optional[Dict[str, bool]] = Field(default=None, description="Control child size")
    child_force_expand: Optional[Dict[str, bool]] = Field(default=None, description="Force expand child")
    cell_size: Optional[Dict[str, float]] = Field(default=None, description="Cell size for grid layout")
    constraint: Optional[str] = Field(default=None, description="Grid constraint")
    constraint_count: Optional[int] = Field(default=None, description="Constraint count")

class UIAnimationParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    gameobject_path: str = Field(description="GameObject path")
    animation_type: str = Field(description="Animation type (Fade, Scale, Move, Rotate)")
    duration: Optional[float] = Field(default=None, description="Animation duration")
    ease_type: Optional[str] = Field(default=None, description="Easing type")
    start_value: Optional[Dict[str, Any]] = Field(default=None, description="Start value")
    end_value: Optional[Dict[str, Any]] = Field(default=None, description="End value")
    loop_type: Optional[str] = Field(default=None, description="Loop type")
    auto_play: Optional[bool] = Field(default=None, description="Auto play on start")
    trigger_event: Optional[str] = Field(default=None, description="Trigger event")


# Build System Parameter Models (3 tools)
class BuildPlayerParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    target_platform: str = Field(description="Target platform (Windows, Mac, Linux, iOS, Android, WebGL)")
    build_path: str = Field(description="Build output path")
    development_build: Optional[bool] = Field(default=False, description="Development build")
    script_debugging: Optional[bool] = Field(default=False, description="Script debugging")
    compression: Optional[str] = Field(default="LZ4", description="Compression type")
    scenes: Optional[List[str]] = Field(default=None, description="Scenes to include")
    player_settings: Optional[Dict[str, Any]] = Field(default=None, description="Player settings")

class BuildSettingsParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    company_name: Optional[str] = Field(default=None, description="Company name")
    product_name: Optional[str] = Field(default=None, description="Product name")
    version: Optional[str] = Field(default=None, description="Version")
    bundle_identifier: Optional[str] = Field(default=None, description="Bundle identifier")
    default_icon: Optional[str] = Field(default=None, description="Default icon path")
    splash_screen: Optional[str] = Field(default=None, description="Splash screen path")
    resolution_settings: Optional[Dict[str, Any]] = Field(default=None, description="Resolution settings")
    quality_settings: Optional[Dict[str, Any]] = Field(default=None, description="Quality settings")

class PlatformSwitchParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    target_platform: str = Field(description="Target platform")
    texture_compression: Optional[str] = Field(default=None, description="Texture compression")
    scripting_backend: Optional[str] = Field(default=None, description="Scripting backend")
    api_compatibility_level: Optional[str] = Field(default=None, description="API compatibility level")
    target_device: Optional[str] = Field(default=None, description="Target device")
    architecture: Optional[str] = Field(default=None, description="Architecture")


# Scripting & Code Generation Parameter Models (4 tools)
class ScriptTemplateParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    template_type: str = Field(description="Script template type (MonoBehaviour, ScriptableObject, Editor, etc.)")
    script_name: str = Field(description="Script name")
    output_path: str = Field(description="Output path for script")
    namespace: Optional[str] = Field(default=None, description="Namespace for script")
    base_class: Optional[str] = Field(default=None, description="Base class")
    interfaces: Optional[List[str]] = Field(default=None, description="Interfaces to implement")
    custom_template: Optional[str] = Field(default=None, description="Custom template content")

class CodeAnalysisParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    analysis_type: str = Field(description="Analysis type (syntax, performance, dependencies, etc.)")
    target_files: Optional[List[str]] = Field(default=None, description="Target files to analyze")
    target_directories: Optional[List[str]] = Field(default=None, description="Target directories")
    include_patterns: Optional[List[str]] = Field(default=None, description="Include patterns")
    exclude_patterns: Optional[List[str]] = Field(default=None, description="Exclude patterns")
    output_format: Optional[str] = Field(default="json", description="Output format")

class CodeRefactorParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    refactor_type: str = Field(description="Refactor type (rename, extract_method, move_class, etc.)")
    target_file: str = Field(description="Target file path")
    old_name: Optional[str] = Field(default=None, description="Old name for rename operations")
    new_name: Optional[str] = Field(default=None, description="New name for rename operations")
    start_line: Optional[int] = Field(default=None, description="Start line for extraction")
    end_line: Optional[int] = Field(default=None, description="End line for extraction")
    target_namespace: Optional[str] = Field(default=None, description="Target namespace for move operations")

class DocumentationParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    doc_type: str = Field(description="Documentation type (xml, markdown, html)")
    target_files: Optional[List[str]] = Field(default=None, description="Target files")
    output_path: str = Field(description="Output path for documentation")
    include_private: Optional[bool] = Field(default=False, description="Include private members")
    include_internal: Optional[bool] = Field(default=False, description="Include internal members")
    template_path: Optional[str] = Field(default=None, description="Custom template path")
    generate_diagrams: Optional[bool] = Field(default=False, description="Generate UML diagrams")


# Performance & Profiling Parameter Models (2 tools)
class ProfilerDataParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    profiler_type: str = Field(description="Profiler type (cpu, memory, rendering, audio, physics)")
    duration: Optional[float] = Field(default=10.0, description="Profiling duration in seconds")
    target_scene: Optional[str] = Field(default=None, description="Target scene to profile")
    sample_rate: Optional[int] = Field(default=300, description="Sample rate in Hz")
    deep_profiling: Optional[bool] = Field(default=False, description="Enable deep profiling")
    output_format: Optional[str] = Field(default="json", description="Output format (json, csv, binary)")
    output_path: Optional[str] = Field(default=None, description="Output file path")

class PerformanceAnalysisParams(BaseModel):
    project_path: str = Field(description="Path to Unity project")
    analysis_type: str = Field(description="Analysis type (frame_time, memory_usage, draw_calls, batches)")
    target_platform: Optional[str] = Field(default="standalone", description="Target platform")
    quality_settings: Optional[str] = Field(default=None, description="Quality settings level")
    resolution: Optional[str] = Field(default=None, description="Screen resolution")
    vsync: Optional[bool] = Field(default=True, description="Enable VSync")
    target_framerate: Optional[int] = Field(default=60, description="Target framerate")
    benchmark_duration: Optional[float] = Field(default=30.0, description="Benchmark duration in seconds")


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
    
    # Scene Management Tools (10 tools)
    @mcp.tool()
    async def scene_load(params: SceneLoadParams) -> Dict[str, Any]:
        """Load a Unity scene in the editor"""
        try:
            logger.info(f"Loading scene {params.scene_path}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.load",
                project_path=params.project_path,
                parameters={
                    "scenePath": params.scene_path,
                    "additive": params.additive
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_path": params.scene_path,
                "additive": params.additive
            }
            
        except Exception as e:
            logger.error(f"Scene load failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_save(params: SceneSaveParams) -> Dict[str, Any]:
        """Save the current Unity scene"""
        try:
            logger.info(f"Saving scene for {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.save",
                project_path=params.project_path,
                parameters={
                    "scenePath": params.scene_path,
                    "saveAs": params.save_as
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_path": params.scene_path or "current"
            }
            
        except Exception as e:
            logger.error(f"Scene save failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_create(params: SceneCreateParams) -> Dict[str, Any]:
        """Create a new Unity scene"""
        try:
            logger.info(f"Creating new scene {params.scene_name}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.create",
                project_path=params.project_path,
                parameters={
                    "sceneName": params.scene_name,
                    "template": params.template
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_name": params.scene_name
            }
            
        except Exception as e:
            logger.error(f"Scene creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_hierarchy(params: SceneHierarchyParams) -> Dict[str, Any]:
        """Get Unity scene hierarchy information"""
        try:
            logger.info(f"Getting scene hierarchy for {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.hierarchy",
                project_path=params.project_path,
                parameters={
                    "scenePath": params.scene_path,
                    "filterType": params.filter_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_path": params.scene_path or "current"
            }
            
        except Exception as e:
            logger.error(f"Scene hierarchy failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def lighting_settings(params: LightingSettingsParams) -> Dict[str, Any]:
        """Configure Unity lighting settings for a scene"""
        try:
            logger.info(f"Configuring lighting settings for {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="lighting.settings",
                project_path=params.project_path,
                parameters={
                    "scenePath": params.scene_path,
                    "settings": params.settings
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_path": params.scene_path or "current"
            }
            
        except Exception as e:
            logger.error(f"Lighting settings failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_merge(params: SceneMergeParams) -> Dict[str, Any]:
        """Merge two Unity scenes together"""
        try:
            logger.info(f"Merging scenes {params.source_scene} into {params.target_scene}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.merge",
                project_path=params.project_path,
                parameters={
                    "sourceScene": params.source_scene,
                    "targetScene": params.target_scene,
                    "mergeMode": params.merge_mode
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "source_scene": params.source_scene,
                "target_scene": params.target_scene
            }
            
        except Exception as e:
            logger.error(f"Scene merge failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_compare(params: SceneCompareParams) -> Dict[str, Any]:
        """Compare two Unity scenes and find differences"""
        try:
            logger.info(f"Comparing scenes {params.scene_a} and {params.scene_b}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.compare",
                project_path=params.project_path,
                parameters={
                    "sceneA": params.scene_a,
                    "sceneB": params.scene_b,
                    "compareType": params.compare_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_a": params.scene_a,
                "scene_b": params.scene_b
            }
            
        except Exception as e:
            logger.error(f"Scene comparison failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_optimize(params: SceneOptimizeParams) -> Dict[str, Any]:
        """Optimize Unity scene for better performance"""
        try:
            logger.info(f"Optimizing scene {params.scene_path}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.optimize",
                project_path=params.project_path,
                parameters={
                    "scenePath": params.scene_path,
                    "optimizationLevel": params.optimization_level
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_path": params.scene_path,
                "optimization_level": params.optimization_level
            }
            
        except Exception as e:
            logger.error(f"Scene optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_backup(params: SceneBackupParams) -> Dict[str, Any]:
        """Create a backup of Unity scene"""
        try:
            logger.info(f"Creating backup of scene {params.scene_path}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.backup",
                project_path=params.project_path,
                parameters={
                    "scenePath": params.scene_path,
                    "backupPath": params.backup_path
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_path": params.scene_path,
                "backup_path": params.backup_path
            }
            
        except Exception as e:
            logger.error(f"Scene backup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def scene_statistics(params: SceneStatisticsParams) -> Dict[str, Any]:
        """Get detailed statistics about Unity scene"""
        try:
            logger.info(f"Getting scene statistics for {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="scene.statistics",
                project_path=params.project_path,
                parameters={
                    "scenePath": params.scene_path,
                    "includeAssets": params.include_assets
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "scene_path": params.scene_path or "current"
            }
            
        except Exception as e:
            logger.error(f"Scene statistics failed: {e}")
            return {
                 "success": False,
                 "error": str(e)
             }
    
    # GameObject Operations Tools (15 tools)
    @mcp.tool()
    async def gameobject_create(params: GameObjectCreateParams) -> Dict[str, Any]:
        """Create a new GameObject in Unity scene"""
        try:
            logger.info(f"Creating GameObject {params.name}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.create",
                project_path=params.project_path,
                parameters={
                    "name": params.name,
                    "parentPath": params.parent_path,
                    "primitiveType": params.primitive_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "name": params.name,
                "parent_path": params.parent_path
            }
            
        except Exception as e:
            logger.error(f"GameObject creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_delete(params: GameObjectDeleteParams) -> Dict[str, Any]:
        """Delete a GameObject from Unity scene"""
        try:
            logger.info(f"Deleting GameObject {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.delete",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "confirm": params.confirm
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path
            }
            
        except Exception as e:
            logger.error(f"GameObject deletion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_find(params: GameObjectFindParams) -> Dict[str, Any]:
        """Find GameObjects in Unity scene by various criteria"""
        try:
            logger.info(f"Finding GameObjects with query: {params.search_query}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.find",
                project_path=params.project_path,
                parameters={
                    "searchQuery": params.search_query,
                    "searchType": params.search_type,
                    "scenePath": params.scene_path
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "search_query": params.search_query,
                "search_type": params.search_type
            }
            
        except Exception as e:
            logger.error(f"GameObject search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_transform(params: GameObjectTransformParams) -> Dict[str, Any]:
        """Modify GameObject transform (position, rotation, scale)"""
        try:
            logger.info(f"Transforming GameObject {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.transform",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "position": params.position,
                    "rotation": params.rotation,
                    "scale": params.scale
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path
            }
            
        except Exception as e:
            logger.error(f"GameObject transform failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_parent(params: GameObjectParentParams) -> Dict[str, Any]:
        """Set parent-child relationship between GameObjects"""
        try:
            logger.info(f"Setting parent for {params.child_path}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.parent",
                project_path=params.project_path,
                parameters={
                    "childPath": params.child_path,
                    "parentPath": params.parent_path
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "child_path": params.child_path,
                "parent_path": params.parent_path
            }
            
        except Exception as e:
            logger.error(f"GameObject parenting failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_duplicate(params: GameObjectDuplicateParams) -> Dict[str, Any]:
        """Duplicate a GameObject in Unity scene"""
        try:
            logger.info(f"Duplicating GameObject {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.duplicate",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "count": params.count,
                    "offset": params.offset
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "count": params.count
            }
            
        except Exception as e:
            logger.error(f"GameObject duplication failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_rename(params: GameObjectRenameParams) -> Dict[str, Any]:
        """Rename a GameObject in Unity scene"""
        try:
            logger.info(f"Renaming GameObject {params.object_path} to {params.new_name}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.rename",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "newName": params.new_name
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "new_name": params.new_name
            }
            
        except Exception as e:
            logger.error(f"GameObject rename failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_tag(params: GameObjectTagParams) -> Dict[str, Any]:
        """Set tag for a GameObject"""
        try:
            logger.info(f"Setting tag {params.tag} for {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.tag",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "tag": params.tag
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "tag": params.tag
            }
            
        except Exception as e:
            logger.error(f"GameObject tag setting failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_layer(params: GameObjectLayerParams) -> Dict[str, Any]:
        """Set layer for a GameObject"""
        try:
            logger.info(f"Setting layer {params.layer} for {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.layer",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "layer": params.layer
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "layer": params.layer
            }
            
        except Exception as e:
            logger.error(f"GameObject layer setting failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_active(params: GameObjectActiveParams) -> Dict[str, Any]:
        """Set active state for a GameObject"""
        try:
            logger.info(f"Setting active {params.active} for {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.active",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "active": params.active
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "active": params.active
            }
            
        except Exception as e:
            logger.error(f"GameObject active setting failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def prefab_create(params: PrefabCreateParams) -> Dict[str, Any]:
        """Create a prefab from a GameObject"""
        try:
            logger.info(f"Creating prefab from {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="prefab.create",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "prefabPath": params.prefab_path,
                    "replaceOriginal": params.replace_original
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "prefab_path": params.prefab_path
            }
            
        except Exception as e:
            logger.error(f"Prefab creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def prefab_instantiate(params: PrefabInstantiateParams) -> Dict[str, Any]:
        """Instantiate a prefab in Unity scene"""
        try:
            logger.info(f"Instantiating prefab {params.prefab_path}")
            
            result = await unity_manager.execute_unity_command(
                action="prefab.instantiate",
                project_path=params.project_path,
                parameters={
                    "prefabPath": params.prefab_path,
                    "parentPath": params.parent_path,
                    "position": params.position,
                    "rotation": params.rotation
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "prefab_path": params.prefab_path,
                "parent_path": params.parent_path
            }
            
        except Exception as e:
            logger.error(f"Prefab instantiation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def prefab_unpack(params: PrefabUnpackParams) -> Dict[str, Any]:
        """Unpack a prefab instance in Unity scene"""
        try:
            logger.info(f"Unpacking prefab instance {params.prefab_instance_path}")
            
            result = await unity_manager.execute_unity_command(
                action="prefab.unpack",
                project_path=params.project_path,
                parameters={
                    "prefabInstancePath": params.prefab_instance_path,
                    "unpackMode": params.unpack_mode
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "prefab_instance_path": params.prefab_instance_path,
                "unpack_mode": params.unpack_mode
            }
            
        except Exception as e:
            logger.error(f"Prefab unpacking failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_group(params: GameObjectGroupParams) -> Dict[str, Any]:
        """Group multiple GameObjects under a parent"""
        try:
            logger.info(f"Grouping {len(params.object_paths)} GameObjects")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.group",
                project_path=params.project_path,
                parameters={
                    "objectPaths": params.object_paths,
                    "groupName": params.group_name
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_paths": params.object_paths,
                "group_name": params.group_name
            }
            
        except Exception as e:
            logger.error(f"GameObject grouping failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def gameobject_align(params: GameObjectAlignParams) -> Dict[str, Any]:
        """Align multiple GameObjects"""
        try:
            logger.info(f"Aligning {len(params.object_paths)} GameObjects")
            
            result = await unity_manager.execute_unity_command(
                action="gameobject.align",
                project_path=params.project_path,
                parameters={
                    "objectPaths": params.object_paths,
                    "alignType": params.align_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_paths": params.object_paths,
                "align_type": params.align_type
            }
            
        except Exception as e:
            logger.error(f"GameObject alignment failed: {e}")
            return {
                 "success": False,
                 "error": str(e)
             }
    
    # Component Management Tools (10 tools)
    @mcp.tool()
    async def component_add(params: ComponentAddParams) -> Dict[str, Any]:
        """Add a component to a GameObject"""
        try:
            logger.info(f"Adding component {params.component_type} to {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.add",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "componentType": params.component_type,
                    "parameters": params.parameters or {}
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "component_type": params.component_type
            }
            
        except Exception as e:
            logger.error(f"Component addition failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_remove(params: ComponentRemoveParams) -> Dict[str, Any]:
        """Remove a component from a GameObject"""
        try:
            logger.info(f"Removing component {params.component_type} from {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.remove",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "componentType": params.component_type,
                    "confirm": params.confirm
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "component_type": params.component_type
            }
            
        except Exception as e:
            logger.error(f"Component removal failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_get(params: ComponentGetParams) -> Dict[str, Any]:
        """Get component information from a GameObject"""
        try:
            logger.info(f"Getting components from {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.get",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "componentType": params.component_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "component_type": params.component_type
            }
            
        except Exception as e:
            logger.error(f"Component retrieval failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_set_property(params: ComponentSetPropertyParams) -> Dict[str, Any]:
        """Set a property value on a component"""
        try:
            logger.info(f"Setting property {params.property_name} on {params.component_type}")
            
            result = await unity_manager.execute_unity_command(
                action="component.setProperty",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "componentType": params.component_type,
                    "propertyName": params.property_name,
                    "propertyValue": params.property_value
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "component_type": params.component_type,
                "property_name": params.property_name
            }
            
        except Exception as e:
            logger.error(f"Component property setting failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_copy(params: ComponentCopyParams) -> Dict[str, Any]:
        """Copy a component from one GameObject to another"""
        try:
            logger.info(f"Copying component {params.component_type} from {params.source_object_path} to {params.target_object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.copy",
                project_path=params.project_path,
                parameters={
                    "sourceObjectPath": params.source_object_path,
                    "targetObjectPath": params.target_object_path,
                    "componentType": params.component_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "source_object_path": params.source_object_path,
                "target_object_path": params.target_object_path,
                "component_type": params.component_type
            }
            
        except Exception as e:
            logger.error(f"Component copying failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_serialize(params: ComponentSerializeParams) -> Dict[str, Any]:
        """Serialize a component to file"""
        try:
            logger.info(f"Serializing component {params.component_type} from {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.serialize",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "componentType": params.component_type,
                    "outputPath": params.output_path
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "component_type": params.component_type,
                "output_path": params.output_path
            }
            
        except Exception as e:
            logger.error(f"Component serialization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_deserialize(params: ComponentDeserializeParams) -> Dict[str, Any]:
        """Deserialize a component from file"""
        try:
            logger.info(f"Deserializing component to {params.object_path} from {params.input_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.deserialize",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "inputPath": params.input_path,
                    "overwrite": params.overwrite
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "input_path": params.input_path
            }
            
        except Exception as e:
            logger.error(f"Component deserialization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_validate(params: ComponentValidateParams) -> Dict[str, Any]:
        """Validate components in scene or specific GameObject"""
        try:
            logger.info(f"Validating components in project {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.validate",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "componentType": params.component_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "component_type": params.component_type
            }
            
        except Exception as e:
            logger.error(f"Component validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_reset(params: ComponentResetParams) -> Dict[str, Any]:
        """Reset a component to default values"""
        try:
            logger.info(f"Resetting component {params.component_type} on {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.reset",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "componentType": params.component_type,
                    "confirm": params.confirm
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "component_type": params.component_type
            }
            
        except Exception as e:
            logger.error(f"Component reset failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def component_enable(params: ComponentEnableParams) -> Dict[str, Any]:
        """Enable or disable a component"""
        try:
            logger.info(f"Setting component {params.component_type} enabled={params.enabled} on {params.object_path}")
            
            result = await unity_manager.execute_unity_command(
                action="component.enable",
                project_path=params.project_path,
                parameters={
                    "objectPath": params.object_path,
                    "componentType": params.component_type,
                    "enabled": params.enabled
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "object_path": params.object_path,
                "component_type": params.component_type,
                "enabled": params.enabled
            }
            
        except Exception as e:
            logger.error(f"Component enable/disable failed: {e}")
            return {
                 "success": False,
                 "error": str(e)
             }
    
    # Asset Management Tools (15 tools)
    @mcp.tool()
    async def asset_import(params: AssetImportParams) -> Dict[str, Any]:
        """Import an asset into Unity project"""
        try:
            logger.info(f"Importing asset {params.asset_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.import",
                project_path=params.project_path,
                parameters={
                    "assetPath": params.asset_path,
                    "importSettings": params.import_settings or {},
                    "forceReimport": params.force_reimport
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "asset_path": params.asset_path
            }
            
        except Exception as e:
            logger.error(f"Asset import failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_export(params: AssetExportParams) -> Dict[str, Any]:
        """Export an asset from Unity project"""
        try:
            logger.info(f"Exporting asset {params.asset_path} to {params.export_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.export",
                project_path=params.project_path,
                parameters={
                    "assetPath": params.asset_path,
                    "exportPath": params.export_path,
                    "exportFormat": params.export_format,
                    "exportSettings": params.export_settings or {}
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "asset_path": params.asset_path,
                "export_path": params.export_path
            }
            
        except Exception as e:
            logger.error(f"Asset export failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_database_refresh(params: AssetDatabaseRefreshParams) -> Dict[str, Any]:
        """Refresh Unity Asset Database"""
        try:
            logger.info(f"Refreshing Asset Database for {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.database.refresh",
                project_path=params.project_path,
                parameters={
                    "forceRefresh": params.force_refresh,
                    "importMode": params.import_mode
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "force_refresh": params.force_refresh
            }
            
        except Exception as e:
            logger.error(f"Asset database refresh failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_search(params: AssetSearchParams) -> Dict[str, Any]:
        """Search for assets in Unity project"""
        try:
            logger.info(f"Searching assets with filter: {params.search_filter}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.search",
                project_path=params.project_path,
                parameters={
                    "searchFilter": params.search_filter,
                    "assetType": params.asset_type,
                    "folderPath": params.folder_path
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "search_filter": params.search_filter
            }
            
        except Exception as e:
            logger.error(f"Asset search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_move(params: AssetMoveParams) -> Dict[str, Any]:
        """Move an asset to a new location"""
        try:
            logger.info(f"Moving asset from {params.source_path} to {params.destination_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.move",
                project_path=params.project_path,
                parameters={
                    "sourcePath": params.source_path,
                    "destinationPath": params.destination_path,
                    "overwrite": params.overwrite
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "source_path": params.source_path,
                "destination_path": params.destination_path
            }
            
        except Exception as e:
            logger.error(f"Asset move failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_delete(params: AssetDeleteParams) -> Dict[str, Any]:
        """Delete an asset from Unity project"""
        try:
            logger.info(f"Deleting asset {params.asset_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.delete",
                project_path=params.project_path,
                parameters={
                    "assetPath": params.asset_path,
                    "confirm": params.confirm
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "asset_path": params.asset_path
            }
            
        except Exception as e:
            logger.error(f"Asset deletion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def texture_import(params: TextureImportParams) -> Dict[str, Any]:
        """Import texture with specific settings"""
        try:
            logger.info(f"Importing texture {params.texture_path}")
            
            result = await unity_manager.execute_unity_command(
                action="texture.import",
                project_path=params.project_path,
                parameters={
                    "texturePath": params.texture_path,
                    "textureType": params.texture_type,
                    "maxSize": params.max_size,
                    "compression": params.compression,
                    "generateMipmaps": params.generate_mipmaps
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "texture_path": params.texture_path,
                "texture_type": params.texture_type
            }
            
        except Exception as e:
            logger.error(f"Texture import failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def mesh_import(params: MeshImportParams) -> Dict[str, Any]:
        """Import mesh with specific settings"""
        try:
            logger.info(f"Importing mesh {params.mesh_path}")
            
            result = await unity_manager.execute_unity_command(
                action="mesh.import",
                project_path=params.project_path,
                parameters={
                    "meshPath": params.mesh_path,
                    "scaleFactor": params.scale_factor,
                    "generateColliders": params.generate_colliders,
                    "optimizeMesh": params.optimize_mesh,
                    "importMaterials": params.import_materials
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "mesh_path": params.mesh_path,
                "scale_factor": params.scale_factor
            }
            
        except Exception as e:
            logger.error(f"Mesh import failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def audio_import(params: AudioImportParams) -> Dict[str, Any]:
        """Import audio with specific settings"""
        try:
            logger.info(f"Importing audio {params.audio_path}")
            
            result = await unity_manager.execute_unity_command(
                action="audio.import",
                project_path=params.project_path,
                parameters={
                    "audioPath": params.audio_path,
                    "audioFormat": params.audio_format,
                    "quality": params.quality,
                    "loadType": params.load_type,
                    "forceMono": params.force_mono
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "audio_path": params.audio_path,
                "audio_format": params.audio_format
            }
            
        except Exception as e:
            logger.error(f"Audio import failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_bundle_create(params: AssetBundleCreateParams) -> Dict[str, Any]:
        """Create an asset bundle"""
        try:
            logger.info(f"Creating asset bundle {params.bundle_name}")
            
            result = await unity_manager.execute_unity_command(
                action="assetbundle.create",
                project_path=params.project_path,
                parameters={
                    "bundleName": params.bundle_name,
                    "assetPaths": params.asset_paths,
                    "buildTarget": params.build_target,
                    "outputPath": params.output_path
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "bundle_name": params.bundle_name,
                "output_path": params.output_path
            }
            
        except Exception as e:
            logger.error(f"Asset bundle creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_bundle_build(params: AssetBundleBuildParams) -> Dict[str, Any]:
        """Build all asset bundles"""
        try:
            logger.info(f"Building asset bundles for {params.build_target}")
            
            result = await unity_manager.execute_unity_command(
                action="assetbundle.build",
                project_path=params.project_path,
                parameters={
                    "outputPath": params.output_path,
                    "buildTarget": params.build_target,
                    "buildOptions": params.build_options or []
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "output_path": params.output_path,
                "build_target": params.build_target
            }
            
        except Exception as e:
            logger.error(f"Asset bundle build failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_dependency(params: AssetDependencyParams) -> Dict[str, Any]:
        """Get asset dependencies"""
        try:
            logger.info(f"Getting dependencies for {params.asset_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.dependency",
                project_path=params.project_path,
                parameters={
                    "assetPath": params.asset_path,
                    "includeIndirect": params.include_indirect
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "asset_path": params.asset_path,
                "include_indirect": params.include_indirect
            }
            
        except Exception as e:
            logger.error(f"Asset dependency analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_metadata(params: AssetMetadataParams) -> Dict[str, Any]:
        """Get or set asset metadata"""
        try:
            if params.metadata_value is not None:
                logger.info(f"Setting metadata {params.metadata_key} for {params.asset_path}")
                action = "asset.metadata.set"
            else:
                logger.info(f"Getting metadata for {params.asset_path}")
                action = "asset.metadata.get"
            
            result = await unity_manager.execute_unity_command(
                action=action,
                project_path=params.project_path,
                parameters={
                    "assetPath": params.asset_path,
                    "metadataKey": params.metadata_key,
                    "metadataValue": params.metadata_value
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "asset_path": params.asset_path,
                "metadata_key": params.metadata_key
            }
            
        except Exception as e:
            logger.error(f"Asset metadata operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_validate(params: AssetValidateParams) -> Dict[str, Any]:
        """Validate assets for issues"""
        try:
            logger.info(f"Validating assets in {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.validate",
                project_path=params.project_path,
                parameters={
                    "assetPath": params.asset_path,
                    "validationType": params.validation_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "asset_path": params.asset_path,
                "validation_type": params.validation_type
            }
            
        except Exception as e:
            logger.error(f"Asset validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def asset_optimize(params: AssetOptimizeParams) -> Dict[str, Any]:
        """Optimize assets for better performance"""
        try:
            logger.info(f"Optimizing assets in {params.project_path}")
            
            result = await unity_manager.execute_unity_command(
                action="asset.optimize",
                project_path=params.project_path,
                parameters={
                    "assetPath": params.asset_path,
                    "optimizationType": params.optimization_type,
                    "backup": params.backup
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "asset_path": params.asset_path,
                "optimization_type": params.optimization_type
            }
            
        except Exception as e:
            logger.error(f"Asset optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Animation & Timeline Tools (10 tools)
    @mcp.tool()
    async def animation_clip_create(params: AnimationClipCreateParams) -> Dict[str, Any]:
        """Create a new animation clip"""
        try:
            logger.info(f"Creating animation clip {params.clip_name}")
            
            result = await unity_manager.execute_unity_command(
                action="animation.clip.create",
                project_path=params.project_path,
                parameters={
                    "clipName": params.clip_name,
                    "duration": params.duration,
                    "frameRate": params.frame_rate,
                    "loop": params.loop
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "clip_name": params.clip_name,
                "duration": params.duration
            }
            
        except Exception as e:
            logger.error(f"Animation clip creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def animation_clip_edit(params: AnimationClipEditParams) -> Dict[str, Any]:
        """Edit animation clip keyframes and curves"""
        try:
            logger.info(f"Editing animation clip {params.clip_path}")
            
            result = await unity_manager.execute_unity_command(
                action="animation.clip.edit",
                project_path=params.project_path,
                parameters={
                    "clipPath": params.clip_path,
                    "propertyPath": params.property_path,
                    "keyframes": params.keyframes,
                    "curveType": params.curve_type
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "clip_path": params.clip_path,
                "property_path": params.property_path
            }
            
        except Exception as e:
            logger.error(f"Animation clip edit failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def animator_controller_create(params: AnimatorControllerCreateParams) -> Dict[str, Any]:
        """Create a new Animator Controller"""
        try:
            logger.info(f"Creating animator controller {params.controller_name}")
            
            result = await unity_manager.execute_unity_command(
                action="animator.controller.create",
                project_path=params.project_path,
                parameters={
                    "controllerName": params.controller_name,
                    "outputPath": params.output_path,
                    "layers": params.layers or [],
                    "parameters": params.parameters or []
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "controller_name": params.controller_name,
                "output_path": params.output_path
            }
            
        except Exception as e:
            logger.error(f"Animator controller creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def animator_state(params: AnimatorStateParams) -> Dict[str, Any]:
        """Add or modify animator state"""
        try:
            logger.info(f"Managing animator state {params.state_name}")
            
            result = await unity_manager.execute_unity_command(
                action="animator.state",
                project_path=params.project_path,
                parameters={
                    "controllerPath": params.controller_path,
                    "layerName": params.layer_name,
                    "stateName": params.state_name,
                    "animationClip": params.animation_clip,
                    "position": params.position
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "state_name": params.state_name,
                "layer_name": params.layer_name
            }
            
        except Exception as e:
            logger.error(f"Animator state operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def animator_transition(params: AnimatorTransitionParams) -> Dict[str, Any]:
        """Create animator state transition"""
        try:
            logger.info(f"Creating transition from {params.from_state} to {params.to_state}")
            
            result = await unity_manager.execute_unity_command(
                action="animator.transition",
                project_path=params.project_path,
                parameters={
                    "controllerPath": params.controller_path,
                    "layerName": params.layer_name,
                    "fromState": params.from_state,
                    "toState": params.to_state,
                    "conditions": params.conditions or [],
                    "duration": params.duration
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "from_state": params.from_state,
                "to_state": params.to_state
            }
            
        except Exception as e:
            logger.error(f"Animator transition creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def timeline_create(params: TimelineCreateParams) -> Dict[str, Any]:
        """Create a new Timeline asset"""
        try:
            logger.info(f"Creating timeline {params.timeline_name}")
            
            result = await unity_manager.execute_unity_command(
                action="timeline.create",
                project_path=params.project_path,
                parameters={
                    "timelineName": params.timeline_name,
                    "outputPath": params.output_path,
                    "duration": params.duration,
                    "frameRate": params.frame_rate
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "timeline_name": params.timeline_name,
                "output_path": params.output_path
            }
            
        except Exception as e:
            logger.error(f"Timeline creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def timeline_track(params: TimelineTrackParams) -> Dict[str, Any]:
        """Add or modify timeline track"""
        try:
            logger.info(f"Managing timeline track {params.track_name}")
            
            result = await unity_manager.execute_unity_command(
                action="timeline.track",
                project_path=params.project_path,
                parameters={
                    "timelinePath": params.timeline_path,
                    "trackName": params.track_name,
                    "trackType": params.track_type,
                    "bindingObject": params.binding_object
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "track_name": params.track_name,
                "track_type": params.track_type
            }
            
        except Exception as e:
            logger.error(f"Timeline track operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def timeline_clip(params: TimelineClipParams) -> Dict[str, Any]:
        """Add or modify timeline clip"""
        try:
            logger.info(f"Managing timeline clip {params.clip_name}")
            
            result = await unity_manager.execute_unity_command(
                action="timeline.clip",
                project_path=params.project_path,
                parameters={
                    "timelinePath": params.timeline_path,
                    "trackName": params.track_name,
                    "clipName": params.clip_name,
                    "startTime": params.start_time,
                    "duration": params.duration,
                    "assetPath": params.asset_path
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "clip_name": params.clip_name,
                "track_name": params.track_name
            }
            
        except Exception as e:
            logger.error(f"Timeline clip operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def animation_record(params: AnimationRecordParams) -> Dict[str, Any]:
        """Record animation from GameObject"""
        try:
            logger.info(f"Recording animation for {params.target_object}")
            
            result = await unity_manager.execute_unity_command(
                action="animation.record",
                project_path=params.project_path,
                parameters={
                    "targetObject": params.target_object,
                    "clipName": params.clip_name,
                    "properties": params.properties,
                    "duration": params.duration,
                    "autoKey": params.auto_key
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "target_object": params.target_object,
                "clip_name": params.clip_name
            }
            
        except Exception as e:
            logger.error(f"Animation recording failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def animation_bake(params: AnimationBakeParams) -> Dict[str, Any]:
        """Bake animation from GameObject to clip"""
        try:
            logger.info(f"Baking animation from {params.source_object}")
            
            result = await unity_manager.execute_unity_command(
                action="animation.bake",
                project_path=params.project_path,
                parameters={
                    "sourceObject": params.source_object,
                    "targetClip": params.target_clip,
                    "frameRange": params.frame_range,
                    "sampleRate": params.sample_rate,
                    "bakePose": params.bake_pose
                }
            )
            
            return {
                "success": True,
                "data": result.get("Data", {}),
                "source_object": params.source_object,
                "target_clip": params.target_clip
            }
            
        except Exception as e:
            logger.error(f"Animation baking failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Physics & Collision Tools (8 tools)
    @mcp.tool()
    async def rigidbody_configure(params: RigidbodyParams) -> str:
        """Configure Rigidbody component properties"""
        try:
            command = {
                "action": "rigidbody_configure",
                "gameobject_path": params.gameobject_path,
                "mass": params.mass,
                "drag": params.drag,
                "angular_drag": params.angular_drag,
                "use_gravity": params.use_gravity,
                "is_kinematic": params.is_kinematic,
                "freeze_rotation": params.freeze_rotation
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Rigidbody configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring rigidbody: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def collider_manage(params: ColliderParams) -> str:
        """Add, modify, or configure collider components"""
        try:
            command = {
                "action": "collider_manage",
                "gameobject_path": params.gameobject_path,
                "collider_type": params.collider_type,
                "is_trigger": params.is_trigger,
                "material": params.material,
                "size": params.size,
                "center": params.center
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Collider managed: {result}"
        except Exception as e:
            logger.error(f"Error managing collider: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def physics_material_create(params: PhysicsMaterialParams) -> str:
        """Create and configure physics materials"""
        try:
            command = {
                "action": "physics_material_create",
                "material_name": params.material_name,
                "output_path": params.output_path,
                "dynamic_friction": params.dynamic_friction,
                "static_friction": params.static_friction,
                "bounciness": params.bounciness,
                "friction_combine": params.friction_combine,
                "bounce_combine": params.bounce_combine
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Physics material created: {result}"
        except Exception as e:
            logger.error(f"Error creating physics material: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def joint_configure(params: JointParams) -> str:
        """Configure joint components and connections"""
        try:
            command = {
                "action": "joint_configure",
                "gameobject_path": params.gameobject_path,
                "joint_type": params.joint_type,
                "connected_body": params.connected_body,
                "anchor": params.anchor,
                "axis": params.axis,
                "limits": params.limits,
                "spring": params.spring
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Joint configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring joint: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def physics_simulation_settings(params: PhysicsSimulationParams) -> str:
        """Configure global physics simulation settings"""
        try:
            command = {
                "action": "physics_simulation_settings",
                "gravity": params.gravity,
                "default_material": params.default_material,
                "bounce_threshold": params.bounce_threshold,
                "sleep_threshold": params.sleep_threshold,
                "default_contact_offset": params.default_contact_offset,
                "solver_iterations": params.solver_iterations,
                "solver_velocity_iterations": params.solver_velocity_iterations
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Physics simulation settings configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring physics simulation: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def physics_raycast(params: RaycastParams) -> str:
        """Perform physics raycasting operations"""
        try:
            command = {
                "action": "physics_raycast",
                "origin": params.origin,
                "direction": params.direction,
                "max_distance": params.max_distance,
                "layer_mask": params.layer_mask,
                "query_trigger_interaction": params.query_trigger_interaction
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Raycast performed: {result}"
        except Exception as e:
            logger.error(f"Error performing raycast: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def physics_overlap(params: OverlapParams) -> str:
        """Perform physics overlap detection"""
        try:
            command = {
                "action": "physics_overlap",
                "shape_type": params.shape_type,
                "position": params.position,
                "size": params.size,
                "layer_mask": params.layer_mask,
                "query_trigger_interaction": params.query_trigger_interaction
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Overlap detection performed: {result}"
        except Exception as e:
            logger.error(f"Error performing overlap detection: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def physics_debug(params: PhysicsDebugParams) -> str:
        """Configure physics debugging and visualization"""
        try:
            command = {
                "action": "physics_debug",
                "debug_type": params.debug_type,
                "enable": params.enable,
                "color": params.color,
                "duration": params.duration
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Physics debug configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring physics debug: {e}")
            return f"Error: {str(e)}"

    # Rendering & Graphics Tools (10 tools)
    @mcp.tool()
    async def material_create(params: MaterialParams) -> str:
        """Create and configure materials"""
        try:
            command = {
                "action": "material_create",
                "material_name": params.material_name,
                "output_path": params.output_path,
                "shader_name": params.shader_name,
                "properties": params.properties,
                "textures": params.textures,
                "keywords": params.keywords
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Material created: {result}"
        except Exception as e:
            logger.error(f"Error creating material: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def shader_create(params: ShaderParams) -> str:
        """Create and manage shaders"""
        try:
            command = {
                "action": "shader_create",
                "shader_name": params.shader_name,
                "output_path": params.output_path,
                "shader_type": params.shader_type,
                "properties": params.properties,
                "passes": params.passes,
                "includes": params.includes
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Shader created: {result}"
        except Exception as e:
            logger.error(f"Error creating shader: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def camera_configure(params: CameraParams) -> str:
        """Configure camera settings and properties"""
        try:
            command = {
                "action": "camera_configure",
                "gameobject_path": params.gameobject_path,
                "clear_flags": params.clear_flags,
                "background_color": params.background_color,
                "culling_mask": params.culling_mask,
                "projection": params.projection,
                "field_of_view": params.field_of_view,
                "near_clip": params.near_clip,
                "far_clip": params.far_clip,
                "render_texture": params.render_texture
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Camera configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring camera: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def lighting_setup(params: LightingParams) -> str:
        """Setup and configure lighting"""
        try:
            command = {
                "action": "lighting_setup",
                "lighting_type": params.lighting_type,
                "gameobject_path": params.gameobject_path,
                "intensity": params.intensity,
                "color": params.color,
                "range": params.range,
                "spot_angle": params.spot_angle,
                "shadows": params.shadows,
                "baking_settings": params.baking_settings
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Lighting setup: {result}"
        except Exception as e:
            logger.error(f"Error setting up lighting: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def postprocessing_configure(params: PostProcessingParams) -> str:
        """Configure post-processing effects"""
        try:
            command = {
                "action": "postprocessing_configure",
                "profile_name": params.profile_name,
                "output_path": params.output_path,
                "effects": params.effects,
                "volume_gameobject": params.volume_gameobject,
                "is_global": params.is_global,
                "priority": params.priority
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Post-processing configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring post-processing: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def render_pipeline_setup(params: RenderPipelineParams) -> str:
        """Setup and configure render pipeline"""
        try:
            command = {
                "action": "render_pipeline_setup",
                "pipeline_type": params.pipeline_type,
                "asset_name": params.asset_name,
                "output_path": params.output_path,
                "settings": params.settings,
                "renderer_features": params.renderer_features
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Render pipeline setup: {result}"
        except Exception as e:
            logger.error(f"Error setting up render pipeline: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def texture_configure(params: TextureParams) -> str:
        """Configure texture import settings"""
        try:
            command = {
                "action": "texture_configure",
                "texture_path": params.texture_path,
                "texture_type": params.texture_type,
                "max_size": params.max_size,
                "compression": params.compression,
                "filter_mode": params.filter_mode,
                "wrap_mode": params.wrap_mode,
                "generate_mipmaps": params.generate_mipmaps,
                "srgb_texture": params.srgb_texture
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Texture configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring texture: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def mesh_configure(params: MeshParams) -> str:
        """Configure mesh import settings"""
        try:
            command = {
                "action": "mesh_configure",
                "mesh_path": params.mesh_path,
                "scale_factor": params.scale_factor,
                "mesh_compression": params.mesh_compression,
                "read_write_enabled": params.read_write_enabled,
                "optimize_mesh": params.optimize_mesh,
                "generate_colliders": params.generate_colliders,
                "normals": params.normals,
                "tangents": params.tangents
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Mesh configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring mesh: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def lod_setup(params: LODParams) -> str:
        """Setup Level of Detail (LOD) groups"""
        try:
            command = {
                "action": "lod_setup",
                "gameobject_path": params.gameobject_path,
                "lod_levels": params.lod_levels,
                "fade_mode": params.fade_mode,
                "animate_cross_fading": params.animate_cross_fading
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"LOD setup: {result}"
        except Exception as e:
            logger.error(f"Error setting up LOD: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def culling_configure(params: CullingParams) -> str:
        """Configure rendering culling settings"""
        try:
            command = {
                "action": "culling_configure",
                "culling_type": params.culling_type,
                "gameobject_path": params.gameobject_path,
                "culling_distance": params.culling_distance,
                "occlusion_culling": params.occlusion_culling,
                "layer_distances": params.layer_distances
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Culling configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring culling: {e}")
            return f"Error: {str(e)}"

    # Audio System Tools (8 tools)
    @mcp.tool()
    async def audio_source_configure(params: AudioSourceParams) -> str:
        """Configure AudioSource component properties"""
        try:
            command = {
                "action": "audio_source_configure",
                "gameobject_path": params.gameobject_path,
                "audio_clip": params.audio_clip,
                "volume": params.volume,
                "pitch": params.pitch,
                "loop": params.loop,
                "play_on_awake": params.play_on_awake,
                "spatial_blend": params.spatial_blend,
                "min_distance": params.min_distance,
                "max_distance": params.max_distance,
                "rolloff_mode": params.rolloff_mode
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Audio source configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring audio source: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def audio_clip_configure(params: AudioClipParams) -> str:
        """Configure audio clip import settings"""
        try:
            command = {
                "action": "audio_clip_configure",
                "clip_path": params.clip_path,
                "load_type": params.load_type,
                "compression_format": params.compression_format,
                "quality": params.quality,
                "force_to_mono": params.force_to_mono,
                "normalize": params.normalize,
                "load_in_background": params.load_in_background,
                "ambisonic": params.ambisonic
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Audio clip configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring audio clip: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def audio_mixer_create(params: AudioMixerParams) -> str:
        """Create and configure audio mixer"""
        try:
            command = {
                "action": "audio_mixer_create",
                "mixer_name": params.mixer_name,
                "output_path": params.output_path,
                "groups": params.groups,
                "snapshots": params.snapshots,
                "exposed_parameters": params.exposed_parameters,
                "effects": params.effects
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Audio mixer created: {result}"
        except Exception as e:
            logger.error(f"Error creating audio mixer: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def audio_3d_configure(params: Audio3DParams) -> str:
        """Configure 3D audio settings"""
        try:
            command = {
                "action": "audio_3d_configure",
                "gameobject_path": params.gameobject_path,
                "doppler_level": params.doppler_level,
                "spread": params.spread,
                "volume_rolloff": params.volume_rolloff,
                "min_distance": params.min_distance,
                "max_distance": params.max_distance,
                "reverb_zone_mix": params.reverb_zone_mix
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"3D audio configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring 3D audio: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def reverb_zone_configure(params: ReverbZoneParams) -> str:
        """Configure AudioReverbZone component"""
        try:
            command = {
                "action": "reverb_zone_configure",
                "gameobject_path": params.gameobject_path,
                "min_distance": params.min_distance,
                "max_distance": params.max_distance,
                "reverb_preset": params.reverb_preset,
                "room": params.room,
                "room_hf": params.room_hf,
                "room_lf": params.room_lf,
                "decay_time": params.decay_time,
                "decay_hf_ratio": params.decay_hf_ratio,
                "reflections": params.reflections,
                "reflections_delay": params.reflections_delay,
                "reverb": params.reverb,
                "reverb_delay": params.reverb_delay,
                "hf_reference": params.hf_reference,
                "lf_reference": params.lf_reference,
                "diffusion": params.diffusion,
                "density": params.density
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Reverb zone configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring reverb zone: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def audio_listener_configure(params: AudioListenerParams) -> str:
        """Configure AudioListener component"""
        try:
            command = {
                "action": "audio_listener_configure",
                "gameobject_path": params.gameobject_path,
                "volume_scale": params.volume_scale,
                "pause_on_audio_focus_loss": params.pause_on_audio_focus_loss
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Audio listener configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring audio listener: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def audio_streaming_configure(params: AudioStreamingParams) -> str:
        """Configure audio streaming settings"""
        try:
            command = {
                "action": "audio_streaming_configure",
                "clip_path": params.clip_path,
                "streaming_enabled": params.streaming_enabled,
                "buffer_size": params.buffer_size,
                "preload_audio_data": params.preload_audio_data,
                "load_in_background": params.load_in_background
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Audio streaming configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring audio streaming: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def audio_compression_configure(params: AudioCompressionParams) -> str:
        """Configure audio compression settings"""
        try:
            command = {
                "action": "audio_compression_configure",
                "clip_path": params.clip_path,
                "compression_format": params.compression_format,
                "quality": params.quality,
                "sample_rate_setting": params.sample_rate_setting,
                "sample_rate_override": params.sample_rate_override,
                "force_to_mono": params.force_to_mono
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Audio compression configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring audio compression: {e}")
            return f"Error: {str(e)}"

    # UI System Tools (5 tools)
    @mcp.tool()
    async def canvas_configure(params: CanvasParams) -> str:
        """Configure Canvas component and settings"""
        try:
            command = {
                "action": "canvas_configure",
                "gameobject_path": params.gameobject_path,
                "render_mode": params.render_mode,
                "camera": params.camera,
                "plane_distance": params.plane_distance,
                "sorting_layer": params.sorting_layer,
                "order_in_layer": params.order_in_layer,
                "pixel_perfect": params.pixel_perfect,
                "override_sorting": params.override_sorting,
                "additional_shader_channels": params.additional_shader_channels
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Canvas configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring canvas: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def ui_element_create(params: UIElementParams) -> str:
        """Create and configure UI elements"""
        try:
            command = {
                "action": "ui_element_create",
                "parent_path": params.parent_path,
                "element_type": params.element_type,
                "element_name": params.element_name,
                "position": params.position,
                "size": params.size,
                "anchor": params.anchor,
                "pivot": params.pivot,
                "text_content": params.text_content,
                "sprite": params.sprite,
                "color": params.color,
                "font": params.font,
                "font_size": params.font_size,
                "interactable": params.interactable
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"UI element created: {result}"
        except Exception as e:
            logger.error(f"Error creating UI element: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def event_system_configure(params: EventSystemParams) -> str:
        """Configure EventSystem for UI input handling"""
        try:
            command = {
                "action": "event_system_configure",
                "gameobject_path": params.gameobject_path,
                "first_selected": params.first_selected,
                "send_navigation_events": params.send_navigation_events,
                "drag_threshold": params.drag_threshold,
                "input_module_type": params.input_module_type
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Event system configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring event system: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def layout_group_configure(params: LayoutGroupParams) -> str:
        """Configure layout groups for UI organization"""
        try:
            command = {
                "action": "layout_group_configure",
                "gameobject_path": params.gameobject_path,
                "layout_type": params.layout_type,
                "padding": params.padding,
                "spacing": params.spacing,
                "child_alignment": params.child_alignment,
                "child_control_size": params.child_control_size,
                "child_force_expand": params.child_force_expand,
                "cell_size": params.cell_size,
                "constraint": params.constraint,
                "constraint_count": params.constraint_count
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Layout group configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring layout group: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def ui_animation_create(params: UIAnimationParams) -> str:
        """Create UI animations and transitions"""
        try:
            command = {
                "action": "ui_animation_create",
                "gameobject_path": params.gameobject_path,
                "animation_type": params.animation_type,
                "duration": params.duration,
                "ease_type": params.ease_type,
                "start_value": params.start_value,
                "end_value": params.end_value,
                "loop_type": params.loop_type,
                "auto_play": params.auto_play,
                "trigger_event": params.trigger_event
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"UI animation created: {result}"
        except Exception as e:
            logger.error(f"Error creating UI animation: {e}")
            return f"Error: {str(e)}"

    # Build System Tools (3 tools)
    @mcp.tool()
    async def build_player(params: BuildPlayerParams) -> str:
        """Build Unity player for target platform"""
        try:
            command = {
                "action": "build_player",
                "target_platform": params.target_platform,
                "build_path": params.build_path,
                "development_build": params.development_build,
                "script_debugging": params.script_debugging,
                "compression": params.compression,
                "scenes": params.scenes,
                "player_settings": params.player_settings
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Player build completed: {result}"
        except Exception as e:
            logger.error(f"Error building player: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def build_settings_configure(params: BuildSettingsParams) -> str:
        """Configure build settings and player settings"""
        try:
            command = {
                "action": "build_settings_configure",
                "company_name": params.company_name,
                "product_name": params.product_name,
                "version": params.version,
                "bundle_identifier": params.bundle_identifier,
                "default_icon": params.default_icon,
                "splash_screen": params.splash_screen,
                "resolution_settings": params.resolution_settings,
                "quality_settings": params.quality_settings
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Build settings configured: {result}"
        except Exception as e:
            logger.error(f"Error configuring build settings: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def platform_switch(params: PlatformSwitchParams) -> str:
        """Switch Unity project to target platform"""
        try:
            command = {
                "action": "platform_switch",
                "target_platform": params.target_platform,
                "texture_compression": params.texture_compression,
                "scripting_backend": params.scripting_backend,
                "api_compatibility_level": params.api_compatibility_level,
                "target_device": params.target_device,
                "architecture": params.architecture
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Platform switched: {result}"
        except Exception as e:
            logger.error(f"Error switching platform: {e}")
            return f"Error: {str(e)}"

    # Scripting & Code Generation Tools (4 tools)
    @mcp.tool()
    async def script_template_create(params: ScriptTemplateParams) -> str:
        """Create script from template"""
        try:
            command = {
                "action": "script_template_create",
                "template_type": params.template_type,
                "script_name": params.script_name,
                "output_path": params.output_path,
                "namespace": params.namespace,
                "base_class": params.base_class,
                "interfaces": params.interfaces,
                "custom_template": params.custom_template
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Script created from template: {result}"
        except Exception as e:
            logger.error(f"Error creating script from template: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def code_analysis_run(params: CodeAnalysisParams) -> str:
        """Run code analysis on Unity project"""
        try:
            command = {
                "action": "code_analysis_run",
                "analysis_type": params.analysis_type,
                "target_files": params.target_files,
                "target_directories": params.target_directories,
                "include_patterns": params.include_patterns,
                "exclude_patterns": params.exclude_patterns,
                "output_format": params.output_format
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Code analysis completed: {result}"
        except Exception as e:
            logger.error(f"Error running code analysis: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def code_refactor(params: CodeRefactorParams) -> str:
        """Perform code refactoring operations"""
        try:
            command = {
                "action": "code_refactor",
                "refactor_type": params.refactor_type,
                "target_file": params.target_file,
                "old_name": params.old_name,
                "new_name": params.new_name,
                "start_line": params.start_line,
                "end_line": params.end_line,
                "target_namespace": params.target_namespace
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Code refactoring completed: {result}"
        except Exception as e:
            logger.error(f"Error performing code refactoring: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def documentation_generate(params: DocumentationParams) -> str:
        """Generate code documentation"""
        try:
            command = {
                "action": "documentation_generate",
                "doc_type": params.doc_type,
                "target_files": params.target_files,
                "output_path": params.output_path,
                "include_private": params.include_private,
                "include_internal": params.include_internal,
                "template_path": params.template_path,
                "generate_diagrams": params.generate_diagrams
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Documentation generated: {result}"
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            return f"Error: {str(e)}"

    # Performance & Profiling Tools (2 tools)
    @mcp.tool()
    async def profiler_data_collect(params: ProfilerDataParams) -> str:
        """Collect Unity profiler data"""
        try:
            command = {
                "action": "profiler_data_collect",
                "profiler_type": params.profiler_type,
                "duration": params.duration,
                "target_scene": params.target_scene,
                "sample_rate": params.sample_rate,
                "deep_profiling": params.deep_profiling,
                "output_format": params.output_format,
                "output_path": params.output_path
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Profiler data collected: {result}"
        except Exception as e:
            logger.error(f"Error collecting profiler data: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def performance_analysis_run(params: PerformanceAnalysisParams) -> str:
        """Run performance analysis on Unity project"""
        try:
            command = {
                "action": "performance_analysis_run",
                "analysis_type": params.analysis_type,
                "target_platform": params.target_platform,
                "quality_settings": params.quality_settings,
                "resolution": params.resolution,
                "vsync": params.vsync,
                "target_framerate": params.target_framerate,
                "benchmark_duration": params.benchmark_duration
            }
            result = await unity_manager.execute_unity_command(params.project_path, command)
            return f"Performance analysis completed: {result}"
        except Exception as e:
            logger.error(f"Error running performance analysis: {e}")
            return f"Error: {str(e)}"

    logger.info("Unity MCP tools registered successfully")