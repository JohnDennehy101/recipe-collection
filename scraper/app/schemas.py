from pydantic import BaseModel, HttpUrl

from .models import Recipe


class ScrapeRequest(BaseModel):
    url: HttpUrl


class FetchMeta(BaseModel):
    tier: str
    extractor: str


class ScrapeResponse(BaseModel):
    recipe: Recipe
    fetch: FetchMeta
