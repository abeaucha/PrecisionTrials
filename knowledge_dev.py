
import precision_trials.knowledge as kl
from precision_trials.datasets.imaging import EffectSizeImages

AHBA = kl.AllenHumanBrainAtlas()

KR = kl.KnowledgeResources()

# KR.add(kl.AllenHumanBrainAtlas)
# KR.add(EffectSizeImages())


metadata = AHBA.load_metadata()
coordinates = AHBA.load_coordinates()

annotations = AHBA.load_annotations()

metadata
coordinates
annotations

print()