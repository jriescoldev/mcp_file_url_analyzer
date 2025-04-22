"""
MCP file URL analyzer package entry point.

- Requiere Python >=3.12
- Instala dependencias con `pip install -r requirements.txt`
- Ejecuta el servidor con `python -m src.mcp_file_url_analyzer.server`
- El archivo `.env` debe estar en `.gitignore` y nunca subirse a repositorios públicos.

Más información y ejemplos en https://github.com/modelcontextprotocol/create-python-server
"""

import asyncio

def main():
    """Main entry point for the package."""
    from . import server

    asyncio.run(server.main())

__all__ = ['main', 'server']
