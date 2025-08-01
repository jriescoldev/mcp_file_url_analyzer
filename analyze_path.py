# -*- coding: utf-8 -*-
"""
CLI tool to analyze a file or directory path using the MCP server's analyze-path tool.

Usage:
	python analyze_path.py <path>
"""

import sys
import asyncio
from src.mcp_file_url_analyzer import server

async def main() -> None:
	"""Analyze a file or directory path passed as a command-line argument using analyze-path tool."""
	if len(sys.argv) != 2:
		print("Usage: python analyze_path.py <path>")
		sys.exit(1)
	path = sys.argv[1]
	result = await server.analyze_path_async(path)
	print(result)

if __name__ == "__main__":
	asyncio.run(main())
