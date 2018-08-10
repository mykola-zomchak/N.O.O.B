from abc import ABC, abstractmethod


class Bot(ABC):

    @abstractmethod
    def get_action(self, **kwargs): pass
