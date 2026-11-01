
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    quantity: str = ""
    unit: str = ""
    item: str


class Recipe(BaseModel):
    name: str
    description: str = ""
    servings: int = 0
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    total_time_minutes: int | None = None
    ingredients: list[Ingredient] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    image_url: str = ""
    source_url: str = ""


RECIPE_JSON_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "servings": {"type": "integer"},
        "prep_time_minutes": {"type": ["integer", "null"]},
        "cook_time_minutes": {"type": ["integer", "null"]},
        "total_time_minutes": {"type": ["integer", "null"]},
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "quantity": {"type": "string"},
                    "unit": {"type": "string"},
                    "item": {"type": "string"},
                },
                "required": ["quantity", "unit", "item"],
                "additionalProperties": False,
            },
        },
        "instructions": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "string"}},
        "image_url": {"type": "string"},
        "source_url": {"type": "string"},
    },
    "required": [
        "name",
        "description",
        "servings",
        "prep_time_minutes",
        "cook_time_minutes",
        "total_time_minutes",
        "ingredients",
        "instructions",
        "tags",
        "image_url",
        "source_url",
    ],
    "additionalProperties": False,
}
