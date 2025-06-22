from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import Base, db_instance
from app.routers import auth, cart, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db = db_instance.get_session()
    Base.metadata.create_all(bind=db_instance.engine)
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

app.include_router(products.router)

app.include_router(cart.router)
