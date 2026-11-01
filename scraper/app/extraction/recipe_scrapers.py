from ..models import Recipe
from .base import parse_servings, split_ingredient


def extract_known_site(html: str, source_url: str) -> Recipe:
    """Tier 1: dedicated parser for a site recipe-scrapers knows."""
    from recipe_scrapers import scrape_html

    scraper = scrape_html(html, source_url, supported_only=True)
    return _from_scraper(scraper, source_url)


def extract_wild_mode(html: str, source_url: str) -> Recipe:
    """Tier 2: generic schema.org Recipe parsing for unknown sites
    (recipe-scrapers with supported_only=False; formerly wild_mode)."""
    from recipe_scrapers import scrape_html

    scraper = scrape_html(html, source_url, supported_only=False)
    recipe = _from_scraper(scraper, source_url)
    if not recipe.ingredients or not recipe.instructions:
        raise ValueError("wild mode found no ingredients or instructions")
    return recipe


def _from_scraper(scraper: "object", source_url: str) -> Recipe:
    recipe = Recipe(
        name=scraper.title() or "",
        description=scraper.description() or "",
        servings=parse_servings(scraper.yields()),
        prep_time_minutes=_call_or_none(scraper, "prep_time"),
        cook_time_minutes=_call_or_none(scraper, "cook_time"),
        total_time_minutes=_call_or_none(scraper, "total_time"),
        ingredients=[split_ingredient(i) for i in scraper.ingredients()],
        instructions=list(scraper.instructions_list()),
        tags=[],
        image_url=scraper.image() or "",
        source_url=source_url,
    )
    if not recipe.name:
        raise ValueError("scraper found no recipe title")
    return recipe


def _call_or_none(scraper: object, method: str) -> int | None:
    try:
        value = getattr(scraper, method)()
    except Exception:  # noqa: BLE001 - many sites omit these fields
        return None
    return value if isinstance(value, int) else None
