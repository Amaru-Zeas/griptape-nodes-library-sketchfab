"""Generate embeddable Sketchfab Viewer API HTML for a 3D model."""

import logging
from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import ControlNode

logger = logging.getLogger(__name__)


class GenerateViewerHTML(ControlNode):
    """Generate HTML code to embed a Sketchfab 3D model viewer.

    Uses the Sketchfab Viewer API to create customizable, embeddable
    viewer HTML with options for autostart, autospin, annotations, and more.
    Reference: https://sketchfab.com/developers/viewer
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "SketchfabViewer",
            "description": "Generate embeddable Sketchfab 3D viewer HTML",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        # --- Input Parameters ---
        self.add_parameter(
            Parameter(
                name="model_uid",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="Sketchfab model UID to embed",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="width",
                input_types=["int"],
                type="int",
                default_value=800,
                tooltip="Width of the viewer in pixels",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="height",
                input_types=["int"],
                type="int",
                default_value=600,
                tooltip="Height of the viewer in pixels",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="autostart",
                input_types=["bool"],
                type="bool",
                default_value=True,
                tooltip="Automatically start the viewer (no click-to-play)",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="autospin",
                input_types=["float"],
                type="float",
                default_value=0.0,
                tooltip="Auto-spin speed (0 = disabled, try 0.2 for gentle spin)",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="ui_controls",
                input_types=["bool"],
                type="bool",
                default_value=True,
                tooltip="Show Sketchfab UI controls (annotations, settings, etc.)",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="annotations_visible",
                input_types=["bool"],
                type="bool",
                default_value=True,
                tooltip="Show model annotations if available",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="transparent_background",
                input_types=["bool"],
                type="bool",
                default_value=False,
                tooltip="Use transparent background",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="use_viewer_api",
                input_types=["bool"],
                type="bool",
                default_value=False,
                tooltip="Generate full Viewer API HTML (with JavaScript controls) instead of a simple iframe embed",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )

        # --- Output Parameters ---
        self.add_parameter(
            Parameter(
                name="html_code",
                output_type="str",
                tooltip="Generated HTML code for embedding the viewer",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"multiline": True, "placeholder_text": "Generated HTML will appear here"},
            )
        )
        self.add_parameter(
            Parameter(
                name="embed_url",
                output_type="str",
                tooltip="Direct embed URL for the model viewer",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="model_uid_out",
                output_type="str",
                tooltip="Pass-through of the model UID",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def _build_embed_url(self, uid: str, autostart: bool, autospin: float,
                         ui_controls: bool, annotations_visible: bool,
                         transparent: bool) -> str:
        """Build the Sketchfab embed URL with query parameters."""
        base_url = f"https://sketchfab.com/models/{uid}/embed"
        params = []

        if autostart:
            params.append("autostart=1")
        if autospin > 0:
            params.append(f"autospin={autospin}")
        if not ui_controls:
            params.append("ui_controls=0")
            params.append("ui_infos=0")
            params.append("ui_stop=0")
            params.append("ui_inspector=0")
            params.append("ui_watermark_link=0")
            params.append("ui_watermark=0")
            params.append("ui_help=0")
            params.append("ui_settings=0")
            params.append("ui_vr=0")
            params.append("ui_fullscreen=0")
            params.append("ui_annotations=0")
        if not annotations_visible:
            params.append("ui_annotations=0")
        if transparent:
            params.append("transparent=1")

        if params:
            return f"{base_url}?{'&'.join(params)}"
        return base_url

    def _generate_simple_embed(self, embed_url: str, width: int, height: int) -> str:
        """Generate a simple iframe embed HTML."""
        return f"""<!DOCTYPE HTML>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sketchfab 3D Viewer</title>
    <style>
        body {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #1a1a2e; }}
        .viewer-container {{ border-radius: 12px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
    </style>
</head>
<body>
    <div class="viewer-container">
        <iframe
            title="Sketchfab 3D Viewer"
            width="{width}"
            height="{height}"
            src="{embed_url}"
            frameborder="0"
            allow="autoplay; fullscreen; xr-spatial-tracking"
            xr-spatial-tracking
            execution-while-out-of-viewport
            execution-while-not-rendered
            web-share
            allowfullscreen
            mozallowfullscreen="true"
            webkitallowfullscreen="true">
        </iframe>
    </div>
</body>
</html>"""

    def _generate_viewer_api_html(self, uid: str, width: int, height: int,
                                  autostart: bool, autospin: float) -> str:
        """Generate full Viewer API HTML with JavaScript controls."""
        autospin_js = f"\n                    api.setAutospin({autospin});" if autospin > 0 else ""
        start_js = "api.start();" if autostart else "// Call api.start() to begin"

        return f"""<!DOCTYPE HTML>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sketchfab Viewer API</title>
    <script type="text/javascript" src="https://static.sketchfab.com/api/sketchfab-viewer-1.12.1.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #e0e0e0; }}
        .viewer-wrapper {{ max-width: {width}px; margin: 0 auto; }}
        #api-frame {{ width: 100%; height: {height}px; border: none; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .controls {{ margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap; }}
        .controls button {{
            padding: 8px 16px; border: 1px solid #444; border-radius: 6px;
            background: #2a2a4a; color: #e0e0e0; cursor: pointer; font-size: 14px;
            transition: all 0.2s ease;
        }}
        .controls button:hover {{ background: #3a3a6a; border-color: #666; }}
        .info {{ margin-top: 12px; padding: 12px; background: #2a2a4a; border-radius: 8px; font-size: 13px; }}
        #model-info {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="viewer-wrapper">
        <iframe src="" id="api-frame"
            allow="autoplay; fullscreen; xr-spatial-tracking"
            xr-spatial-tracking execution-while-out-of-viewport
            execution-while-not-rendered web-share
            allowfullscreen mozallowfullscreen="true"
            webkitallowfullscreen="true">
        </iframe>

        <div class="controls">
            <button onclick="takeScreenshot()">Screenshot</button>
            <button onclick="toggleSpin()">Toggle Spin</button>
            <button onclick="resetCamera()">Reset Camera</button>
            <button onclick="getModelInfo()">Get Model Info</button>
        </div>
        <div class="info" id="model-info">Initializing viewer...</div>
    </div>

    <script type="text/javascript">
        var iframe = document.getElementById('api-frame');
        var uid = '{uid}';
        var viewerApi = null;
        var isSpinning = false;

        var client = new Sketchfab(iframe);
        client.init(uid, {{
            success: function onSuccess(api) {{
                {start_js}
                api.addEventListener('viewerready', function() {{
                    viewerApi = api;{autospin_js}
                    document.getElementById('model-info').textContent = 'Viewer ready! Use the controls below.';
                    console.log('Sketchfab Viewer is ready');
                }});
            }},
            error: function onError() {{
                document.getElementById('model-info').textContent = 'Error loading viewer.';
                console.log('Viewer error');
            }}
        }});

        function takeScreenshot() {{
            if (!viewerApi) return;
            viewerApi.getScreenShot(function(data) {{
                var link = document.createElement('a');
                link.href = data;
                link.download = 'sketchfab_screenshot.png';
                link.click();
            }});
        }}

        function toggleSpin() {{
            if (!viewerApi) return;
            isSpinning = !isSpinning;
            viewerApi.setAutospin(isSpinning ? 0.3 : 0);
        }}

        function resetCamera() {{
            if (!viewerApi) return;
            viewerApi.recenterCamera();
        }}

        function getModelInfo() {{
            if (!viewerApi) return;
            viewerApi.getSceneGraph(function(err, result) {{
                if (!err) {{
                    document.getElementById('model-info').textContent = JSON.stringify(result, null, 2).substring(0, 2000);
                }}
            }});
        }}
    </script>
</body>
</html>"""

    def process(self) -> None:
        uid = self.parameter_values.get("model_uid", "").strip()
        width = self.parameter_values.get("width", 800)
        height = self.parameter_values.get("height", 600)
        autostart = self.parameter_values.get("autostart", True)
        autospin = self.parameter_values.get("autospin", 0.0)
        ui_controls = self.parameter_values.get("ui_controls", True)
        annotations_visible = self.parameter_values.get("annotations_visible", True)
        transparent = self.parameter_values.get("transparent_background", False)
        use_viewer_api = self.parameter_values.get("use_viewer_api", False)

        if not uid:
            raise ValueError("model_uid is required. Provide a Sketchfab model UID.")

        # Build embed URL
        embed_url = self._build_embed_url(
            uid, autostart, autospin, ui_controls, annotations_visible, transparent
        )

        # Generate HTML
        if use_viewer_api:
            html_code = self._generate_viewer_api_html(uid, width, height, autostart, autospin)
        else:
            html_code = self._generate_simple_embed(embed_url, width, height)

        # Set outputs
        self.parameter_output_values["html_code"] = html_code
        self.parameter_output_values["embed_url"] = embed_url
        self.parameter_output_values["model_uid_out"] = uid

        logger.info(f"Generated viewer HTML for model: {uid}")
