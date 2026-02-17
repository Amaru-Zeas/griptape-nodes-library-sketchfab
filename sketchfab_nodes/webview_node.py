"""WebView Widget node - render any live website directly inside a node."""

import logging
from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.traits.widget import Widget

logger = logging.getLogger(__name__)


class WebViewNode(DataNode):
    """Embed any live website inside a node.

    Renders a URL in an iframe widget. Use it for:
    - Sketchfab 3D model viewer
    - OpenPose 3D editor (openposeai.com)
    - Any web app or page

    Connect a URL from another node or type one directly in the widget.
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "SketchfabViewer",
            "description": "Embed a live website inside the node",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        # Input: URL from another node
        self.add_parameter(
            Parameter(
                name="url",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="URL to load in the web viewer. Connect from another node or set manually.",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )

        # Widget: the web viewer
        self.add_parameter(
            Parameter(
                name="web_viewer",
                input_types=["dict"],
                type="dict",
                output_type="dict",
                default_value={"url": ""},
                tooltip="Live website viewer. Enter a URL and click Go.",
                allowed_modes={ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                traits={Widget(name="WebView", library="Sketchfab 3D Library")},
            )
        )

        # Output: the current URL
        self.add_parameter(
            Parameter(
                name="current_url",
                output_type="str",
                tooltip="The URL currently loaded in the viewer",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def after_value_set(self, parameter: Parameter, value: Any) -> None:
        """When url input changes, update the web viewer widget."""
        if parameter.name == "url" and value:
            url = str(value).strip()
            if url:
                self.parameter_values["web_viewer"] = {"url": url}
                self.parameter_output_values["web_viewer"] = {"url": url}
                self.parameter_output_values["current_url"] = url
        return super().after_value_set(parameter, value)

    def process(self) -> None:
        url_input = self.parameter_values.get("url", "")
        viewer_data = self.parameter_values.get("web_viewer", {})

        # Input URL takes priority
        url = ""
        if url_input:
            url = str(url_input).strip()
        elif isinstance(viewer_data, dict) and viewer_data.get("url"):
            url = str(viewer_data["url"]).strip()

        if url:
            self.parameter_output_values["web_viewer"] = {"url": url}
            self.parameter_output_values["current_url"] = url
        else:
            self.parameter_output_values["web_viewer"] = {"url": ""}
            self.parameter_output_values["current_url"] = ""
