"""Sketchfab 3D Viewer Widget node - view 3D models directly inside the node."""

import logging
import re
from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.traits.widget import Widget

logger = logging.getLogger(__name__)


class SketchfabViewerWidget(DataNode):
    """View a Sketchfab 3D model directly inside the node using an interactive widget.

    Connect a model_uid from a Search or GetModelInfo node, or paste a
    Sketchfab URL directly into the widget input field.

    The widget uses the Sketchfab Viewer API for full 3D interaction
    with controls for screenshots, auto-spin, and camera reset.
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "SketchfabViewer",
            "description": "View a 3D model directly in the node",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        # Input: model UID from other nodes
        self.add_parameter(
            Parameter(
                name="model_uid",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="Sketchfab model UID or URL. Connect from Search or Get Model Info nodes.",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )

        # Widget: the 3D viewer
        self.add_parameter(
            Parameter(
                name="viewer",
                input_types=["dict"],
                type="dict",
                output_type="dict",
                default_value={"model_uid": ""},
                tooltip="Interactive 3D model viewer. Paste a UID/URL or connect model_uid input.",
                allowed_modes={ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                traits={Widget(name="SketchfabViewer", library="sketchfab_nodes")},
            )
        )

        # Output: pass-through the model UID
        self.add_parameter(
            Parameter(
                name="model_uid_out",
                output_type="str",
                tooltip="The model UID currently being viewed",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    @staticmethod
    def _extract_uid(raw: str) -> str:
        """Extract a Sketchfab model UID from a string or URL."""
        raw = raw.strip()
        if not raw:
            return ""

        if "sketchfab.com" in raw:
            match = re.search(r"[/-]([a-f0-9]{32})(?:[/?#]|$)", raw)
            if match:
                return match.group(1)
            match = re.search(r"/([a-zA-Z0-9]+)(?:[/?#]|$)", raw)
            if match:
                return match.group(1)

        return raw

    def after_value_set(self, parameter: Parameter, value: Any) -> None:
        """When model_uid input changes, update the viewer widget."""
        if parameter.name == "model_uid" and value:
            uid = self._extract_uid(str(value))
            if uid:
                self.parameter_values["viewer"] = {"model_uid": uid}
                self.parameter_output_values["viewer"] = {"model_uid": uid}
                self.parameter_output_values["model_uid_out"] = uid
        return super().after_value_set(parameter, value)

    def process(self) -> None:
        # Get model_uid from input or from the viewer widget itself
        model_uid = self.parameter_values.get("model_uid", "")
        viewer_data = self.parameter_values.get("viewer", {})

        # Input takes priority, then widget value
        uid = ""
        if model_uid:
            uid = self._extract_uid(str(model_uid))
        elif isinstance(viewer_data, dict) and viewer_data.get("model_uid"):
            uid = self._extract_uid(str(viewer_data["model_uid"]))

        if uid:
            self.parameter_output_values["viewer"] = {"model_uid": uid}
            self.parameter_output_values["model_uid_out"] = uid
        else:
            self.parameter_output_values["viewer"] = {"model_uid": ""}
            self.parameter_output_values["model_uid_out"] = ""
