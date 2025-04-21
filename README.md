# mcp-file-url-analyzer MCP server

Servidor MCP que analiza archivos locales o URLs proporcionadas

## Components

### Resources

The server implements a simple note storage system with:
- Custom note:// URI scheme for accessing individual notes
- Each note resource has a name, description and text/plain mimetype

### Prompts

The server provides a single prompt:
- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration

[TODO: Add configuration details specific to your implementation]

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "mcp-file-url-analyzer": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/javi/prueba",
        "run",
        "mcp-file-url-analyzer"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "mcp-file-url-analyzer": {
      "command": "uvx",
      "args": [
        "mcp-file-url-analyzer"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /home/javi/prueba run mcp-file-url-analyzer
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

## Análisis de archivos y URLs

Este servidor MCP permite analizar archivos individuales, directorios completos y URLs (tanto texto como binario). Usa los comandos MCP:

- `analyze_path(path: str)`: Analiza un archivo o directorio local. Si es directorio, recorre todos los archivos.
- `analyze_url(url: str)`: Descarga y analiza el contenido de la URL (texto o binario).

El análisis de texto muestra número de líneas, palabras, tamaño y un preview. El análisis binario muestra tamaño, tipo y preview en hexadecimal.

## Ejecución local

1. Activa el entorno virtual:
   ```bash
   source .venv/bin/activate
   ```
2. Ejecuta el servidor MCP (desde la raíz del proyecto):
   ```bash
   python -m src.mcp_file_url_analyzer.server
   ```

## Configuración para VS Code

El archivo `.vscode/mcp.json` ya está configurado para depuración y conexión desde VS Code.

## Ejemplos de uso

### Analizar un archivo local
```python
from mcp.client import MCPClient
client = MCPClient()
result = await client.tool('analyze-path', path='/ruta/al/archivo.txt')
print(result)
```

### Analizar un directorio local
```python
result = await client.tool('analyze-path', path='/ruta/al/directorio')
print(result)
```

### Analizar una URL (texto o binario)
```python
result = await client.tool('analyze-url', url='https://ejemplo.com/archivo.txt')
print(result)
```

- El resultado será un diccionario con información relevante según el tipo de archivo o contenido.

## Referencias
- [SDK y ejemplos MCP Python](https://github.com/modelcontextprotocol/create-python-server)