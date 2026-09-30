
from abc import ABC, abstractmethod
from pathlib import Path

class GeneticsModality(ABC):
    
    def __init__(self, data_dir = "data/genetics"):
        self.data_dir = Path(data_dir)

    def __repr__(self):
        return f"{self.__class__.__name__}"
        
    @property
    def key(self):
        return f"{self.__class__.__name__}"

    @abstractmethod
    def __len__(self):
        pass



class GeneticsTest(GeneticsModality):

    def __init__(self, data_dir = "data/genetics"):
        super().__init__(data_dir)

    def __len__(self):
        pass