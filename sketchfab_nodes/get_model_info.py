"""Get detailed information about a specific Sketchfab 3D model."""

import json
import logging
import re
from typing import Any

import requests

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import ControlNode

logger = logging.getLogger(__name__)


class GetModelInfo(ControlNode):
    """Retrieve detailed information about a Sketchfab 3D model by UID or URL.

    Uses the Sketchfab Data API v3 to fetch model metadata including
    name, description, thumbnails, geometry stats, and more.
    """

    SKETCHFAB_MODELS_URL = "https://api.sketchfab.com/v3/models"

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "SketchfabSearch",
            "description": "Get detailed information about a Sketchfab model",
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
                tooltip="Sketchfab model UID or full URL (e.g., 'abc123' or 'https://sketchfab.com/3d-models/my-model-abc123')",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="api_token",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="Sketchfab API token (optional, for authenticated requests)",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )

        # --- Output Parameters ---
        self.add_parameter(
            Parameter(
                name="model_name",
                output_type="str",
                tooltip="Name of the 3D model",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="description",
                output_type="str",
                tooltip="Model description",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"multiline": True, "placeholder_text": "Model description"},
            )
        )
        self.add_parameter(
            Parameter(
                name="thumbnail_url",
                output_type="str",
                tooltip="URL of the model's thumbnail image",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="viewer_url",
                output_type="str",
                tooltip="URL to view the model on Sketchfab",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="embed_url",
                output_type="str",
                tooltip="Embeddable iframe URL for the model",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="vertex_count",
                output_type="int",
                tooltip="Number of vertices in the model",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="face_count",
                output_type="int",
                tooltip="Number of faces in the model",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="is_downloadable",
                output_type="bool",
                tooltip="Whether the model is downloadable",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="license",
                output_type="str",
                tooltip="License information for the model",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="author",
                output_type="str",
                tooltip="Display name of the model author",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="model_json",
                output_type="str",
                tooltip="Full JSON response with all model details",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"multiline": True, "placeholder_text": "Full model details JSON"},
            )
        )

    @staticmethod
    def _extract_uid(model_uid_or_url: str) -> str:
        """Extract a Sketchfab model UID from a UID string or full URL."""
        model_uid_or_url = model_uid_or_url.strip()

        # If it looks like a URL, try to extract the UID from it
        if "sketchfab.com" in model_uid_or_url:
            # Pattern: https://sketchfab.com/3d-models/model-name-uid
            match = re.search(r"[/-]([a-f0-9]{32})(?:[/?#]|$)", model_uid_or_url)
            if match:
                return match.group(1)
            # Pattern: short UID at the end of the URL
            match = re.search(r"/([a-zA-Z0-9]+)(?:[/?#]|$)", model_uid_or_url)
            if match:
                return match.group(1)

        return model_uid_or_url

    def process(self) -> None:
        raw_uid = self.parameter_values.get("model_uid", "")
        api_token = self.parameter_values.get("api_token", "")

        if not raw_uid:
            raise ValueError("model_uid is required. Provide a Sketchfab model UID or URL.")

        uid = self._extract_uid(raw_uid)
        logger.info(f"Fetching Sketchfab model info for UID: {uid}")

        # Build headers
        headers: dict[str, str] = {}
        if api_token:
            headers["Authorization"] = f"Token {api_token}"

        try:
            response = requests.get(
                f"{self.SKETCHFAB_MODELS_URL}/{uid}",
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            model = response.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise ValueError(f"Model not found: '{uid}'. Check the UID or URL.") from e
            raise RuntimeError(f"Sketchfab API error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Sketchfab API request failed: {e}") from e

        # Extract thumbnail
        thumbnail_url = ""
        thumbnails = model.get("thumbnails", {}).get("images", [])
        if thumbnails:
            sorted_thumbs = sorted(thumbnails, key=lambda t: t.get("width", 0), reverse=True)
            thumbnail_url = sorted_thumbs[0].get("url", "")

        # Extract license
        license_info = model.get("license", {})
        license_str = ""
        if license_info:
            license_str = license_info.get("fullName", license_info.get("label", ""))

        # Set outputs
        self.parameter_output_values["model_name"] = model.get("name", "")
        self.parameter_output_values["description"] = model.get("description", "")
        self.parameter_output_values["thumbnail_url"] = thumbnail_url
        self.parameter_output_values["viewer_url"] = f"https://sketchfab.com/3d-models/{uid}"
        self.parameter_output_values["embed_url"] = f"https://sketchfab.com/models/{uid}/embed"
        self.parameter_output_values["vertex_count"] = model.get("vertexCount", 0)
        self.parameter_output_values["face_count"] = model.get("faceCount", 0)
        self.parameter_output_values["is_downloadable"] = model.get("isDownloadable", False)
        self.parameter_output_values["license"] = license_str
        self.parameter_output_values["author"] = model.get("user", {}).get("displayName", "")
        self.parameter_output_values["model_json"] = json.dumps(model, indent=2, default=str)

        logger.info(f"Retrieved model info: {model.get('name', uid)}")
