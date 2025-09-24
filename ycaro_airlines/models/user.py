from enum import Enum
from typing import ClassVar, Unpack

import pydantic
from ycaro_airlines.models.base_model import BaseModel
from ycaro_airlines.models.model_database import ModelRepository


class Roles(Enum):
    CustomerService = "Worker"
    Customer = "Customer"


class User(BaseModel):
    username: str
    # email: str
    role: Roles | None = None
    repostitory: ClassVar[ModelRepository] = ModelRepository["User"]()

    def __init_subclass__(cls, **kwargs: Unpack[pydantic.ConfigDict]):
        cls.repository = cls.repository

    def __init__(self, username: str, *args, **kwargs) -> None:
        super().__init__(username=username, *args, **kwargs)

    @classmethod
    def get_by_username(cls, customer_username: str):
        for v in cls.repository.list():
            if v is None:
                continue
            if v.username == customer_username:
                return v
        return None
