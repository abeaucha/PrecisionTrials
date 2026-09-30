
from precision_trials.datasets.imaging import ImagingModality
from precision_trials.datasets.behaviour import BehaviourModality
from precision_trials.datasets.genetics import GeneticsModality


class ModalityDataset:

    modality_type = None

    def __init__(self, *modalities):
        self.modalities = {}
        self.add(*modalities)

    def __repr__(self):
        if not self.modalities:
            return f"{self.__class__.__name__}()"
        out = f"{self.__class__.__name__}({list(self.modalities.keys())})"
        return out

    def __len__(self):
        return len(self.modalities)

    def add(self, *modalities):

        for modality in modalities:
            if not isinstance(modality, self.modality_type):
                raise TypeError(
                    f"Expected {self.modality_type.__name__}, "
                    f"got {type(modality).__name__}."
            )

            self.modalities[modality.key] = modality

    def get(self, key):
        return self.modalities[key]


class ImagingDataset(ModalityDataset):
    modality_type = ImagingModality


class BehaviourDataset(ModalityDataset):
    modality_type = BehaviourModality

class GeneticsDataset(ModalityDataset):
    modality_type = GeneticsModality


class ParticipantDataset:

    def __init__(self, imaging = None, behaviour = None, genetics = None):
        
        if imaging is None:
            self.imaging = ImagingDataset()
        else: 
            if not isinstance(imaging, ImagingDataset):
                raise TypeError(
                    f"Expected ImagingDataset, got {type(imaging).__name__}."
                )
            self.imaging = imaging

        if behaviour is None:
            self.behaviour = BehaviourDataset()
        else:
            if not isinstance(behaviour, BehaviourDataset):
                raise TypeError(
                    f"Expected BehaviourDataset, got {type(behaviour).__name__}."
                )
            self.behaviour = behaviour

        if genetics is None:
            self.genetics = GeneticsDataset()
        else:
            if not isinstance(genetics, GeneticsDataset):
                raise TypeError(
                    f"Expected GeneticsDataset, got {type(genetics).__name__}."
                )
            self.genetics = genetics

    def __repr__(self):
        return f"ParticipantDataset(\n\t{self.imaging}\n\t{self.behaviour}\n\t{self.genetics}\n)"

