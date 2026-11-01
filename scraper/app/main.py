import logging

from fastapi import FastAPI

from .routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="recipe-scraper")
app.include_router(router)
