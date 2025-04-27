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

    # Add and read a note
    await client.tool('add-note', name='my-note', content='hello')
    content = await client.resource('note://my-note')
    print(content)
"""

import asyncio

def main():
    """Main entry point for the package."""
    from . import server

    asyncio.run(server.main())

__all__ = ['main', 'server']
