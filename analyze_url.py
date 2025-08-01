# -*- coding: utf-8 -*-
"""
CLI tool to analyze a URL using the MCP server's analyze-url tool.

Usage:
	python analyze_url.py <url>
"""

import sys
import asyncio
from src.mcp_file_url_analyzer import server

async def main() -> None:
	"""Analyze a URL passed as a command-line argument using analyze-url tool."""
	if len(sys.argv) != 2:
		print("Usage: python analyze_url.py <url>")
		sys.exit(1)
	url = sys.argv[1]
	result = await server.analyze_url_async(url)
	print(result)

if __name__ == "__main__":
	asyncio.run(main())
