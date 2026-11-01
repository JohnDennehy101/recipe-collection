import os

import httpx

from .base import BaseFetcher, FetchResult


class Crawl4AiCloudFetcher(BaseFetcher):
    tier = "crawl4ai-cloud"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("CRAWL4AI_KEY", "")
        self.base_url = base_url or os.environ.get("CRAWL4AI_URL", "https://api.crawl4ai.com")

    def available(self) -> bool:
        return bool(self.api_key)

    async def fetch(self, url: str) -> FetchResult:
        if not self.api_key:
            raise RuntimeError("CRAWL4AI_KEY not set; cloud tier disabled")

        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(
                f"{self.base_url}/scrape",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"url": url, "format": "html"},
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"{self.tier}: cloud scrape returned {resp.status_code}: {resp.text[:200]}"
                )
            data = resp.json()

        # Prefer raw HTML (needed by the recipe-scrapers tiers). If the
        # service only returns markdown, the JSON-LD tiers will fail but the
        # Mistral tier still extracts from the text.
        html = data.get("html") or data.get("markdown") or ""
        status = data.get("status") or data.get("status_code") or 200
        return self._require_usable(int(status), html)
