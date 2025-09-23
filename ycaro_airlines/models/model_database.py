import abc
from itertools import count
from typing import Generic, TypeVar
import pydantic


T = TypeVar("T", bound=pydantic.BaseModel)


class ModelRepository(abc.ABC, Generic[T]):
    def __init__(self) -> None:
        self.id_counter = count()
        self.data: dict[int, T] = {}
        return super().__init_subclass__()

    def get(self, id: int) -> T | None:
        return self.data.get(id)

    def list(self):
        return list(self.data.values())

    def save(self, item: T) -> int:
        item_id = next(self.id_counter)
        self.data[item_id] = item
        return item_id

    def remove(self, id: int) -> T | None:
        return self.data.pop(id)

    def update(self, id: int, **kwargs) -> T | None:
        if (item := self.data.get(id)) is None:
            return None

        model_attribute_dump = item.model_dump()
        model_attribute_dump.update(**kwargs)

        try:
            updated_model: T = T.model_validate(model_attribute_dump)  # pyright: ignore[reportAttributeAccessIssue]

        except pydantic.ValidationError as e:
            print(e)
            return None

        self.data[id] = updated_model

        return updated_model
