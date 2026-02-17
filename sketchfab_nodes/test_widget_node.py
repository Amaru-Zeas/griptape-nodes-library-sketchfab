"""Minimal test node to verify widget rendering works."""

from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.traits.widget import Widget


class TestWidgetNode(DataNode):
    """Minimal test to verify widgets render. If you see a green box, widgets work."""

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "SketchfabViewer",
            "description": "Test if widgets render",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        self.add_parameter(
            Parameter(
                name="test",
                input_types=["dict"],
                type="dict",
                output_type="dict",
                default_value={"hello": "world"},
                tooltip="If you see a green box, widgets work!",
                allowed_modes={ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                traits={Widget(name="TestWidget", library="Sketchfab 3D Library")},
            )
        )

    def process(self) -> None:
        self.parameter_output_values["test"] = self.parameter_values.get("test", {})
