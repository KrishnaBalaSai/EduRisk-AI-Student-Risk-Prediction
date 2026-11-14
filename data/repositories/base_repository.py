"""
Base Repository Interface
"""

from typing import Type, TypeVar, Generic, List, Optional, Any
from sqlalchemy.orm import Session
from data.database import get_session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model_class: Type[T], session: Optional[Session] = None):
        self.model_class = model_class
        self._session = session

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = get_session()
        return self._session

    def get_by_id(self, entity_id: str) -> Optional[T]:
        return self.session.query(self.model_class).filter(self.model_class.id == entity_id).first()

    def get_all(self, limit: int = 1000, offset: int = 0) -> List[T]:
        return self.session.query(self.model_class).offset(offset).limit(limit).all()

    def count(self) -> int:
        return self.session.query(self.model_class).count()

    def create(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def bulk_create(self, entities: List[T], batch_size: int = 500) -> int:
        for i in range(0, len(entities), batch_size):
            batch = entities[i : i + batch_size]
            self.session.bulk_save_objects(batch)
            self.session.commit()
        return len(entities)

    def update(self, entity: T) -> T:
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity_id: str) -> bool:
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False

