import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Catalogo Poli"
    db_url: str = "sqlite:///./test.db"
    jwt_secret: str = os.getenv("SECRET_KEY")
    jwt_algorithm: str = os.getenv("ALGORITHM")


settings = Settings()
