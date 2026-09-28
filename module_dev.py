import sys
import os
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
import numpy as np
import pandas as pd
from pyminc.volumes.factory import volumeFromFile


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


# Base directories for data and knowledge
def _extract_voxel_values(img, coords):
    """
    Extract voxel values from a MINC image at specified coordinates.

    """
    img_vol = volumeFromFile(img)
    img_vals = np.zeros(coords.shape[0])
    for i, row in coords.iterrows():
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


if __name__ == "__main__":

    # Define base directories for data and knowledge
    data_dir = "data"
    data_dir = os.path.join(data_dir, "imaging", "anatomical", "")

    knowledge_dir = "knowledge"
    knowledge_dir = os.path.join(knowledge_dir, "AllenHumanBrainAtlas", "")

    # Input directory for participant images
    img_dir = os.path.join(data_dir, "effect-sizes-relative", "")

    # AHBA microarray coordinates files
    file_coordinates = "AHBA_microarray_coordinates_mni_icbm152_sym_09c.csv"
    file_coordinates = os.path.join(knowledge_dir, file_coordinates)

    file_coordinates_defs = "AHBA_microarray_coordinates_mni_icbm152_sym_09c_defs.csv"
    file_coordinates_defs = os.path.join(knowledge_dir, file_coordinates_defs)

    df_coordinates = pd.merge(pd.read_csv(file_coordinates), pd.read_csv(file_coordinates_defs), on = "label")



    img_files = [os.path.join(img_dir, f) for f in os.listdir(img_dir) if f.endswith(".mnc")]
    
    # Set n_jobs=4 (or None) to run images in parallel.
    img_vals = np.array(extract_voxel_values(img_files, df_coordinates, n_jobs=1))
    
    df_imgs = pd.DataFrame(
        img_vals,
        index = pd.Index(img_files, name = "path"),
        columns = df_coordinates["sample_id"],
    )

    file_expression = "AHBA_microarray_expression.csv"
    file_expression = os.path.join(knowledge_dir, file_expression)
    df_expression = pd.read_csv(file_expression, index_col="Gene")

    # TODO: Filter for gene set


    def correlate(x, y):
        x_normed = normalize_rows(x)
        y_normed = normalize_rows(y)
        correlations = x_normed @ y_normed.T
        return correlations

    batch_size = 50
    correlations = np.full((len(df_expression), len(df_imgs)), 0.0, dtype=np.float64)
    for start in range(0, 200, batch_size):
        stop = min(start + batch_size, len(df_imgs))

        df_img_batch = df_imgs.iloc[start:stop].to_numpy()

        correlations_batch = correlate(x = df_expression.to_numpy(), y = df_img_batch.to_numpy())

        # Output rows are genes; output columns are images.
        correlations[:, start:stop] = correlations_batch