import os
import re
from typing import Optional
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

load_dotenv()

mcp = FastMCP("Firecrawl")
BASE_URL = "https://api.firecrawl.dev/v2"
MAX_PAGES = 20


def api_key() -> str:
    key = os.getenv("FIRECRAWL_API_KEY")
    if not key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")
    return key


def error(exc: Exception) -> dict:
    if isinstance(exc, httpx.HTTPStatusError):
        return {"success": False, "status_code": exc.response.status_code,
                "error": f"Firecrawl returned HTTP {exc.response.status_code}"}
    return {"success": False, "error": str(exc)}


@mcp.tool()
async def firecrawl_crawl(
    url: str,
    prompt: Optional[str] = None,
    max_pages: int = 10,
    max_depth: int = 2,
    ctx: Context = None,
) -> dict:
    """Start a guarded asynchronous Firecrawl job and return its ID."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"success": False, "error": "a valid HTTP(S) URL is required"}
    limit = max(1, min(max_pages, MAX_PAGES))
    body = {
        "url": url, "maxDiscoveryDepth": max(0, min(max_depth, 5)), "limit": limit,
        "sitemap": "skip", "allowExternalLinks": False, "allowSubdomains": False,
        "scrapeOptions": {"formats": ["markdown"], "onlyMainContent": True,
                          "storeInCache": True},
    }
    if prompt:
        body["prompt"] = prompt[:2000]
    if ctx:
        ctx.info(f"Starting Firecrawl job for {url} (up to {limit} pages)")
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(f"{BASE_URL}/crawl",
                                         headers={"Authorization": f"Bearer {api_key()}"},
                                         json=body)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        return error(exc)


@mcp.tool()
async def firecrawl_get_crawl(crawl_id: str, ctx: Context = None) -> dict:
    """Get status and available page results for a Firecrawl job."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", crawl_id):
        return {"success": False, "error": "invalid crawl_id"}
    if ctx:
        ctx.info(f"Checking Firecrawl job: {crawl_id}")
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.get(f"{BASE_URL}/crawl/{crawl_id}",
                                        headers={"Authorization": f"Bearer {api_key()}"})
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        return error(exc)


if __name__ == "__main__":
    mcp.run()
