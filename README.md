# mcp-file-url-analyzer MCP server

A modern, secure MCP server for analyzing local files and URLs (text and binary) using the latest MCP Python SDK (FastMCP).

## Features

- Analyze local files, directories, and URLs (text or binary)
- SSRF protection and file/URL size limits
- Docker support for easy deployment
- Comprehensive async unit tests
- Compatible with Python >=3.13

## Tools summary
| Tool           | Description                                 | Arguments                |
|----------------|---------------------------------------------|--------------------------|
| analyze-path   | Analyze a local file or directory           | path: str                |
| analyze-url    | Download and analyze a URL (text or binary) | url: str                 |

## Resources summary
| Resource URI      | Description                |
|-------------------|---------------------------|
| *(none)*          |                           |

## Variables de entorno soportadas
- `.env` (no se sube al repo):
  - Variables secretas o de configuración opcional.
- `MAX_FILE_SIZE` (opcional, bytes): Límite de tamaño de archivo/URL (por defecto 5MB).
- `PYTHONUNBUFFERED=1`: Para logs inmediatos en Docker.

## Initialize MCP Enviroment tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.mcp_file_url_analyzer.server
```
## Troubleshooting
- Si ves `ModuleNotFoundError: No module named 'mcp'`, instala dependencias con `pip install -r requirements.txt` en un entorno virtual.
- Para debuggear logs en Docker, revisa los mensajes `[mcp-file-url-analyzer]` y usa el script Python para flujo correcto.

## Ejemplo de uso del script Python

```bash
python3 analyze_host.py https://www.rstic.es/
```
Esto analizará la URL indicada y mostrará la respuesta formateada.

## Practical Examples

### Analyze a local file (Python)
```python
from mcp.client import MCPClient
client = MCPClient()
result = await client.tool('analyze-path', path='/path/to/file.txt')
print(result)
# Output example:
# {'type': 'text', 'mime': 'text/plain', 'lines': 42, 'words': 300, 'size': 1234, 'preview': 'First 500 chars...'}
```

### Analyze a directory (Python)
```python
result = await client.tool('analyze-path', path='/path/to/dir')
print(result)
# Output example:
# {'/path/to/dir/file1.txt': {...}, '/path/to/dir/file2.bin': {...}}
```

### Analyze a URL (Python)
```python
result = await client.tool('analyze-url', url='https://example.com/file.txt')
print(result)
# Output example:
# {'type': 'text', 'content_type': 'text/plain', 'lines': 10, 'words': 100, 'size': 456, 'preview': 'First 500 chars...'}
```
## Run tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## VSCode Integration

Example for `.vscode/mcp.json`:
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
# Inside WSL
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
## Main Dependencies (see requirements.txt for full list)
- mcp>=1.10.0
- aiofiles==24.1.0
- httpx==0.28.1
- pydantic==2.11.3
- pytest==8.3.5
- pytest-asyncio==0.26.0

**Requires Python 3.13**

## References
- [MCP Python SDK & Examples](https://github.com/modelcontextprotocol/create-python-server)

## Build Docker Image
docker build -t mcp-file-url-analyzer:latest .

## Bash example: MCP stdio protocol (Docker)
See the file `analyze-hosts.sh` in the project root for a ready-to-use example.

## Python example: MCP stdio protocol (Docker)
See the file `analyze-hosts.py` in the project root for a ready-to-use Python script.

