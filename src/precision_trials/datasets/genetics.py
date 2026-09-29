

class GeneticsDataset:

    def __init__(self):
        self._modalities = {}

    def __repr__(self):
        if not self._modalities:
            return "GeneticsDataset(empty)"
        out = f"GeneticsDataset({list(self._modalities.keys())})"
        return out