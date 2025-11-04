from typing import Self, Unpack
import pydantic

from ycaro_airlines.models.model_database import ModelRepository


class BaseModel(pydantic.BaseModel):
    id: int

    def __init_subclass__(cls, **kwargs: Unpack[pydantic.ConfigDict]):
        # Create a repository instance tied to the concrete subclass type so each
        # model class gets its own storage. Avoid using typing Self here because
        # that can resolve to the same typing object across subclasses and lead
        # to shared repositories.
        cls.repository = ModelRepository(model_type=cls)

        # Migration safety: if previous repositories (created before we changed
        # the singleton keying) contain instances of this concrete class, move
        # them into the new repository so data created before the refactor is
        # not lost. This checks all existing ModelRepository instances and
        # migrates any stored items whose type matches `cls`.
        migrated = {}
        max_id = -1
        for key, repo in ModelRepository._instances.items():
            if repo is cls.repository:
                continue
            data = getattr(repo, 'data', {})
            # find items of the target class
            for item_id, item in list(data.items()):
                if isinstance(item, cls):
                    migrated[item_id] = item
                    max_id = max(max_id, item_id)
                    # remove from old repo to avoid duplicates
                    try:
                        del repo.data[item_id]
                    except Exception:
                        pass

        if migrated:
            # merge migrated data into the new repository preserving ids
            cls.repository.data.update(migrated)
            # ensure id_counter starts after the highest existing id
            try:
                from itertools import count
                cls.repository.id_counter = count(max_id + 1)
            except Exception:
                pass
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
