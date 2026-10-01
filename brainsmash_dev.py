

import numpy as np
from scipy.spatial.distance import pdist, squareform

from precision_trials.knowledge import AllenHumanBrainAtlas

AHBA = AllenHumanBrainAtlas()

coordinates = AHBA.load_coordinates()

# Pairwise Euclidean distances, in the same row order as coordinates.
distances = squareform(pdist(coordinates[["x", "y", "z"]].to_numpy(), metric="euclidean"))


random_array = np.random.default_rng().random(3702)

import brainsmash
from brainsmash.mapgen.base import Base


print(brainsmash.__file__)

brainsmash_base = Base(x = random_array, D = distances, n_jobs = 1)

surrogates = brainsmash_base(n = 1)

print(type(surrogates))
print(surrogates.shape)