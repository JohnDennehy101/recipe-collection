import logging

from ..models import Recipe
from .base import ExtractionError
from .mistral import extract_with_mistral
from .recipe_scrapers import extract_known_site, extract_wild_mode

log = logging.getLogger(__name__)

TIERS = (
    (extract_known_site, "recipe-scrapers"),
    (extract_wild_mode, "recipe-scrapers-wild"),
    (extract_with_mistral, "mistral"),
)


def extract_recipe(html: str, source_url: str) -> tuple[Recipe, str]:
    """Returns (recipe, extractor_name). Raises ExtractionError if no tier
    works."""
    for extractor, name in TIERS:
        try:
            return extractor(html, source_url), name
        except Exception as exc:  # noqa: BLE001 - tier fallback is the point
            log.info("extraction tier %s failed for %s: %s", name, source_url, exc)

    raise ExtractionError("no extraction tier succeeded")
