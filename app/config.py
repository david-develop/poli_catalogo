import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Catalogo Poli"
    db_url: str = "sqlite:///./test.db"
    jwt_secret: str = os.getenv("JWT_SECRET")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")


settings = Settings()
