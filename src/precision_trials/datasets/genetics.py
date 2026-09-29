

class GeneticsDataset:

    def __init__(self):
        self._modalities = {}

    def __repr__(self):
        if not self._modalities:
            return "GeneticsDataset()"
        out = f"GeneticsDataset({list(self._modalities.keys())})"
        return out

    def __len__(self):
        return len(self._modalities)


class GeneticsModality:
    pass