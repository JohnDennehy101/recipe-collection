import httpx

from .base import BROWSER_HEADERS, BaseFetcher, FetchResult


class HttpxFetcher(BaseFetcher):
    tier = "httpx"

    async def fetch(self, url: str) -> FetchResult:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(url, headers=BROWSER_HEADERS)
            return self._require_usable(resp.status_code, resp.text)
