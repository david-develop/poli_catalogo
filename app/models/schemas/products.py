from typing import Optional

from pydantic import BaseModel


class CreateArticleForm(BaseModel):
    name: str
    category: str
    description: str
    price: float
    stock: int


class UpdateArticleForm(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

    def any_field_set(self):
        return any(getattr(self, field) is not None for field in self.model_fields)
