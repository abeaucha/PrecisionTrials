
from abc import ABC, abstractmethod
from pathlib import Path

class BehaviourModality(ABC):

    def __init__(self, data_dir = "data/behaviour"):
        self.data_dir = Path(data_dir)

    def __repr__(self):
        return f"{self.__class__.__name__}"
        
    @property
    def key(self):
        return f"{self.__class__.__name__}"

    @abstractmethod
    def __len__(self):
        pass


class BehaviourTest(BehaviourModality):

    def __init__(self, data_dir = "data/behaviour"):
        super().__init__(data_dir)

    def __len__(self):
        pass