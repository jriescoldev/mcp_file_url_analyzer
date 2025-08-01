
# mcp-file-url-analyzer MCP server

MCP server for analyzing local files, directories, and URLs (text or binary) using the latest MCP Python SDK (FastMCP).

---

## Features
- Analyze local files, directories, and URLs (text or binary)
- SSRF protection and file/URL size limits
- Docker support for easy deployment
- Comprehensive async unit tests
- Compatible with Python >=3.13

## Requirements
- Python 3.13 or newer
- See `requirements.txt` for dependencies

## Quick Start

### 1. Installation (Virtualenv)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
- Copy `.env.example` to `.env` and edit as needed (not committed to repo)
- Environment variables:
  - `MAX_FILE_SIZE` (optional, bytes): File/URL size limit (default 5MB)
  - `PYTHONUNBUFFERED=1`: For immediate logs in Docker

### 3. Run the Server
```bash
python -m src.mcp_file_url_analyzer.server
```

---

## Usage

### Command-Line Analysis

- Analyze a local file or directory:
  ```bash
  python3 analyze_path.py /path/to/file_or_directory
  ```
- Analyze a URL:
  ```bash
  python3 analyze_url.py https://www.example.com
  ```

### Python API Example

- Analyze a local file:
  ```python
  from mcp.client import MCPClient
  client = MCPClient()
  result = await client.tool('analyze-path', path='/path/to/file.txt')
  print(result)
  # Output: {'type': 'text', 'mime': 'text/plain', ...}
  ```
- Analyze a directory:
  ```python
  result = await client.tool('analyze-path', path='/path/to/dir')
  print(result)
  # Output: {'/path/to/dir/file1.txt': {...}, ...}
  ```
- Analyze a URL:
  ```python
  result = await client.tool('analyze-url', url='https://example.com/file.txt')
  print(result)
  # Output: {'type': 'text', 'content_type': 'text/plain', ...}
  ```

---

## Tools
| Tool         | Description                                 | Arguments |
|--------------|---------------------------------------------|-----------|
| analyze-path | Analyze a local file or directory           | path: str |
| analyze-url  | Download and analyze a URL (text or binary) | url: str  |

---

## Docker Usage

### Build Image
```bash
docker build -t mcp-file-url-analyzer:latest .
```
### Rebuild (no cache)
```bash
docker build --no-cache -t mcp-file-url-analyzer:latest .
```
### Run Image
```bash
docker run --rm -i --env-file .env mcp-file-url-analyzer
```

---

## VSCode & WSL Integration

### VSCode Example (`.vscode/mcp.json`)
```json
{
  "servers": {
    "mcp-file-url-analyzer": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--env-file", "${workspaceFolder}/.env",
        "mcp-file-url-analyzer"
      ]
    }
  }
}
```
### WSL Example
```json
"mcp-file-url-analyzer": {
  "type": "stdio",
  "command": "wsl",
  "args": [
    "docker", "run", "--rm", "-i",
    "mcp-file-url-analyzer"
  ]
}
```

---

## Testing
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

---

## Troubleshooting
- If you see `ModuleNotFoundError: No module named 'mcp'`, install dependencies with `pip install -r requirements.txt` in a virtual environment.
- For Docker logs, check for `[mcp-file-url-analyzer]` messages.

---

## References & Resources
- [MCP Python SDK & Examples](https://github.com/modelcontextprotocol/create-python-server)

---

## Upload to Container Registry

### Authenticate Docker with GitHub
```bash
echo <YOUR_GITHUB_PAT> | docker login ghcr.io -u <your-github-username> --password-stdin
```
### Build and Tag
```bash
docker build -t ghcr.io/<your-github-username>/<image-name>:<tag> .
docker build -t ghcr.io/jriescoldev/mcp-file-url-analyzer:latest .
```
### Push
```bash
docker push ghcr.io/<your-github-username>/<image-name>:<tag>
```