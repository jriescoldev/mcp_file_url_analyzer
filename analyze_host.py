"""
Python script to interact with the MCP server via Docker (stdio protocol).
Sends 'tools/call' to analyze a URL (no initialize message needed).
"""
import json
import subprocess
import sys
from pprint import pprint

# Allow URL as command-line argument
url = sys.argv[1] if len(sys.argv) > 1 else "https://www.github.com/"

TOOL_MSG = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "analyze-url",
        "arguments": {"url": url}
    }
}

# Start the Docker container as a subprocess using a context manager
with subprocess.Popen(
    ["docker", "run", "--rm", "-i", "--env-file", ".env", "mcp-file-url-analyzer"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
) as proc:
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
            if resp.get("id") == 1:
                print("[server] Response to tools/call:")
                pprint(resp)
                break
        except json.JSONDecodeError:
            print("[server]", line.strip())
            continue
