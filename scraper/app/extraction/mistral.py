"""Tier 3: Mistral AI structured extraction.

Last resort for pages without usable Recipe schema: ask Mistral for
structured output over the cleaned page text. Costs tokens, so it only runs
when the deterministic tiers have failed.
"""

import os

from bs4 import BeautifulSoup

from ..models import RECIPE_JSON_SCHEMA, Recipe
from .base import ExtractionError

MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")

# Keep the prompt bounded; recipes live near the top of the page.
MAX_TEXT_CHARS = 60_000


def extract_with_mistral(html: str, source_url: str) -> Recipe:
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ExtractionError("MISTRAL_API_KEY is not set")

    from mistralai.client import Mistral  # mistralai >= 3 layout

    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model=MISTRAL_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract recipes from raw web page text. Return ONLY the "
                    "recipe as structured JSON. If a field is missing, use its "
                    "empty/null default. Split each ingredient into quantity, unit "
                    "and item where possible. Set source_url to the value given, "
                    "not one found in the page."
                ),
            },
            {
                "role": "user",
                "content": f"source_url: {source_url}\n\npage text:\n{page_text(html)}",
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "recipe",
                "schema": RECIPE_JSON_SCHEMA,
                "strict": True,
            },
        },
        temperature=0,
    )

    content = response.choices[0].message.content
    recipe = Recipe.model_validate_json(content)
    recipe.source_url = source_url
    if not recipe.name:
        raise ExtractionError("Mistral returned a recipe with no name")
    return recipe


def page_text(html: str) -> str:
    """HTML -> readable text, keeping ingredient/step list structure."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    return text[:MAX_TEXT_CHARS]
