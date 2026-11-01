from .base import BaseFetcher, FetchResult


class Crawl4AiFetcher(BaseFetcher):
    tier = "crawl4ai"

    async def fetch(self, url: str) -> FetchResult:
        from crawl4ai import AsyncWebCrawler, CacheMode

        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, cache_mode=CacheMode.BYPASS)
            html = getattr(result, "html", "") or ""
            status = getattr(result, "status_code", None) or 200
            return self._require_usable(status, html)
