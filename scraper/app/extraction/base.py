from ..models import Ingredient


class ExtractionError(Exception):
    """No extraction tier succeeded."""


def split_ingredient(raw: str) -> Ingredient:
    """Best-effort split of '2 cups flour' into quantity/unit/item.

    Deliberately naive; the Mistral tier and a later manual edit pass fix
    whatever this gets wrong.
    """
    parts = raw.strip().split(maxsplit=2)
    if len(parts) == 1:
        return Ingredient(quantity="", unit="", item=parts[0])
    if len(parts) == 2:
        return Ingredient(quantity=parts[0], unit="", item=parts[1])
    return Ingredient(quantity=parts[0], unit=parts[1], item=parts[2])


def parse_servings(yields: str) -> int:
    """'4 servings' / 'Serves 6' -> int, 0 if unparseable."""
    digits = "".join(ch for ch in (yields or "").strip() if ch.isdigit())
    return int(digits) if digits else 0
