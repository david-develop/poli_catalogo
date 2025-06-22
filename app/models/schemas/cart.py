from pydantic import BaseModel


class CartItem(BaseModel):
    article_id: str
    quantity: int
