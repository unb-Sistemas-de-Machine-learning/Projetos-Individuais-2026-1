from abc import ABC, abstractmethod


class Model(ABC):
    @abstractmethod
    def prompt_diff(self, diff: str) -> str | None:
        pass
