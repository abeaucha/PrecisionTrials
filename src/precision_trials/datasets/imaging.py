

from abc import ABC, abstractmethod
from pathlib import Path



class ImagingModality(ABC):

    def __init__(self, data_dir = "data/imaging/"):
        self.data_dir = Path(data_dir)

    def __repr__(self):
        return f"{self.__class__.__name__}"
        
    @property
    def key(self):
        return f"{self.__class__.__name__}"

    @abstractmethod
    def __len__(self):
        pass



class T1wImages(ImagingModality):

    def __init__(self, data_dir = "data/imaging/anatomical/"):
        super().__init__(data_dir)
        self.image_dir = self.data_dir / "T1w"

    def __len__(self):
        # Count the number of .mnc files in the image_dir
        if not self.image_dir.exists():
            return 0
        return len(list(self.image_dir.glob("*.mnc")))
        
    @property
    def image_files(self):
        return [f for f in sorted(self.image_dir.iterdir())]
    
    def load_images(self):
        pass


class JacobianImages(ImagingModality):

    _VALID_JACOBIAN_TYPES = {"relative", "absolute"}
    
    def __init__(self, data_dir = "data/imaging/anatomical/", jacobian_type = "relative"):

        if jacobian_type not in self._VALID_JACOBIAN_TYPES:
            raise ValueError(
                f"Invalid jacobian_type '{jacobian_type}'. "
                f"Must be one of {sorted(self._VALID_JACOBIAN_TYPES)}."
            )
        
        super().__init__(data_dir)

        self.jacobian_type = jacobian_type
        self.template_file = self.data_dir / "reference-files/model_3.0mm.mnc"
        self.mask_file = self.data_dir / "reference-files/mask_3.0mm.mnc"
        self.image_dir = self.data_dir / f"jacobians-{self.jacobian_type}"

    def __repr__(self):
        return f"{self.__class__.__name__}(jacobian_type={self.jacobian_type})"

    def __len__(self):
        # Count the number of .mnc files in the image_dir
        if not self.image_dir.exists():
            return 0
        return len(list(self.image_dir.glob("*.mnc")))

    @property
    def key(self):
        return f"{super().key}:{self.jacobian_type}"

    @property
    def image_files(self):
        return [f for f in sorted(self.image_dir.iterdir())]

    def load_images(self):
        pass


class EffectSizeImages(ImagingModality):

    _VALID_JACOBIAN_TYPES = {"relative", "absolute"}

    def __init__(self, data_dir = "data/imaging/anatomical/", jacobian_type = "relative"):

        if jacobian_type not in self._VALID_JACOBIAN_TYPES:
            raise ValueError(
                f"Invalid jacobian_type '{jacobian_type}'. "
                f"Must be one of {sorted(self._VALID_JACOBIAN_TYPES)}."
            )

        super().__init__(data_dir)

        self.jacobian_type = jacobian_type
        self.template_file = self.data_dir / "reference-files/model_3.0mm.mnc"
        self.mask_file = self.data_dir / "reference-files/mask_3.0mm.mnc"
        self.image_dir = self.data_dir / f"effect-sizes-{self.jacobian_type}"

    def __repr__(self):
        return f"{self.__class__.__name__}(jacobian_type={self.jacobian_type})"
    
    def __len__(self):
        # Count the number of .mnc files in the image_dir
        if not self.image_dir.exists():
            return 0
        return len(list(self.image_dir.glob("*.mnc")))
    
    @property
    def key(self):
        return f"{super().key}:{self.jacobian_type}"

    @property
    def image_files(self):
        return [f for f in sorted(self.image_dir.iterdir())]
        
    def load_images(self):
        pass