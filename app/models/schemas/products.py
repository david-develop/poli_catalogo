from typing import List, Optional

from pydantic import BaseModel

from app.models.schemas.const import CATEGORIES


class CreateArticleForm(BaseModel):
    name: str
    category: CATEGORIES
    description: str
    price: float
    stock: int


class UpdateArticleForm(BaseModel):
    name: Optional[str] = None
    category: Optional[CATEGORIES] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

    def any_field_set(self):
        return any(getattr(self, field) is not None for field in self.model_fields)


class AdvancedSearchForm(BaseModel):
    name: Optional[str] = None
    category: Optional[CATEGORIES] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
