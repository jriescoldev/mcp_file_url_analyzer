#!/usr/bin/env python3
"""
Python script to interact with the MCP server via Docker (stdio protocol).
Sends 'initialize', waits for response, then sends 'tools/call' to analyze /etc/hosts.
"""
import json
import subprocess
import sys
from pprint import pprint

# Allow URL as command-line argument
url = sys.argv[1] if len(sys.argv) > 1 else "https://www.github.com/"

INIT_MSG = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "1.0",
        "capabilities": {},
        "clientInfo": {"name": "python-script", "version": "1.0"}
    }
}

TOOL_MSG = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "analyze-url",
        "arguments": {"url": url}
    }
}

# Start the Docker container as a subprocess
proc = subprocess.Popen(
    ["docker", "run", "--rm", "-i", "--env-file", ".env", "mcp-file-url-analyzer"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Send initialize
print("[client] Sending initialize...")
proc.stdin.write(json.dumps(INIT_MSG) + "\n")
proc.stdin.flush()

# Read and print the response to initialize
while True:
    line = proc.stdout.readline()
    if not line:
        break
    print("[server]", line.strip())
    try:
        resp = json.loads(line)
        if resp.get("id") == 1:
            break
    except Exception:
        continue

# Send tools/call
print("[client] Sending tools/call (analyze-url)...")
proc.stdin.write(json.dumps(TOOL_MSG) + "\n")
proc.stdin.flush()

# Read and print the response to tools/call
while True:
    line = proc.stdout.readline()
    if not line:
        break
    try:
        resp = json.loads(line)
        if resp.get("id") == 2:
            print("[server] Response to tools/call:")
            pprint(resp)
            break
    except Exception:
        print("[server]", line.strip())
        continue

proc.stdin.close()
proc.stdout.close()
proc.wait()
