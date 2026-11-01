import logging
from collections.abc import Sequence

from .base import BaseFetcher, FetchError, FetchResult
from .browser_fetcher import BrowserFetcher
from .cloud_fetcher import Crawl4AiCloudFetcher
from .crawl4ai_fetcher import Crawl4AiFetcher
from .httpx_fetcher import HttpxFetcher

log = logging.getLogger(__name__)


class FetchChain:
    def __init__(self, tiers: Sequence[BaseFetcher]) -> None:
        self.tiers = tuple(tiers)

    async def fetch(self, url: str) -> FetchResult:
        errors: list[str] = []
        for tier in self.tiers:
            if not tier.available():
                log.debug("skipping disabled fetch tier %s", tier.tier)
                continue
            try:
                result = await tier.fetch(url)
                if result and result.html:
                    log.info("fetched %s via tier=%s", url, result.tier)
                    return result
                errors.append(f"{tier.tier}: empty page")
            except Exception as exc:  # noqa: BLE001 - tier fallback is the point
                log.warning("fetch tier %s failed for %s: %s", tier.tier, url, exc)
                errors.append(f"{tier.tier}: {exc}")
        raise FetchError("all fetch tiers failed: " + "; ".join(errors))


def default_chain() -> FetchChain:
    """Production wiring: cheapest tiers first, paid cloud tier last."""
    return FetchChain(
        (
            HttpxFetcher(),
            Crawl4AiFetcher(),
            BrowserFetcher(),
            Crawl4AiCloudFetcher(),
        )
    )
