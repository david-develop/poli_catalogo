from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.models.models import Article
from app.models.schemas.products import (AdvancedSearchForm, CreateArticleForm,
                                         UpdateArticleForm)
from app.routers.auth import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
router = APIRouter(
    prefix="/productos",
    tags=["productos"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
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
            "articulos": (
                [article.to_json() for article in all_articles] if all_articles else []
            ),
        },
        status_code=status.HTTP_200_OK,
    )


@router.get("/detalle-articulo/{article_id}")
def get_article(request: Request, article_id: str, token: str = Depends(oauth2_scheme)):
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
    token: str = Depends(oauth2_scheme),
):
    user = get_current_user(request, token)
    if not user or getattr(user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden agregar artículos",
        )
    article = Article(
        name=article_data.name,
        category=article_data.category,
        description=article_data.description,
        price=article_data.price,
        stock=article_data.stock,
    )
    request.app.db.add(article)
    request.app.db.commit()
    return JSONResponse(
        content={
            "message": "Artículo agregado correctamente",
            "articulo": article.to_json(),
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/agregar-multiples-articulos", status_code=status.HTTP_201_CREATED)
def add_multiple_articles(
    request: Request,
    articles_data: list[CreateArticleForm],
    token: str = Depends(oauth2_scheme),
):
    user = get_current_user(request, token)
    if not user or getattr(user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden agregar artículos",
        )
    articles = []
    for article_data in articles_data:
        article = Article(
            name=article_data.name,
            category=article_data.category,
            description=article_data.description,
            price=article_data.price,
            stock=article_data.stock,
        )
        articles.append(article)
        request.app.db.add(article)
    request.app.db.commit()
    return JSONResponse(
        content={
            "message": "Artículos agregados correctamente",
            "articulos": [article.to_json() for article in articles],
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/actualizar/{article_id}")
def update_article(
    request: Request,
    article_id: str,
    article_data: UpdateArticleForm,
    token: str = Depends(oauth2_scheme),
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
    if not article_data.any_field_set():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar",
        )

    cambios = False
    for field, value in article_data.model_dump(exclude_unset=True).items():
        if getattr(article, field) != value:
            setattr(article, field, value)
            cambios = True

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se cambió ningún campo",
        )

    request.app.db.add(article)
    request.app.db.commit()
    return JSONResponse(
        content={"message": "Artículo actualizado correctamente"},
        status_code=status.HTTP_200_OK,
    )


@router.delete("/eliminar/{article_id}")
def delete_article(
    request: Request, article_id: str, token: str = Depends(oauth2_scheme)
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
def search_articles(request: Request, query: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    articles = (
        request.app.db.query(Article).filter(Article.name.ilike(f"%{query}%")).all()
    )
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


@router.post("/busqueda-avanzada")
def advanced_search(
    request: Request,
    search: AdvancedSearchForm,
    token: str = Depends(oauth2_scheme),
):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    query = request.app.db.query(Article)
    if search.name:
        query = query.filter(Article.name.ilike(f"%{search.name}%"))
    if search.category:
        query = query.filter(Article.category.ilike(f"%{search.category}%"))
    if search.min_price is not None:
        query = query.filter(Article.price >= search.min_price)
    if search.max_price is not None:
        query = query.filter(Article.price <= search.max_price)
    results = query.all()
    return JSONResponse(
        content={"articulos": [a.to_json() for a in results]},
        status_code=status.HTTP_200_OK,
    )
