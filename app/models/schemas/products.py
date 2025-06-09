from pydantic import BaseModel


class CreateArticleForm(BaseModel):
    name: str
    category: str
    description: str
    price: float
    stock: int
