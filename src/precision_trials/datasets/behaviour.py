

class BehaviourDataset:

    def __init__(self):
        self._modalities = {}

    def __repr__(self):
        if not self._modalities:
            return "BehaviourDataset(empty)"
        out = f"BehaviourDataset({list(self._modalities.keys())})"
        return out