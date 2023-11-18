from abc import ABCMeta, abstractmethod
from typing import Generic, List, TypeVar

from nonebot.adapters import Bot, Event

from .models import Session

B = TypeVar("B", bound=Bot)
E = TypeVar("E", bound=Event)


class Extractor(Generic[B, E], metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def get_adapter(cls) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_session(self, bot: B, event: E) -> Session:
        raise NotImplementedError

    @abstractmethod
    def get_subjects(self, bot: B, event: E) -> List[str]:
        raise NotImplementedError
