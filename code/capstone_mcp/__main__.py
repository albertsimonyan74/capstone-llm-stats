# capstone_mcp/__main__.py
"""Allow running the server via `python -m capstone_mcp`."""
from capstone_mcp.server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
