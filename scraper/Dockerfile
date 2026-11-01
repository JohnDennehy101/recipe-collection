FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app
# crawl4ai works fully local with no API key; this only hides its cloud
# promo banner from the service logs.
ENV CRAWL4AI_NO_CLOUD_NOTICE=1

# Copy lock metadata first so dependency install layer-caches independently of
# app code changes.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

COPY app ./app
# playwright: browser for crawl4ai (tier 2). patchright: stealth-patched
# Playwright for tier 3; shares the same browser cache directory.
RUN uv run --no-dev playwright install --with-deps chromium && \
    uv run --no-dev patchright install chromium

EXPOSE 8000
CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
