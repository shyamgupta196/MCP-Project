"""
Phase 1 — research-tools MCP server.

Exposes two tools that our research agents will use later:
  - web_search(query, max_results)  -> list of {title, url, snippet}
  - fetch_url(url, max_chars)       -> clean main text of a web page

Run directly (stdio transport):   uv run app/server.py
Inspect in the browser:           npx @modelcontextprotocol/inspector uv run app/server.py
"""

import os

import httpx
import trafilatura
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer  # mcp 2.x name for FastMCP
from tavily import TavilyClient

load_dotenv()  # reads TAVILY_API_KEY from .env

mcp = MCPServer("research-tools")

_tavily: TavilyClient | None = None


def _get_tavily() -> TavilyClient:
    """Create the Tavily client lazily so the server still starts without a key."""
    global _tavily
    if _tavily is None:
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("TAVILY_API_KEY is not set. Add it to your .env file.")
        _tavily = TavilyClient(api_key=key)
    return _tavily


@mcp.tool()
def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web for a query.

    Returns a list of results, each with a title, url and a short snippet.
    Use fetch_url on a result's url to read the full page.
    """
    max_results = max(1, min(max_results, 10))
    resp = _get_tavily().search(query=query, max_results=max_results)
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
        }
        for r in resp.get("results", [])
    ]


@mcp.tool()
def fetch_url(url: str, max_chars: int = 8000) -> str:
    """Download a web page and return its main readable text (no menus/ads).

    Output is cut to max_chars so it fits in the model's context.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: url must start with http:// or https://"
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=20,
            headers={"User-Agent": "research-tools-mcp/0.1"},
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        return f"Error fetching {url}: {e}"

    text = trafilatura.extract(resp.text, url=url) or ""
    if not text:
        return f"Could not extract readable text from {url}"
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n[truncated — {len(text)} chars total]"
    return text


if __name__ == "__main__":
    mcp.run()  # default transport = stdio
