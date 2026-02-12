"""Download a 3D model from Sketchfab using the Download API."""

import json
import logging
import os
import re
import time
from typing import Any

import requests

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import ControlNode

logger = logging.getLogger(__name__)


class DownloadModel(ControlNode):
    """Download a 3D model from Sketchfab using the Download API.

    Requires a Sketchfab API token with download permissions. Only works
    for models that are marked as downloadable on Sketchfab.
    Reference: https://sketchfab.com/developers/download-api
    """

    SKETCHFAB_MODELS_URL = "https://api.sketchfab.com/v3/models"

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "SketchfabDownload",
            "description": "Download a 3D model from Sketchfab",
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
                tooltip="Sketchfab model UID or URL to download",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="api_token",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="Sketchfab API token (required for downloads). Get yours at https://sketchfab.com/settings/password",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="output_directory",
                input_types=["str"],
                type="str",
                default_value="./downloads",
                tooltip="Directory to save the downloaded model file",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )

        # --- Output Parameters ---
        self.add_parameter(
            Parameter(
                name="download_url",
                output_type="str",
                tooltip="The temporary download URL for the model",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="file_path",
                output_type="str",
                tooltip="Local file path where the model was saved",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="file_size",
                output_type="str",
                tooltip="Size of the downloaded file",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="status",
                output_type="str",
                tooltip="Download status message",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"multiline": True, "placeholder_text": "Download status"},
            )
        )

    @staticmethod
    def _extract_uid(model_uid_or_url: str) -> str:
        """Extract a Sketchfab model UID from a UID string or full URL."""
        model_uid_or_url = model_uid_or_url.strip()

        if "sketchfab.com" in model_uid_or_url:
            match = re.search(r"[/-]([a-f0-9]{32})(?:[/?#]|$)", model_uid_or_url)
            if match:
                return match.group(1)
            match = re.search(r"/([a-zA-Z0-9]+)(?:[/?#]|$)", model_uid_or_url)
            if match:
                return match.group(1)

        return model_uid_or_url

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def validate_before_node_run(self) -> list[Exception] | None:
        """Validate that the API token is provided."""
        exceptions = []
        api_token = self.parameter_values.get("api_token", "")

        if not api_token:
            # Try to get from secrets manager
            try:
                api_token = self.get_config_value(service="Sketchfab", value="SKETCHFAB_API_TOKEN")
            except Exception:
                pass

        if not api_token:
            exceptions.append(
                ValueError(
                    "Sketchfab API token is required for downloading models. "
                    "Get yours at https://sketchfab.com/settings/password"
                )
            )

        model_uid = self.parameter_values.get("model_uid", "")
        if not model_uid:
            exceptions.append(ValueError("model_uid is required."))

        return exceptions if exceptions else None

    def process(self) -> None:
        raw_uid = self.parameter_values.get("model_uid", "")
        api_token = self.parameter_values.get("api_token", "")
        output_dir = self.parameter_values.get("output_directory", "./downloads")

        # Try secrets manager if no token provided directly
        if not api_token:
            try:
                api_token = self.get_config_value(service="Sketchfab", value="SKETCHFAB_API_TOKEN")
            except Exception:
                pass

        if not api_token:
            raise ValueError("Sketchfab API token is required for downloading models.")

        uid = self._extract_uid(raw_uid)
        logger.info(f"Requesting download for Sketchfab model: {uid}")

        headers = {"Authorization": f"Token {api_token}"}

        # Step 1: Request the download URL
        try:
            download_endpoint = f"{self.SKETCHFAB_MODELS_URL}/{uid}/download"
            response = requests.get(download_endpoint, headers=headers, timeout=30)
            response.raise_for_status()
            download_data = response.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                status = e.response.status_code
                if status == 401:
                    raise ValueError("Invalid API token. Check your Sketchfab API token.") from e
                elif status == 403:
                    raise ValueError("Access denied. This model may not be downloadable.") from e
                elif status == 404:
                    raise ValueError(f"Model not found: '{uid}'.") from e
            raise RuntimeError(f"Sketchfab Download API error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Sketchfab API request failed: {e}") from e

        # Step 2: Get the actual download URL (usually in glTF format)
        download_info = None
        for fmt_key in ["gltf", "glb", "usdz", "source"]:
            if fmt_key in download_data:
                download_info = download_data[fmt_key]
                break

        if not download_info:
            # Try the first available format
            for key, value in download_data.items():
                if isinstance(value, dict) and "url" in value:
                    download_info = value
                    break

        if not download_info or "url" not in download_info:
            raise RuntimeError(
                f"No download URL found in response. Available formats: {list(download_data.keys())}"
            )

        download_url = download_info["url"]
        file_size_remote = download_info.get("size", 0)

        self.parameter_output_values["download_url"] = download_url

        # Step 3: Download the file
        os.makedirs(output_dir, exist_ok=True)

        # Determine filename
        content_type = download_info.get("contentType", "")
        ext = ".zip"
        if "gltf" in content_type or "gltf" in str(download_info.get("format", "")):
            ext = ".zip"  # glTF usually comes as a zip
        elif "glb" in content_type:
            ext = ".glb"

        filename = f"{uid}{ext}"
        file_path = os.path.join(output_dir, filename)

        logger.info(f"Downloading model to: {file_path}")

        try:
            with requests.get(download_url, stream=True, timeout=120) as dl_response:
                dl_response.raise_for_status()
                total_downloaded = 0

                with open(file_path, "wb") as f:
                    for chunk in dl_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        total_downloaded += len(chunk)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Download failed: {e}") from e

        file_size_str = self._format_file_size(total_downloaded)

        # Set outputs
        self.parameter_output_values["file_path"] = os.path.abspath(file_path)
        self.parameter_output_values["file_size"] = file_size_str
        self.parameter_output_values["status"] = (
            f"Successfully downloaded model {uid}\n"
            f"File: {os.path.abspath(file_path)}\n"
            f"Size: {file_size_str}"
        )

        logger.info(f"Successfully downloaded model {uid} ({file_size_str})")
