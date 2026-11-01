from dataclasses import dataclass

BOT_WALL_MARKERS = (
    "just a moment",
    "checking your browser",
    "enable javascript and cookies",
    "attention required",
    "cf-browser-verification",
    "verify you are a human",
)

# Only the head of the document is scanned; challenge markers live in the
# first few KB.
BOT_WALL_SCAN_CHARS = 20_000

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class FetchError(Exception):
    """All fetch tiers failed."""


@dataclass(frozen=True)
class FetchResult:
    html: str
    tier: str


def is_bad_status(status_code: int) -> bool:
    """Any 4xx/5xx: not a real page. 404s in particular must not reach
    extraction, or the LLM tier will invent a recipe out of an error page."""
    return status_code >= 400


def looks_like_bot_wall(html: str) -> bool:
    """Challenge-page markers in the HTML body."""
    lowered = html[:BOT_WALL_SCAN_CHARS].lower()
    return any(marker in lowered for marker in BOT_WALL_MARKERS)


class BaseFetcher:
    """One retrieval tier. Subclasses implement fetch() and return its result
    via _require_usable(), which refuses error and challenge pages so the
    chain falls through to the next tier instead of extracting garbage."""

    tier: str = "base"

    def available(self) -> bool:
        """False skips the tier in the chain (e.g. no API key configured)."""
        return True

    async def fetch(self, url: str) -> FetchResult:
        raise NotImplementedError

    def _require_usable(self, status: int, html: str) -> FetchResult:
        if is_bad_status(status):
            raise RuntimeError(f"{self.tier}: bad status {status}")
        if not html or looks_like_bot_wall(html):
            raise RuntimeError(f"{self.tier}: bot wall or no usable page")
        return FetchResult(html=html, tier=self.tier)
