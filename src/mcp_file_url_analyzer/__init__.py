"""
Entry point for the mcp-file-url-analyzer package.

- Requires Python >=3.12
- See README.md for installation, usage, and security notes

Example usage:
    from mcp.client import MCPClient
    client = MCPClient()
    result = await client.tool('analyze-path', path='/path/to/file.txt')
    print(result)

    # Analyze a URL
    result = await client.tool('analyze-url', url='https://example.com/file.txt')
    print(result)
"""

import asyncio

from . import server

def main():
    """Main entry point for the package."""
    server.mcp.run()

__all__ = ['main', 'server']
