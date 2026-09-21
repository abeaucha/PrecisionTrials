#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="precision-trials-env"

if ! command -v conda >/dev/null 2>&1; then
    echo "Error: conda is not available. Install Miniconda or Anaconda and make conda available in your shell." >&2
    exit 1
fi

if conda list --name "$ENV_NAME" >/dev/null 2>&1; then
    echo "Ensuring Python is installed in existing environment: $ENV_NAME"
    conda install --yes --name "$ENV_NAME" python=3.14.7
else
    echo "Creating environment with Python: $ENV_NAME"
    conda create --yes --name "$ENV_NAME" python=3.14.7
fi

conda install --yes -c conda-forge --name "$ENV_NAME" --file python_packages.txt

printf '\nSetup complete. Activate the environment with:\n  conda activate %s\n' "$ENV_NAME"
