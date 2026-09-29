
from precision_trials.datasets.imaging import ImagingDataset
from precision_trials.datasets.behaviour import BehaviourDataset
from precision_trials.datasets.genetics import GeneticsDataset

class ModalitySet:

    def __init__(self):
        self._modalities = {}

    def __repr__(self):
        if not self._modalities:
            return "ModalitySet()"
        out = f"ModalitySet({list(self._modalities.keys())})"
        return out

    def __len__(self):
        return len(self._modalities)


class ParticipantDataset:

    def __init__(self):
        self.imaging = ImagingDataset()
        self.behaviour = BehaviourDataset()
        self.genetics = GeneticsDataset()

    def __repr__(self):
        return f"ParticipantDataset(\n\t{self.imaging}\n\t{self.behaviour}\n\t{self.genetics}\n)"