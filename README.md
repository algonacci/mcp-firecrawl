# mcp-firecrawl

MCP server for guarded asynchronous Firecrawl crawling.

## Setup

```bash
cp .env.example .env
# Add FIRECRAWL_API_KEY to .env
uv sync
```

Register in an MCP client:

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-firecrawl", "run", "main.py"]
    }
  }
}
```

## Tools

- `firecrawl_crawl`: starts an asynchronous crawl and returns a job ID.
- `firecrawl_get_crawl`: retrieves status and available results for a job.

Each job is capped at 20 pages, skips sitemaps, and does not follow external links or subdomains. Firecrawl's free plan currently includes 1,000 monthly credits; a crawl can consume multiple credits.
