#!/bin/bash
# analyze-hosts.sh
# Example: Analyze /etc/hosts using the MCP server via Docker (stdio protocol)
# Requires: docker, .env file, and a running mcp-file-url-analyzer image

cat <<EOF | docker run --rm -i --env-file .env mcp-file-url-analyzer
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1.0", "capabilities": {}, "clientInfo": {"name": "bash", "version": "1.0"}}}
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "analyze-path", "arguments": {"path": "/etc/hosts"}}}
EOF
