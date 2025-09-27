from typing import Self, Unpack
import pydantic

from ycaro_airlines.models.model_database import ModelRepository


class BaseModel(pydantic.BaseModel):
    id: int

    def __init_subclass__(cls, **kwargs: Unpack[pydantic.ConfigDict]):
        cls.repository = ModelRepository[Self]()
        return super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        #inicializa com um ID temporário
        super().__init__(id=-1, *args, **kwargs)
        #salva no repository e atualiza o ID
        self.id = self.repository.save(self)

    @classmethod
    def get(cls, id: int) -> Self | None:
        return cls.repository.get(id)

    @classmethod
    def list(cls) -> list[Self]:
        return cls.repository.list()
