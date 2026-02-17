"""OpenPose 3D Editor Widget node - pose a human skeleton directly inside the node."""

import json
import logging
from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.traits.widget import Widget

logger = logging.getLogger(__name__)

# Default T-pose joint positions
DEFAULT_JOINTS = {
    "nose":            {"x": 0,     "y": 1.7,  "z": 0},
    "neck":            {"x": 0,     "y": 1.5,  "z": 0},
    "right_shoulder":  {"x": -0.3,  "y": 1.5,  "z": 0},
    "right_elbow":     {"x": -0.55, "y": 1.5,  "z": 0},
    "right_wrist":     {"x": -0.8,  "y": 1.5,  "z": 0},
    "left_shoulder":   {"x": 0.3,   "y": 1.5,  "z": 0},
    "left_elbow":      {"x": 0.55,  "y": 1.5,  "z": 0},
    "left_wrist":      {"x": 0.8,   "y": 1.5,  "z": 0},
    "right_hip":       {"x": -0.15, "y": 1.0,  "z": 0},
    "right_knee":      {"x": -0.15, "y": 0.55, "z": 0},
    "right_ankle":     {"x": -0.15, "y": 0.1,  "z": 0},
    "left_hip":        {"x": 0.15,  "y": 1.0,  "z": 0},
    "left_knee":       {"x": 0.15,  "y": 0.55, "z": 0},
    "left_ankle":      {"x": 0.15,  "y": 0.1,  "z": 0},
    "right_eye":       {"x": -0.06, "y": 1.75, "z": 0.05},
    "left_eye":        {"x": 0.06,  "y": 1.75, "z": 0.05},
    "right_ear":       {"x": -0.12, "y": 1.73, "z": -0.02},
    "left_ear":        {"x": 0.12,  "y": 1.73, "z": -0.02},
}


class OpenPoseEditor(DataNode):
    """Interactive 3D OpenPose skeleton editor.

    Pose a human figure by dragging joints in 3D space.
    Outputs joint positions as a dict compatible with OpenPose / ControlNet workflows.

    Features:
    - 18 draggable joints (head, shoulders, elbows, wrists, hips, knees, ankles, eyes, ears)
    - Color-coded joints matching OpenPose conventions
    - Front, Side, and Top view presets
    - Reset to T-pose
    - Outputs joint positions as JSON for downstream processing

    Reference: https://openposeai.com/
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "OpenPose",
            "description": "3D OpenPose skeleton editor for posing",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        # Widget: the pose editor
        self.add_parameter(
            Parameter(
                name="pose_editor",
                input_types=["dict"],
                type="dict",
                output_type="dict",
                default_value={"joints": DEFAULT_JOINTS},
                tooltip="Interactive 3D OpenPose editor. Drag joints to pose the skeleton.",
                allowed_modes={ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                traits={Widget(name="OpenPoseEditor", library="Sketchfab 3D Library")},
            )
        )

        # Output: joint positions as JSON string
        self.add_parameter(
            Parameter(
                name="joints_json",
                output_type="str",
                tooltip="Joint positions as a JSON string (for passing to text-based nodes)",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"multiline": True, "placeholder_text": "Joint positions JSON"},
            )
        )

        # Output: number of joints
        self.add_parameter(
            Parameter(
                name="joint_count",
                output_type="int",
                tooltip="Number of joints in the pose",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def process(self) -> None:
        pose_data = self.parameter_values.get("pose_editor", {})

        joints = {}
        if isinstance(pose_data, dict):
            joints = pose_data.get("joints", DEFAULT_JOINTS)

        # Output the pose data
        self.parameter_output_values["pose_editor"] = {"joints": joints}
        self.parameter_output_values["joints_json"] = json.dumps(joints, indent=2)
        self.parameter_output_values["joint_count"] = len(joints)

        logger.info(f"OpenPose editor output: {len(joints)} joints")
