"""Open a Sketchfab 3D model viewer in the user's default web browser."""

import logging
import os
import tempfile
import webbrowser
from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import ControlNode

logger = logging.getLogger(__name__)


class ViewInBrowser(ControlNode):
    """Open a Sketchfab 3D model in the default web browser.

    Can work in two modes:
    - Direct URL mode: Opens the Sketchfab embed URL directly (simple, fast)
    - HTML mode: Saves generated HTML to a local file and opens it (supports Viewer API controls)

    Connect this after a GenerateViewerHTML or SearchModels node to view 3D models instantly.
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "SketchfabViewer",
            "description": "Open a 3D model viewer in your web browser",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        # --- Input Parameters ---
        self.add_parameter(
            Parameter(
                name="html_code",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="HTML code from the Generate Viewer HTML node. If provided, saves to a file and opens it.",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                ui_options={"multiline": True, "placeholder_text": "Connect html_code from Generate Viewer HTML node"},
            )
        )
        self.add_parameter(
            Parameter(
                name="embed_url",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="Sketchfab embed URL. Used as fallback if no HTML code is provided.",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="model_uid",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="Sketchfab model UID. Used as last fallback to build a viewer URL.",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="save_directory",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="Directory to save HTML file (leave empty for system temp directory)",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )

        # --- Output Parameters ---
        self.add_parameter(
            Parameter(
                name="opened_url",
                output_type="str",
                tooltip="The URL or file path that was opened in the browser",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="status",
                output_type="str",
                tooltip="Status message",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"multiline": True, "placeholder_text": "Status will appear here"},
            )
        )

    def process(self) -> None:
        html_code = self.parameter_values.get("html_code", "").strip()
        embed_url = self.parameter_values.get("embed_url", "").strip()
        model_uid = self.parameter_values.get("model_uid", "").strip()
        save_directory = self.parameter_values.get("save_directory", "").strip()

        # Priority 1: Use HTML code (save to file, open in browser)
        if html_code:
            file_path = self._save_and_open_html(html_code, model_uid, save_directory)
            self.parameter_output_values["opened_url"] = file_path
            self.parameter_output_values["status"] = (
                f"Opened Viewer API HTML in browser.\nFile saved to: {file_path}"
            )
            logger.info(f"Opened HTML viewer file: {file_path}")
            return

        # Priority 2: Use embed URL directly
        if embed_url:
            webbrowser.open(embed_url)
            self.parameter_output_values["opened_url"] = embed_url
            self.parameter_output_values["status"] = f"Opened embed URL in browser:\n{embed_url}"
            logger.info(f"Opened embed URL: {embed_url}")
            return

        # Priority 3: Build URL from model UID
        if model_uid:
            url = f"https://sketchfab.com/models/{model_uid}/embed?autostart=1"
            webbrowser.open(url)
            self.parameter_output_values["opened_url"] = url
            self.parameter_output_values["status"] = f"Opened model in browser:\n{url}"
            logger.info(f"Opened model URL: {url}")
            return

        raise ValueError(
            "No input provided. Connect html_code, embed_url, or model_uid from another Sketchfab node."
        )

    def _save_and_open_html(self, html_code: str, model_uid: str, save_directory: str) -> str:
        """Save HTML to a file and open it in the default browser."""
        # Determine filename
        filename = f"sketchfab_viewer_{model_uid}.html" if model_uid else "sketchfab_viewer.html"

        if save_directory:
            os.makedirs(save_directory, exist_ok=True)
            file_path = os.path.join(save_directory, filename)
        else:
            # Use temp directory but with a recognizable name
            temp_dir = os.path.join(tempfile.gettempdir(), "sketchfab_viewers")
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, filename)

        # Write the HTML file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_code)

        # Open in default browser
        file_url = f"file:///{os.path.abspath(file_path).replace(os.sep, '/')}"
        webbrowser.open(file_url)

        return os.path.abspath(file_path)
