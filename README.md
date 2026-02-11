# Griptape Nodes: Sketchfab 3D Library

A [Griptape Nodes](https://www.griptapenodes.com/) custom library for searching, viewing, and downloading 3D models from [Sketchfab](https://sketchfab.com/) using the [Data API v3](https://sketchfab.com/developers/data-api/v3) and [Viewer API](https://sketchfab.com/developers/viewer).

## Features

- **Search Models** - Query Sketchfab's massive 3D model library with filters for category, sort order, downloadability, and animation
- **Get Model Info** - Retrieve detailed metadata for any model including geometry stats, thumbnails, license info, and author details
- **Generate Viewer HTML** - Create embeddable 3D viewer HTML using the Sketchfab Viewer API with customizable controls (autostart, autospin, screenshots, etc.)
- **Download Models** - Download 3D model files from Sketchfab (requires API token and downloadable models)

## Nodes

### Sketchfab Search

| Node | Type | Description |
|------|------|-------------|
| **Search Sketchfab Models** | ControlNode | Search for 3D models by keyword, category, and filters |
| **Get Model Info** | ControlNode | Get detailed information about a specific model by UID or URL |

### Sketchfab Viewer

| Node | Type | Description |
|------|------|-------------|
| **Generate Viewer HTML** | ControlNode | Generate embeddable HTML for 3D model viewing with Viewer API |

### Sketchfab Download

| Node | Type | Description |
|------|------|-------------|
| **Download Model** | ControlNode | Download a 3D model file from Sketchfab |

---

## Node Details

### Search Sketchfab Models

Search for 3D models on Sketchfab using the [Data API v3](https://docs.sketchfab.com/data-api/v3/index.html).

**Inputs:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | `"robot"` | Search query for 3D models |
| `category` | str | `""` | Category filter (e.g., `animals-pets`, `architecture`, `cars-vehicles`) |
| `sort_by` | str | `"-relevance"` | Sort order: `-relevance`, `-likeCount`, `-viewCount`, `-createdAt`, `-publishedAt` |
| `downloadable` | bool | `False` | Only show downloadable models |
| `animated` | bool | `False` | Only show animated models |
| `max_results` | int | `10` | Number of results (1-24) |
| `api_token` | str | `""` | Optional API token for authenticated requests |

**Outputs:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `results_json` | str | Full JSON array with parsed model data |
| `model_uids` | str | Comma-separated list of model UIDs |
| `first_model_uid` | str | UID of the first result (for easy chaining) |
| `result_count` | int | Number of results returned |

**Available Categories:**
`animals-pets`, `architecture`, `art-abstract`, `cars-vehicles`, `characters-creatures`, `cultural-heritage-history`, `electronics-gadgets`, `fashion-style`, `food-drink`, `furniture-home`, `music`, `nature-plants`, `news-politics`, `people`, `places-travel`, `science-technology`, `sports-fitness`, `weapons-military`

---

### Get Model Info

Retrieve detailed metadata for a specific Sketchfab model. Accepts either a model UID or a full Sketchfab URL.

**Inputs:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_uid` | str | `""` | Model UID or full Sketchfab URL |
| `api_token` | str | `""` | Optional API token |

**Outputs:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `model_name` | str | Name of the model |
| `description` | str | Model description |
| `thumbnail_url` | str | URL of the largest thumbnail image |
| `viewer_url` | str | Sketchfab page URL |
| `embed_url` | str | Embeddable iframe URL |
| `vertex_count` | int | Number of vertices |
| `face_count` | int | Number of faces |
| `is_downloadable` | bool | Whether the model can be downloaded |
| `license` | str | License information |
| `author` | str | Author display name |
| `model_json` | str | Full JSON response with all model details |

---

### Generate Viewer HTML

Generate embeddable HTML for the Sketchfab 3D viewer. Supports two modes:
1. **Simple iframe embed** (default) - lightweight, just an iframe
2. **Full Viewer API** - includes JavaScript controls for screenshots, camera reset, autospin toggle, and scene graph inspection

Reference: [Sketchfab Viewer API](https://sketchfab.com/developers/viewer)

**Inputs:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_uid` | str | `""` | Sketchfab model UID to embed |
| `width` | int | `800` | Viewer width in pixels |
| `height` | int | `600` | Viewer height in pixels |
| `autostart` | bool | `True` | Auto-start the viewer |
| `autospin` | float | `0.0` | Auto-spin speed (0 = off, try 0.2) |
| `ui_controls` | bool | `True` | Show Sketchfab UI controls |
| `annotations_visible` | bool | `True` | Show model annotations |
| `transparent_background` | bool | `False` | Transparent background |
| `use_viewer_api` | bool | `False` | Generate full Viewer API HTML with JS controls |

**Outputs:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `html_code` | str | Generated HTML code |
| `embed_url` | str | Direct embed URL |
| `model_uid_out` | str | Pass-through of the model UID |

**Viewer API Features (when `use_viewer_api` = True):**
- Take screenshots and download as PNG
- Toggle auto-spin
- Reset camera to default position
- Inspect scene graph (model structure)

---

### Download Model

Download a 3D model from Sketchfab. **Requires a valid API token** and only works with models marked as downloadable.

Reference: [Sketchfab Download API](https://sketchfab.com/developers/download-api)

**Inputs:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_uid` | str | `""` | Model UID or URL |
| `api_token` | str | `""` | Sketchfab API token (required) |
| `output_directory` | str | `"./downloads"` | Directory to save the model |

**Outputs:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `download_url` | str | Temporary download URL |
| `file_path` | str | Local path of the saved file |
| `file_size` | str | Human-readable file size |
| `status` | str | Download status message |

---

## Setup

### Prerequisites

- [Griptape Nodes](https://github.com/griptape-ai/griptape-nodes) installed and running
- Python 3.12+
- A Sketchfab account (free) for API token (optional for search, required for downloads)

### Get Your Sketchfab API Token

1. Go to [https://sketchfab.com/settings/password](https://sketchfab.com/settings/password)
2. Scroll down to **API Token**
3. Copy your token
4. Add it to your environment or Griptape Nodes secrets as `SKETCHFAB_API_TOKEN`

### Install the Library

1. Clone or download this repository into your Griptape Nodes workspace directory:

   ```bash
   cd `gtn config show workspace_directory`
   git clone https://github.com/your-username/griptape-nodes-library-sketchfab.git
   ```

2. Add the library in the Griptape Nodes Editor:

   - Open **Settings** > **Libraries**
   - Click **+ Add Library**
   - Enter the path to the library JSON file:
     ```
     <workspace_directory>/griptape-nodes-library-sketchfab/sketchfab_nodes/griptape_nodes_library.json
     ```
   - Close Settings and click **Refresh Libraries**

3. Verify your nodes appear under the **Sketchfab Search**, **Sketchfab Viewer**, and **Sketchfab Download** categories.

### Configure API Token (for Downloads)

Set the `SKETCHFAB_API_TOKEN` in Griptape Nodes:

- Open **Settings** > **API Keys & Secrets**
- Add `SKETCHFAB_API_TOKEN` with your token value

Or pass it directly to nodes via the `api_token` input parameter.

---

## Example Flows

### Search and View

Chain the **Search Sketchfab Models** node with **Generate Viewer HTML**:

1. **Search Sketchfab Models**: Set `query` to "dragon", `max_results` to 5
2. Connect `first_model_uid` output to **Generate Viewer HTML** `model_uid` input
3. The `html_code` output contains a ready-to-use HTML page with the 3D viewer

### Search, Info, and Download

1. **Search Sketchfab Models**: Set `query` to "helmet", `downloadable` to True
2. Connect `first_model_uid` to **Get Model Info** `model_uid`
3. Connect `first_model_uid` to **Download Model** `model_uid`
4. View model details in Get Model Info outputs and download the file

---

## API References

- [Sketchfab Data API v3](https://docs.sketchfab.com/data-api/v3/index.html) - REST API for model search and metadata
- [Sketchfab Viewer API](https://sketchfab.com/developers/viewer) - JavaScript API for 3D viewer control
- [Sketchfab Download API](https://sketchfab.com/developers/download-api) - API for downloading model files
- [Sketchfab Developer Guidelines](https://sketchfab.com/developers/guidelines) - Usage guidelines and best practices

## Dependencies

- `griptape-nodes` - Griptape Nodes framework
- `requests` >= 2.25.0 - HTTP library for API calls

## License

This library is provided under the Apache License 2.0.
