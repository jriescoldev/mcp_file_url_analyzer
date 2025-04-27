#!/bin/bash
# analyze-hosts.sh
# Example: Analyze /etc/hosts using the MCP server via Docker (stdio protocol)
# Requires: docker, .env file, and a running mcp-file-url-analyzer image

echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "analyze-path", "arguments": {"path": "/etc/hosts"}}}' | \
docker run --rm -i --env-file .env mcp-file-url-analyzer
