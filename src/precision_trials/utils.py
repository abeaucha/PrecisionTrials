import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from pyminc.volumes.factory import volumeFromFile


def _extract_voxel_values(img, coords):
    """
    Extract voxel values from a MINC image at specified coordinates.

    """
    img_vol = volumeFromFile(str(img))
    img_vals = np.zeros(coords.shape[0])
    # for i, row in coords.iterrows():
    for i, (idx, row) in enumerate(coords.iterrows()):
        coords_world = np.array([row['x'], row['y'], row['z']])
        coords_voxel = img_vol.convertWorldToVoxel(coords_world)
        coords_voxel = np.round(coords_voxel)
        x = int(coords_voxel[0]) - 1
        y = int(coords_voxel[1]) - 1
        z = int(coords_voxel[2]) - 1
        img_vals[i] = img_vol.data[x, y, z]
    return img_vals


def extract_voxel_values(imgs, coords, n_jobs = 1):
    """Return one voxel-value array per image, preserving input file order.

    n_jobs=1 runs sequentially; a positive integer sets the process count;
    None lets Python choose the process count. Call parallel execution from
    a script under an ``if __name__ == "__main__":`` guard.
    """
    if n_jobs is not None and (not isinstance(n_jobs, int) or n_jobs < 1):
        raise ValueError("n_jobs must be a positive integer or None")
    if n_jobs == 1:
        return [_extract_voxel_values(img, coords) for img in imgs]
    with ProcessPoolExecutor(max_workers = n_jobs) as executor:
        return list(executor.map(_extract_voxel_values, imgs, repeat(coords)))


def normalize_rows(values):
    """
    Center rows and scale them to unit Euclidean norm for Pearson correlation.
    """
    normalized = np.array(values, dtype=np.float64, copy=True)
    if normalized.ndim != 2 or normalized.shape[1] < 2:
        raise ValueError("values must be a 2D array with at least two columns")
    if not np.isfinite(normalized).all():
        raise ValueError("values must contain only finite values (no NaN or infinity)")

    constant = np.all(normalized == normalized[:, :1], axis=1)
    normalized -= normalized.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(normalized, axis=1, keepdims=True)
    norms[constant | (norms[:, 0] == 0)] = np.nan
    normalized /= norms
    return normalized


def correlate_matrices(x, y):
    x_normed = normalize_rows(x)
    y_normed = normalize_rows(y)
    correlations = x_normed @ y_normed.T
    return correlations