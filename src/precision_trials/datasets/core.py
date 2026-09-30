
from precision_trials.datasets.imaging import ImagingModality
from precision_trials.datasets.behaviour import BehaviourModality
from precision_trials.datasets.genetics import GeneticsModality


class ModalityDataset:
    """Store modality objects of a common type, indexed by their keys.

    Use a concrete subclass such as :class:`ImagingDataset`,
    :class:`BehaviourDataset`, or :class:`GeneticsDataset`. Subclasses must
    set ``modality_type`` to the accepted modality base class before adding
    objects; the default value of ``None`` cannot be used for type checking.

    Parameters
    ----------
    *modalities : instances of modality_type
        Initial modalities. Each object's ``key`` must be hashable. If
        multiple objects share a key, the last object replaces earlier ones.
        Omit this argument to create an empty dataset.

    Attributes
    ----------
    modality_type : type
        Class attribute defining the accepted type. Instances of its
        subclasses are also accepted.
    modalities : dict
        Mapping from modality keys to the original objects, in insertion
        order. Objects are stored by reference without copying or loading
        their data. Keys are captured when objects are added; later changes
        to an object's key do not update this mapping automatically.

    Notes
    -----
    ``len(dataset)`` counts stored modalities, not participants or files.
    ``repr(dataset)`` shows the dataset class name and its stored keys.

    Examples
    --------
    >>> from precision_trials.datasets.imaging import T1wImages, JacobianImages
    >>> dataset = ImagingDataset(T1wImages())
    >>> dataset.add(JacobianImages(jacobian_type="relative"))
    >>> len(dataset)
    2
    >>> dataset.get("JacobianImages:relative").jacobian_type
    'relative'
    >>> dataset
    ImagingDataset(['T1wImages', 'JacobianImages:relative'])
    """

    modality_type = None

    def __init__(self, *modalities):
        """Initialize the modality mapping and populate it using :meth:`add`."""
        self.modalities = {}
        self.add(*modalities)

    def __repr__(self):
        """Return the class name and stored keys, or just the name if empty."""
        if not self.modalities:
            return f"{self.__class__.__name__}()"
        out = f"{self.__class__.__name__}({list(self.modalities.keys())})"
        return out

    def __len__(self):
        """Return the number of distinct modality keys in the dataset."""
        return len(self.modalities)

    def add(self, *modalities):
        """Add modalities, replacing any existing objects with the same keys.

        Parameters
        ----------
        *modalities : instances of modality_type
            Objects to store under their ``key`` values. Passing no objects
            leaves the dataset unchanged.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If an object is not an instance of ``modality_type``, or its key
            is not hashable.

        Notes
        -----
        Objects are validated and inserted one at a time. If an insertion
        fails, earlier insertions from the same call remain in the dataset.
        Replacing an existing key preserves its position in the mapping.
        """

        for modality in modalities:
            if not isinstance(modality, self.modality_type):
                raise TypeError(
                    f"Expected {self.modality_type.__name__}, "
                    f"got {type(modality).__name__}."
            )

            self.modalities[modality.key] = modality

    def get(self, key):
        """Return the stored modality for a key.

        Parameters
        ----------
        key : hashable
            Key used when the modality was added (normally a string).

        Returns
        -------
        instance of modality_type
            The original stored object, not a copy.

        Raises
        ------
        KeyError
            If the key is absent. This method does not supply a default value.
        TypeError
            If the key is not hashable.
        """
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
