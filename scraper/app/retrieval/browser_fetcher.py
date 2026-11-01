from .base import BROWSER_HEADERS, BaseFetcher, FetchResult


class BrowserFetcher(BaseFetcher):
    tier = "playwright"

    def __init__(self) -> None:
        try:
            from patchright.async_api import async_playwright

            self.tier = "patchright"
        except ImportError:
            from playwright.async_api import async_playwright

        self._async_playwright = async_playwright

    async def fetch(self, url: str) -> FetchResult:
        async with self._async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ],
            )
            page = await browser.new_page(user_agent=BROWSER_HEADERS["User-Agent"])
            # Extra fingerprint hiding on top of patchright's built-in patches.
            await page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            await page.wait_for_timeout(2000)  # let late JS settle
            html = await page.content()
            await browser.close()

            status = resp.status if resp else 200
            return self._require_usable(status, html)
