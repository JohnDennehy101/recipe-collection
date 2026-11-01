import logging

from fastapi import APIRouter, HTTPException

from .extraction import ExtractionError, extract_recipe
from .retrieval import FetchError, default_chain
from .schemas import ScrapeRequest, ScrapeResponse

log = logging.getLogger(__name__)

router = APIRouter()
# Module-level so tests can swap in a chain of fake fetchers.
chain = default_chain()

@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape(req: ScrapeRequest) -> ScrapeResponse:
    url = str(req.url)
    try:
        result = await chain.fetch(url)
    except FetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        recipe, extractor = extract_recipe(result.html, url)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    log.info("scraped %s via tier=%s extractor=%s", url, result.tier, extractor)
    return ScrapeResponse(
        recipe=recipe,
        fetch={"tier": result.tier, "extractor": extractor},
    )
