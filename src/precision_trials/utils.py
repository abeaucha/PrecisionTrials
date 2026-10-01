import os
import re
import subprocess
from numbers import Real

import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from pyminc.volumes.factory import volumeFromFile


def run_r_script(script, *, rscript_executable="Rscript", **kwargs):
    """Run an R script with optparse-style options and capture its output.

    ``script`` is a path (relative to the current working directory or absolute).
    Rscript is found on PATH; activate the desired conda environment first, or
    provide its executable path via ``rscript_executable``.

    Underscores in option names become hyphens. Strings, numbers, and paths
    become ``--name=value`` arguments. True adds a standalone flag (for
    optparse's ``action="store_true"``); False and None omit the option. For
    options with ``type="logical"``, pass the strings "TRUE" or "FALSE".
    Collections are rejected: serialize them in the format your R script uses.

    Returns a subprocess.CompletedProcess with text stdout and stderr. Raises
    subprocess.CalledProcessError on a nonzero exit status; the exception also
    contains stdout and stderr. Arguments are passed directly without a shell.

    Example::

        result = run_r_script("analysis.R", batch_size=100, verbose=True)
        print(result.stdout)
        result = run_r_script("analysis.R", **{"batch_size": 100})
    """
    command = [os.fspath(rscript_executable), os.fspath(script)]
    for name, value in kwargs.items():
        option = name.replace("_", "-")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", option):
            raise ValueError(f"Invalid R option name: {name!r}")
        if value is None or value is False:
            continue
        if value is True:
            command.append(f"--{option}")
        elif isinstance(value, (str, Real, os.PathLike)):
            value = os.fsdecode(value) if isinstance(value, os.PathLike) else str(value)
            command.append(f"--{option}={value}")
        else:
            raise TypeError(f"Unsupported value for {name!r}: {type(value).__name__}")

    return subprocess.run(command, check=True, capture_output=True, text=True)


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


def correlate_matrices(x, y, batch_size = None):

    if batch_size is None:
        batch_size = len(y)

    x_normed = normalize_rows(x)

    correlations = np.full((len(x), len(y)), 0.0, dtype=np.float64)
    for start in range(0, len(y), batch_size):
        stop = min(start + batch_size, len(y))
        y_batch = y[start:stop,:]
        y_batch_normed = normalize_rows(y_batch)
        correlations_batch = x_normed @ y_batch_normed.T
        correlations[:, start:stop] = correlations_batch

    return correlations

