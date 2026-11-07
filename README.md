# MCP Project — Deep Research Agent

## Phase 1: research-tools MCP server

`app/server.py` exposes two MCP tools:

| Tool | What it does |
|---|---|
| `web_search(query, max_results=5)` | Tavily search → list of `{title, url, snippet}` |
| `fetch_url(url, max_chars=8000)` | Downloads a page, returns clean main text |

### Setup
```bash
uv sync                      # install dependencies
# .env must contain:  TAVILY_API_KEY=tvly-xxxx
```

### Run / test
```bash
uv run python tests_phase1.py                                   # smoke test via an MCP client
npx @modelcontextprotocol/inspector uv run python app/server.py # visual inspector in browser
```

Note: this uses `mcp` 2.x, where `FastMCP` is called `MCPServer`
(`from mcp.server.mcpserver import MCPServer`).
