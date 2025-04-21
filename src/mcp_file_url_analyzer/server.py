"""
Servidor MCP en Python que analiza archivos locales y URLs (texto y binario).

- Requiere Python >=3.12
- Instala dependencias con `pip install -r requirements.txt`
- Ejecuta el servidor con `python -m src.mcp_file_url_analyzer.server`
- El archivo `.env` debe estar en `.gitignore` y nunca subirse a repositorios públicos.

Más información y ejemplos en https://github.com/modelcontextprotocol/create-python-server
"""

import sys, os
"""
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
"""
import mimetypes
import aiofiles
import httpx
# from pydantic import AnyUrl  # No usar AnyUrl, usar str
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as types
import mcp.server.stdio

notes: dict[str, str] = {}
server = Server("mcp-file-url-analyzer")


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """
    return [
        types.Resource(
            uri=f"note://internal/{name}",
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """
    # uri es un string tipo 'note://internal/NAME'
    if not uri.startswith("note://internal/"):
        raise ValueError(f"Unsupported URI: {uri}")
    name = uri[len("note://internal/"):]
    if name in notes:
        return notes[name]
    raise ValueError(f"Note not found: {name}")


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return [
        types.Prompt(
            name="summarize-notes",
            description="Creates a summary of all notes",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Style of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    if name != "summarize-notes":
        raise ValueError(f"Unknown prompt: {name}")

    style = (arguments or {}).get("style", "brief")
    detail_prompt = " Give extensive details." if style == "detailed" else ""

    return types.GetPromptResult(
        description="Summarize the current notes",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                    + "\n".join(
                        f"- {name}: {content}"
                        for name, content in notes.items()
                    ),
                ),
            )
        ],
    )


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="add-note",
            description="Add a new note",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["name", "content"],
            },
        ),
        types.Tool(
            name="analyze-path",
            description="Analiza un archivo o directorio local (texto o binario)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta al archivo o directorio"},
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name="analyze-url",
            description="Descarga y analiza el contenido de una URL (texto o binario)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL a analizar"},
                },
                "required": ["url"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name == "add-note":
        if not arguments:
            raise ValueError("Missing arguments")
        note_name = arguments.get("name")
        content = arguments.get("content")
        if not note_name or not content:
            raise ValueError("Missing name or content")
        notes[note_name] = content
        await server.request_context.session.send_resource_list_changed()
        return [
            types.TextContent(
                type="text",
                text=f"Added note '{note_name}' with content: {content}",
            )
        ]
    elif name == "analyze-path":
        if not arguments or "path" not in arguments:
            raise ValueError("Missing 'path' argument")
        path = arguments["path"]
        result = await _analyze_path(path)
        return [types.TextContent(type="text", text=str(result))]
    elif name == "analyze-url":
        if not arguments or "url" not in arguments:
            raise ValueError("Missing 'url' argument")
        url = arguments["url"]
        result = await _analyze_url(url)
        return [types.TextContent(type="text", text=str(result))]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _analyze_path(path: str) -> dict:
    """
    Analiza un archivo o directorio local.
    Si es archivo, devuelve info básica. Si es directorio, analiza todos los archivos dentro.
    """
    if not os.path.exists(path):
        return {"error": f"Path not found: {path}"}
    if os.path.isfile(path):
        return await _analyze_file(path)
    elif os.path.isdir(path):
        results = {}
        for root, _, files in os.walk(path):
            for f in files:
                file_path = os.path.join(root, f)
                results[file_path] = await _analyze_file(file_path)
        return results
    else:
        return {"error": "Path is neither file nor directory"}


async def _analyze_url(url: str) -> dict:
    """
    Descarga y analiza el contenido de una URL (texto o binario).
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        mime, _ = mimetypes.guess_type(url)
        content_type = resp.headers.get("content-type", mime or "unknown")
        content_bytes = await resp.aread()
        if "text" in content_type:
            try:
                text = content_bytes.decode(errors="replace")
            except UnicodeDecodeError as e:
                return {
                    "error": f"No se pudo decodificar el contenido como texto: {e}",
                    "content_type": content_type,
                    "size": len(content_bytes),
                }
            return {
                "type": "text",
                "content_type": content_type,
                "lines": len(text.splitlines()),
                "words": len(text.split()),
                "size": len(content_bytes),
                "preview": text[:500],
            }
        else:
            return {
                "type": "binary",
                "content_type": content_type,
                "size": len(content_bytes),
                "preview_bytes": content_bytes[:32].hex(),
            }


async def _analyze_file(path: str) -> dict:
    """
    Analiza un archivo local.
    Devuelve info básica sobre el archivo.
    """
    mime, _ = mimetypes.guess_type(path)
    try:
        async with aiofiles.open(path, mode="rb") as f:
            content = await f.read()
        if mime and "text" in mime:
            text = content.decode(errors="replace")
            return {
                "type": "text",
                "mime": mime,
                "lines": len(text.splitlines()),
                "words": len(text.split()),
                "size": len(content),
                "preview": text[:500],
            }
        else:
            return {
                "type": "binary",
                "mime": mime or "unknown",
                "size": len(content),
                "preview_bytes": content[:32].hex(),
            }
    except (OSError, UnicodeDecodeError) as e:
        return {"error": str(e)}


async def main():
    """
    Entry point for the MCP server. Runs the server using stdin/stdout streams.
    Sets up the server with its name, version, and capabilities.
    """
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-file-url-analyzer",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        print(f"[server error] Exception in main: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
