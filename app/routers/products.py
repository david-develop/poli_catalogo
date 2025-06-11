from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.models.models import Article
from app.models.schemas.products import CreateArticleForm
from app.routers.auth import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
router = APIRouter(
    prefix="/productos",
    tags=["productos"],
    responses={404: {"description": "Not found"}},
)


@router.get("/catalogo")
def get_all_articles(request: Request, token: str = Depends(oauth2_scheme)):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    all_articles = request.app.db.query(Article).all()

    return JSONResponse(
        content={
            "articulos": [article.to_json() for article in all_articles] if all_articles else [],
        },
        status_code=status.HTTP_200_OK,
    )


@router.get("/detalle-articulo/{article_id}")
def get_article(
    request: Request, article_id: str, token: str = Depends(oauth2_scheme)
):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    article = request.app.db.query(Article).filter_by(id=article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artículo no encontrado",
        )
    return JSONResponse(
        content={
            "articulo": article.to_json(),
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/agregar-articulo", status_code=status.HTTP_201_CREATED)
def add_article(
    request: Request,
    article_data: CreateArticleForm,
    token: str = Depends(oauth2_scheme)
):
    user = get_current_user(request, token)
    if not user or getattr(user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden agregar artículos",
        )
    article = Article(name=article_data.name, category=article_data.category, description=article_data.description, price=article_data.price, stock=article_data.stock)
    request.app.db.add(article)
    request.app.db.commit()
    return JSONResponse(
        content={"message": "Artículo agregado correctamente", "articulo": article.to_json()},
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/actualizar/{article_id}")
def update_article(
    request: Request,
    article_id: str,
    article_data: CreateArticleForm,
    token: str = Depends(oauth2_scheme)
):
    user = get_current_user(request, token)
    if not user or getattr(user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden actualizar artículos",
        )
    article = request.app.db.query(Article).filter_by(id=article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artículo no encontrado",
        )
    article.name = article_data.name
    article.category = article_data.category
    article.description = article_data.description
    article.price = article_data.price
    article.stock = article_data.stock
    request.app.db.add(article)
    request.app.db.commit()
    return JSONResponse(
        content={"message": "Artículo actualizado correctamente"},
        status_code=status.HTTP_200_OK
    )


@router.delete("/eliminar/{article_id}")
def delete_article(
    request: Request,
    article_id: str,
    token: str = Depends(oauth2_scheme)
):
    user = get_current_user(request, token)
    if not user or getattr(user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar artículos",
        )
    article = request.app.db.query(Article).filter_by(id=article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artículo no encontrado",
        )
    request.app.db.delete(article)
    request.app.db.commit()
    return JSONResponse(
        content={"message": "Artículo eliminado correctamente"},
        status_code=status.HTTP_200_OK,
    )

@router.get("/buscar")
def search_articles(
    request: Request,
    query: str,
    token: str = Depends(oauth2_scheme)
):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    articles = request.app.db.query(Article).filter(Article.name.ilike(f"%{query}%")).all()
    if not articles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron artículos",
        )
    return JSONResponse(
        content={
            "articulos": [article.to_json() for article in articles],
        },
        status_code=status.HTTP_200_OK,
    )
