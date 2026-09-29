

class BehaviourDataset:

    def __init__(self):
        self._modalities = {}

    def __repr__(self):
        if not self._modalities:
            return "BehaviourDataset()"
        out = f"BehaviourDataset({list(self._modalities.keys())})"
        return out

    def __len__(self):
        return len(self._modalities)


class BehaviourModality:
    pass