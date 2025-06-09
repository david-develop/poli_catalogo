import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql.sqltypes import Float
from starlette.requests import Request

from app.db.database import Base
from app.models.schemas.products import CreateArticleForm


class AppBaseModel:
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    def __init__(self, *args, **kwargs):
        """
        instantiation of new BaseModel Class
        """
        if kwargs:
            self.__set_attributes(kwargs)
        else:
            self.id = str(uuid4())

    def __set_attributes(self, attr_dict):
        """
        private: converts attr_dict values to python class attributes
        """
        if "id" not in attr_dict:
            attr_dict["id"] = str(uuid4())
        for attr, val in attr_dict.items():
            setattr(self, attr, val)

    def __str__(self):
        """
        returns string type representation of object instance
        """
        class_name = type(self).__name__
        return "[{}] ({}) {}".format(class_name, self.id, self.__dict__)

    @staticmethod
    def __is_serializable(obj_v):
        """
        private: checks if object is serializable
        """
        try:
            obj_to_str = json.dumps(obj_v)
            return obj_to_str is not None and isinstance(obj_to_str, str)
        except:
            return False

    def to_json(self):
        """
        returns json representation of self
        """
        obj_class = self.__class__.__name__
        bm_dict = {
            k: v if self.__is_serializable(v) else str(v)
            for k, v in self.__dict__.items()
        }
        bm_dict.pop("_sa_instance_state", None)
        bm_dict.update({"__class__": obj_class})
        return bm_dict


class User(AppBaseModel, Base):
    __tablename__ = "users"
    full_name = Column(String)
    username = Column(String, unique=True, index=True)  # same as email
    hashed_password = Column(String)
    role = Column(String, nullable=False)

    __mapper_args__ = {"polymorphic_on": role, "polymorphic_identity": "user"}


class Admin(User):
    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

    @staticmethod
    def create_article(request: Request, data: CreateArticleForm):
        new_article = Article(
            name=data.name,
            category=data.category,
            description=data.description,
            price=data.price,
            stock=data.stock,
        )
        request.app.db.add(new_article)
        request.app.db.commit()
        return new_article.to_json()

    @staticmethod
    def get_all_shoppers(request: Request):
        shoppers = request.app.db.query(Shopper).all()
        shoppers = [shopper.to_json() for shopper in shoppers] if shoppers else []
        return shoppers


class Shopper(User):
    __mapper_args__ = {
        "polymorphic_identity": "shopper",
    }


class Article(AppBaseModel, Base):
    __tablename__ = "article"
    name = Column(String, index=True)
    category = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    stock = Column(Integer)
