from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.models.models import Article, Cart, CartItemModel
from app.models.schemas.cart import CartItem
from app.routers.auth import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
router = APIRouter(
    prefix="/carrito",
    tags=["carrito"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/comprar")
def purchase_items(
    request: Request,
    token: str = Depends(oauth2_scheme),
):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    cart = request.app.db.query(Cart).filter_by( user_id=user.id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
        )
    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío"
        )
    total_price = 0
    total_quantity = 0
    for item in cart.items:
        article = request.app.db.query(Article).filter_by(id=item.article_id).first()
        if not article or article.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock insuficiente para algunos artículos",
            )
        total_price += article.price * item.quantity
        article.stock -= item.quantity
        total_quantity += item.quantity

    request.app.db.query(CartItemModel).filter_by(cart_id=cart.id).delete()
    request.app.db.delete(cart)
    request.app.db.commit()
    return JSONResponse(
        content={
            "message": "Compra realizada con éxito",
            "cantidad_articulos": len(cart.items),
            "precio_total": total_price,
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/agregar")
def add_to_cart(
    request: Request,
    purchase: CartItem,
    token: str = Depends(oauth2_scheme),
):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    cart = request.app.db.query(Cart).filter_by(user_id=user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        request.app.db.add(cart)
        request.app.db.commit()
    article = request.app.db.query(Article).filter_by(id=purchase.article_id).first()
    if not article or article.stock < purchase.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente"
        )
    cart_item = (
        request.app.db.query(CartItemModel)
        .filter_by(cart_id=cart.id, article_id=article.id)
        .first()
    )
    if cart_item:
        cart_item.quantity += purchase.quantity
    else:
        cart_item = CartItemModel(
            cart_id=cart.id, article_id=article.id, quantity=purchase.quantity
        )
        request.app.db.add(cart_item)
    request.app.db.commit()
    return JSONResponse(
        content={"message": "Artículo agregado al carrito",
                 "cart_id": cart.id},
        status_code=status.HTTP_200_OK,
    )


@router.delete("/eliminar/{article_id}")
def remove_from_cart(
    request: Request,
    article_id: str,
    token: str = Depends(oauth2_scheme),
):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    cart = request.app.db.query(Cart).filter_by(user_id=user.id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
        )
    cart_item = (
        request.app.db.query(CartItemModel)
        .filter_by(cart_id=cart.id, article_id=article_id)
        .first()
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artículo no encontrado en el carrito",
        )
    request.app.db.delete(cart_item)
    request.app.db.commit()
    return JSONResponse(
        content={"message": "Artículo eliminado del carrito"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/")
def get_cart(
    request: Request,
    token: str = Depends(oauth2_scheme),
):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    cart = request.app.db.query(Cart).filter_by(user_id=user.id).first()
    if not cart:
        return JSONResponse(
            content={"items": [], "total_price": 0}, status_code=status.HTTP_200_OK
        )
    items = []
    total = 0
    for item in cart.items:
        article = request.app.db.query(Article).filter_by(id=item.article_id).first()
        if article:
            subtotal = article.price * item.quantity
            items.append(
                {
                    "article_id": article.id,
                    "name": article.name,
                    "price": article.price,
                    "quantity": item.quantity,
                    "total": subtotal,
                }
            )
            total += subtotal
    return JSONResponse(
        content={"items": items, "total_price": total, "cart_id": cart.id},
        status_code=status.HTTP_200_OK,
    )


@router.delete("/vaciar")
def clear_cart(
    request: Request,
    token: str = Depends(oauth2_scheme),
):
    user = get_current_user(request, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
    cart = request.app.db.query(Cart).filter_by(user_id=user.id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
        )
    request.app.db.query(CartItemModel).filter_by(cart_id=cart.id).delete()
    request.app.db.delete(cart)
    request.app.db.commit()
    return JSONResponse(
        content={"message": "Carrito vaciado correctamente"},
        status_code=status.HTTP_200_OK,
    )
