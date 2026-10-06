import os
import re
import shutil
import subprocess
import sys
from numbers import Real
from pathlib import Path

import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from pyminc.volumes.factory import volumeFromFile


class RScriptError(subprocess.CalledProcessError):
    """A subprocess failure that displays captured R diagnostics."""

    def __str__(self):
        return (
            f"{super().__str__()}\n"
            f"Working directory: {self.cwd}\n"
            f"Rscript executable: {self.executable}\n"
            f"R stderr:\n{self.stderr or '(empty)'}\n"
            f"R stdout:\n{self.stdout or '(empty)'}"
        )


def run_r_script(script, *, rscript_executable=None, **kwargs):
    """Run an R script with optparse-style options and capture its output.

    ``script`` is a path (relative to the current working directory or absolute).
    Prefer Rscript in Python's environment (sys.prefix/bin), falling back to
    PATH. Provide ``rscript_executable`` to override this selection explicitly.

    Underscores in option names become hyphens. Strings, numbers, and paths
    become ``--name=value`` arguments. True adds a standalone flag (for
    optparse's ``action="store_true"``); False and None omit the option. For
    options with ``type="logical"``, pass the strings "TRUE" or "FALSE".
    Collections are rejected: serialize them in the format your R script uses.

    Returns a subprocess.CompletedProcess with text stdout and stderr. Raises
    RScriptError (a subprocess.CalledProcessError) on a nonzero exit status;
    its message includes stdout, stderr, the executable, and working directory.
    Arguments are passed directly without a shell.

    Example::

        result = run_r_script("analysis.R", batch_size=100, verbose=True)
        print(result.stdout)
        result = run_r_script("analysis.R", **{"batch_size": 100})
    """
    # Prefer R installed alongside Python so debugger PATH differences do not
    # accidentally select a system R with a different set of packages.
    if rscript_executable is None:
        environment_rscript = Path(sys.prefix) / "bin" / "Rscript"
        rscript_executable = (
            environment_rscript
            if environment_rscript.is_file() and os.access(environment_rscript, os.X_OK)
            else "Rscript"
        )
    
    # Resolve executable names through PATH for informative error messages.
    # Keep unresolved names so subprocess raises its usual FileNotFoundError.
    executable = os.fsdecode(rscript_executable)
    executable = shutil.which(executable) or executable
    
    # Pass separate arguments without a shell; paths and values need no quoting.
    command = [executable, os.fspath(script)]
    for name, value in kwargs.items():
    
        # Translate Python keyword names to the R script's option convention.
        option = name.replace("_", "-")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", option):
            raise ValueError(f"Invalid R option name: {name!r}")
    
        # Boolean switches are present or absent, rather than --option=True.
        if value is None or value is False:
            continue
        if value is True:
            command.append(f"--{option}")
        elif isinstance(value, (str, Real, os.PathLike)):
            # The equals sign keeps each option and its scalar value together.
            value = os.fsdecode(value) if isinstance(value, os.PathLike) else str(value)
            command.append(f"--{option}={value}")
        else:
            # Require callers to choose how collections or other objects serialize.
            raise TypeError(f"Unsupported value for {name!r}: {type(value).__name__}")

    # Capture both streams as text and handle failures ourselves so the raised
    # exception displays R's diagnostics instead of only the exit status.
    cwd = os.getcwd()
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode:
        error = RScriptError(
            result.returncode, result.args, output=result.stdout, stderr=result.stderr
        )
        # Record execution context to help diagnose relative paths and R selection.
        error.cwd = cwd
        error.executable = executable
        raise error
    
    return result


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
        res = [_extract_voxel_values(img, coords) for img in imgs]
        return np.array(res, dtype=np.float64)
        # return [_extract_voxel_values(img, coords) for img in imgs]
    with ProcessPoolExecutor(max_workers = n_jobs) as executor:
        res = list(executor.map(_extract_voxel_values, imgs, repeat(coords)))
        return np.array(res, dtype = np.float64)


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
