from pathlib import Path

class ImagingDataset:

    def __init__(self):
        self._modalities = {}

    def __repr__(self):
        if not self._modalities:
            return "ImagingDataset(empty)"

        # out = f"ImagingDataset(\n{list(self._modalities.values())}\n)"
        # out = f"ImagingDataset(\n{"\n".join(str(x) for x in self._modalities.values())}\n)"
        out = f"ImagingDataset({list(self._modalities.keys())})"
        return out

    def add(self, modality):
        self._modalities[modality.key] = modality

    @property
    def modalities(self):
        return self._modalities

    def get(self, key):
        return self._modalities[key]


class T1wImages:

    def __init__(self, data_dir = "data/imaging/anatomical"):
        self.data_dir = Path(data_dir)
        self.image_dir = self.data_dir / "T1w"

    def __repr__(self):
        out = f"{self.__class__.__name__}"
        return out
        
    @property
    def key(self):
        return f"{self.__class__.__name__}"
    
    def load_images(self):
        pass


class JacobianImages:

    _VALID_JACOBIAN_TYPES = {"relative", "absolute"}
    
    def __init__(self, data_dir = "data/imaging/anatomical", jacobian_type = "relative"):

        if jacobian_type not in self._VALID_JACOBIAN_TYPES:
            raise ValueError(
                f"Invalid jacobian_type '{jacobian_type}'. "
                f"Must be one of {sorted(self._VALID_JACOBIAN_TYPES)}."
            )
        
        self.jacobian_type = jacobian_type
        self.data_dir = Path(data_dir)
        self.template_file = self.data_dir / "reference-files/model_3.0mm.mnc"
        self.mask_file = self.data_dir / "reference-files/mask_3.0mm.mnc"
        self.image_dir = self.data_dir / f"jacobians-{self.jacobian_type}"

    def __repr__(self):
        out = f"{self.__class__.__name__}(jacobian_type = {self.jacobian_type})"
        return out
        
    @property
    def key(self):
        return f"{self.__class__.__name__}:{self.jacobian_type}"
    
    def load_images(self):
        pass



class EffectSizeImages:

    _VALID_JACOBIAN_TYPES = {"relative", "absolute"}
    
    def __init__(self, data_dir = "data/imaging/anatomical", jacobian_type = "relative"):

        if jacobian_type not in self._VALID_JACOBIAN_TYPES:
            raise ValueError(
                f"Invalid jacobian_type '{jacobian_type}'. "
                f"Must be one of {sorted(self._VALID_JACOBIAN_TYPES)}."
            )
        
        self.jacobian_type = jacobian_type
        self.data_dir = Path(data_dir)
        self.template_file = self.data_dir / "reference-files/model_3.0mm.mnc"
        self.mask_file = self.data_dir / "reference-files/mask_3.0mm.mnc"
        self.image_dir = self.data_dir / f"effect-sizes-{self.jacobian_type}"

    def __repr__(self):
        out = f"{self.__class__.__name__}(jacobian_type = {self.jacobian_type})"
        return out
        

    @property
    def key(self):
        return f"{self.__class__.__name__}:{self.jacobian_type}"

    # Allows on the fly computation if jacobian_type is reassigned in an instance
    # @property
    # def image_dir(self):
    #     return self.data_dir / f"effect-sizes-{self.jacobian_type}"
    
    def load_images(self):
        pass

    



