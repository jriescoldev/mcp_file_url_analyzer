"""
MCP server in Python that analyzes local files and URLs (text and binary).

- Requires Python >=3.12
- Install dependencies with `pip install -r requirements.txt`
- Run the server with `python -m src.mcp_file_url_analyzer.server`
- Docker support: see README for usage
- Security: SSRF protection, file/URL size limits (5MB)
- Never commit your .env file to public repositories

Example usage:
    from mcp.client import MCPClient
    client = MCPClient()
    result = await client.tool('analyze-path', path='/path/to/file.txt')
    print(result)

More information and examples at https://github.com/modelcontextprotocol/create-python-server
"""

import os
import mimetypes
import types
import logging
import ipaddress
import asyncio
from urllib.parse import urlparse
import traceback

import httpx
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
)
logger = logging.getLogger("mcp-file-url-analyzer")

print("[mcp-file-url-analyzer] FastMCP and dependencies imported successfully.")

mcp = FastMCP("mcp-file-url-analyzer")

@mcp.tool()
def analyze_path(path: str) -> dict:
    """Analyze a local file or directory (text or binary)."""
    if not os.path.exists(path):
        return {"error": f"Path not found: {path}"}
    if os.path.isfile(path):
        return _analyze_file(path)
    if os.path.isdir(path):
        results = {}
        for root, _, files in os.walk(path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                results[file_path] = _analyze_file(file_path)
        return results
    return {"error": "Path is neither file nor directory"}

# --- SSRF protection: global, reusable and tested ---
def is_safe_url(url: str) -> bool:
    """Return True if the URL is considered safe for remote 
    access (no localhost, no private IPs)."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        if hostname in ("localhost", "127.0.0.1", "::1"):
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                return False
        except ValueError:
            pass
        return True
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("is_safe_url: Exception for %s: %s", url, exc)
        return False

@mcp.tool()
def analyze_url(url: str) -> dict:
    """Download and analyze the content of a URL (text or binary)."""
    if not is_safe_url(url):
        logger.warning("Blocked unsafe URL: %s", url)
        return {"error": "URL not allowed for security reasons."}

    max_url_size = 5 * 1024 * 1024

    async def fetch():
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, follow_redirects=True, timeout=10)
                content_length = int(resp.headers.get("content-length", 0))
                if content_length > max_url_size:
                    return {"error": (
                        f"Remote file too large (>"
                        f"{max_url_size // (1024*1024)} MB)"
                    )}
                content_bytes = await resp.aread()
                if len(content_bytes) > max_url_size:
                    return {"error": (
                        "Downloaded file too large (>"
                        f"{max_url_size // (1024*1024)} MB)"
                    )}
                mime, _ = mimetypes.guess_type(url)
                content_type = resp.headers.get("content-type", mime or "unknown")
                if "text" in content_type:
                    try:
                        text = content_bytes.decode(errors="replace")
                    except UnicodeDecodeError as exc:
                        return {
                            "error": f"Could not decode content as text: {exc}",
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
                return {
                    "type": "binary",
                    "content_type": content_type,
                    "size": len(content_bytes),
                    "preview_bytes": content_bytes[:32].hex(),
                }
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("analyze_url: Exception fetching %s: %s", url, exc)
            return {"error": f"Failed to fetch or analyze URL: {exc}"}
    try:
        asyncio.get_running_loop()
        return fetch()
    except RuntimeError:
        return asyncio.run(fetch())

def _get_max_file_size():
    try:
        return int(os.environ.get("MAX_FILE_SIZE", 5 * 1024 * 1024))
    except (ValueError, TypeError):
        return 5 * 1024 * 1024

def _analyze_file(path: str) -> dict:
    """Analyze a local file. Returns basic info about the file."""
    max_file_size = _get_max_file_size()
    mime, _ = mimetypes.guess_type(path)
    try:
        size = os.path.getsize(path)
        if size > max_file_size:
            return {"error": (
                f"File too large (>"
                f"{max_file_size // (1024*1024)} MB)"
            )}
        with open(path, mode="rb") as file_obj:
            content = file_obj.read()
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
        return {
            "type": "binary",
            "mime": mime or "unknown",
            "size": len(content),
            "preview_bytes": content[:32].hex(),
        }
    except (OSError, UnicodeDecodeError) as exc:
        return {"error": f"Error reading file: {exc}"}

if __name__ == "__main__":
    print("[mcp-file-url-analyzer] MCP server starting... (Python)")
    try:
        mcp.run()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"[mcp-file-url-analyzer] MCP server failed to start: {exc}")
        traceback.print_exc()

# --- Handlers for testing (not used in production server) ---

async def handle_list_resources():
    """Return an empty list (no resources supported)."""
    return []

async def handle_call_tool(tool_name, args):
    """Call the appropriate tool handler based on tool_name."""
    if tool_name == 'analyze-path':
        if not args or 'path' not in args:
            raise ValueError('Missing path')
        return await _analyze_path(args['path'])
    if tool_name == 'analyze-url':
        if not args or 'url' not in args:
            raise ValueError('Missing url')
        return await _analyze_url(args['url'])
    raise ValueError('Unknown tool')

async def handle_read_resource(uri):
    """Raise error (no resources supported)."""
    raise ValueError('Unsupported URI')

async def handle_list_tools():
    """Return the list of available tools."""
    tool = types.SimpleNamespace
    return [
        tool(name='analyze-path'),
        tool(name='analyze-url'),
    ]

async def handle_get_prompt(prompt_name, args):
    """Raise error (no prompts implemented)."""
    _ = args  # Unused argument
    if prompt_name != 'summarize-notes':
        raise ValueError('Unknown prompt')
    # Not implemented in this server
    raise NotImplementedError('No prompts implemented')

async def _analyze_path(path: str):
    """Analyze a file or directory asynchronously for testing."""
    if not os.path.exists(path):
        return {"error": f"Path not found: {path}"}
    if os.path.isfile(path):
        return _analyze_file(path)
    if os.path.isdir(path):
        results = {}
        for root, _, files in os.walk(path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                results[file_path] = _analyze_file(file_path)
        return results
    return {"error": "Path is neither file nor directory"}

async def _analyze_url(url: str):
    """Analyze a URL asynchronously for testing."""
    if not is_safe_url(url):
        return {"error": "URL not allowed for security reasons."}
    max_url_size = 5 * 1024 * 1024
    async def fetch():
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True)
            content_length = int(resp.headers.get("content-length", 0))
            if content_length > max_url_size:
                return {"error": (
                    "Remote file too large (>"
                    f"{max_url_size // (1024*1024)} MB)"
                )}
            content_bytes = await resp.aread()
            if len(content_bytes) > max_url_size:
                return {"error": (
                    "Downloaded file too large (>"
                    f"{max_url_size // (1024*1024)} MB)"
                )}
            mime, _ = mimetypes.guess_type(url)
            content_type = resp.headers.get("content-type", mime or "unknown")
            if "text" in content_type:
                try:
                    text = content_bytes.decode(errors="replace")
                except UnicodeDecodeError as exc:
                    return {
                        "error": f"Could not decode content as text: {exc}",
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
            return {
                "type": "binary",
                "content_type": content_type,
                "size": len(content_bytes),
                "preview_bytes": content_bytes[:32].hex(),
            }
    return await fetch()

async def analyze_url_async(url: str):
    """Public async wrapper for _analyze_url (for testing and external use)."""
    return await _analyze_url(url)

async def analyze_path_async(path: str):
    """Public async wrapper for _analyze_path (for testing and external use)."""
    return await _analyze_path(path)

MAX_FILE_SIZE = 5 * 1024 * 1024

# Export for tests
__all__ = [
    'handle_list_resources',
    'handle_call_tool',
    'handle_read_resource',
    'handle_list_tools',
    'handle_get_prompt',
    'is_safe_url',
    '_analyze_path',
    '_analyze_url',
    'analyze_url_async',
    'analyze_path_async',
    'MAX_FILE_SIZE',
]
