"""Search for 3D models on Sketchfab using the Data API v3."""

import json
import logging
from typing import Any

import requests

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import ControlNode

logger = logging.getLogger(__name__)

# Sketchfab model categories
SKETCHFAB_CATEGORIES = [
    "animals-pets",
    "architecture",
    "art-abstract",
    "cars-vehicles",
    "characters-creatures",
    "cultural-heritage-history",
    "electronics-gadgets",
    "fashion-style",
    "food-drink",
    "furniture-home",
    "music",
    "nature-plants",
    "news-politics",
    "people",
    "places-travel",
    "science-technology",
    "sports-fitness",
    "weapons-military",
]

SORT_OPTIONS = [
    "-relevance",
    "-likeCount",
    "-viewCount",
    "-createdAt",
    "-publishedAt",
]


class SearchModels(ControlNode):
    """Search for 3D models on Sketchfab using the Data API v3.

    This node queries the Sketchfab search API and returns model results
    including names, UIDs, thumbnail URLs, and viewer URLs.
    """

    SKETCHFAB_SEARCH_URL = "https://api.sketchfab.com/v3/search"

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "SketchfabSearch",
            "description": "Search for 3D models on Sketchfab",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        # --- Input Parameters ---
        self.add_parameter(
            Parameter(
                name="query",
                input_types=["str"],
                type="str",
                default_value="robot",
                tooltip="Search query for 3D models on Sketchfab",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="category",
                input_types=["str"],
                type="str",
                default_value="",
                tooltip="Filter by category (leave empty for all categories)",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="sort_by",
                input_types=["str"],
                type="str",
                default_value="-relevance",
                tooltip="Sort results by: -relevance, -likeCount, -viewCount, -createdAt, -publishedAt",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="downloadable",
                input_types=["bool"],
                type="bool",
                default_value=False,
                tooltip="Only show downloadable models",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="animated",
                input_types=["bool"],
                type="bool",
                default_value=False,
                tooltip="Only show animated models",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="max_results",
                input_types=["int"],
                type="int",
                default_value=10,
                tooltip="Maximum number of results to return (1-24)",
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
                name="results_json",
                output_type="str",
                tooltip="Full JSON response with model search results",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"multiline": True, "placeholder_text": "Search results will appear here"},
            )
        )
        self.add_parameter(
            Parameter(
                name="model_uids",
                output_type="str",
                tooltip="Comma-separated list of model UIDs from search results",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="first_model_uid",
                output_type="str",
                tooltip="The UID of the first model in search results",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="result_count",
                output_type="int",
                tooltip="Number of results returned",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def process(self) -> None:
        query = self.parameter_values.get("query", "")
        category = self.parameter_values.get("category", "")
        sort_by = self.parameter_values.get("sort_by", "-relevance")
        downloadable = self.parameter_values.get("downloadable", False)
        animated = self.parameter_values.get("animated", False)
        max_results = self.parameter_values.get("max_results", 10)
        api_token = self.parameter_values.get("api_token", "")

        # Clamp max_results
        max_results = max(1, min(24, max_results))

        # Build request parameters
        params: dict[str, Any] = {
            "type": "models",
            "q": query,
            "count": max_results,
            "sort_by": sort_by,
        }

        if category:
            params["categories"] = category
        if downloadable:
            params["downloadable"] = "true"
        if animated:
            params["animated"] = "true"

        # Build headers
        headers: dict[str, str] = {}
        if api_token:
            headers["Authorization"] = f"Token {api_token}"

        logger.info(f"Searching Sketchfab for: '{query}'")

        try:
            response = requests.get(
                self.SKETCHFAB_SEARCH_URL,
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Sketchfab search failed: {e}")
            raise RuntimeError(f"Sketchfab API request failed: {e}") from e

        # Parse results
        results = data.get("results", [])
        parsed_results = []

        for model in results:
            thumbnail_url = ""
            thumbnails = model.get("thumbnails", {}).get("images", [])
            if thumbnails:
                # Get the largest thumbnail
                sorted_thumbs = sorted(thumbnails, key=lambda t: t.get("width", 0), reverse=True)
                thumbnail_url = sorted_thumbs[0].get("url", "")

            parsed_results.append({
                "uid": model.get("uid", ""),
                "name": model.get("name", ""),
                "description": model.get("description", "")[:200],
                "thumbnail_url": thumbnail_url,
                "viewer_url": f"https://sketchfab.com/3d-models/{model.get('uid', '')}",
                "embed_url": f"https://sketchfab.com/models/{model.get('uid', '')}/embed",
                "like_count": model.get("likeCount", 0),
                "view_count": model.get("viewCount", 0),
                "vertex_count": model.get("vertexCount", 0),
                "face_count": model.get("faceCount", 0),
                "is_downloadable": model.get("isDownloadable", False),
                "animated": model.get("animationCount", 0) > 0,
                "user": model.get("user", {}).get("displayName", ""),
                "created_at": model.get("createdAt", ""),
            })

        uids = [r["uid"] for r in parsed_results]

        # Set outputs
        self.parameter_output_values["results_json"] = json.dumps(parsed_results, indent=2)
        self.parameter_output_values["model_uids"] = ",".join(uids)
        self.parameter_output_values["first_model_uid"] = uids[0] if uids else ""
        self.parameter_output_values["result_count"] = len(parsed_results)

        logger.info(f"Sketchfab search returned {len(parsed_results)} results")
