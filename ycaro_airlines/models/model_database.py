import abc
from itertools import count
from typing import Generic, TypeVar, Dict, Type
import pydantic

"""

Exemplo de singleton genérico para repositórios de modelos.

"""



T = TypeVar("T", bound=pydantic.BaseModel)

class ModelRepository(abc.ABC, Generic[T]):
    _instances: Dict[Type, 'ModelRepository'] = {}
    
    def __new__(cls, model_type: Type[T] = None):
        # Implementa Singleton por tipo de modelo
        key = (cls, model_type) if model_type else cls
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance
        return cls._instances[key]
    
    def __init__(self, model_type: Type[T] = None):
        if not hasattr(self, '_initialized'):
            self.id_counter = count()
            self.data: dict[int, T] = {}
            self.model_type = model_type
            self._initialized = True

    def get(self, id: int) -> T | None:
        return self.data.get(id)

    def list(self):
        return list(self.data.values())

    def save(self, item: T) -> int:
        item_id = next(self.id_counter)
        self.data[item_id] = item
        return item_id

    def remove(self, id: int) -> T | None:
        return self.data.pop(id, None)

    def update(self, id: int, **kwargs) -> T | None:
        if (item := self.data.get(id)) is None:
            return None

        model_attribute_dump = item.model_dump()
        model_attribute_dump.update(**kwargs)

        try:
            updated_model: T = self.model_type.model_validate(model_attribute_dump)
        except pydantic.ValidationError as e:
            print(e)
            return None

        self.data[id] = updated_model
        return updated_model