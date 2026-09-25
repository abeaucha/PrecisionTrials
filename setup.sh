#!/usr/bin/env bash
set -euo pipefail

# Path to conda installation
CONDA_PATH=$(conda info --base)

if ! command -v conda >/dev/null 2>&1; then
    echo "Error: conda is not available. Install Miniconda or Anaconda and make conda available in your shell." >&2
    exit 1
fi

# Environment names 
MINC_ENV_NAME="minc-env"
ENV_NAME="precision-trials-env"

# Environment paths
MINC_ENV_PATH=${CONDA_PATH}/envs/${MINC_ENV_NAME}
ENV_PATH=${CONDA_PATH}/envs/${ENV_NAME}

# Create MINC environment and install minc-toolkit-v2
if [ -d "${MINC_ENV_PATH}/conda-meta" ]; then
  echo -e "\nMINC environment ${MINC_ENV_NAME} already exists; skipping creation."
else
  echo -e "\nBuilding MINC environment..."
  conda create -n "$MINC_ENV_NAME" -c minc-forge minc-toolkit-v2 -y
fi

# Resolve and install R, Python, and their Conda packages together
echo -e "\nBuilding project environment..."
conda create -n "$ENV_NAME" -c conda-forge \
  r-base=4.5.3 python=3.14.7 \
  --file R_packages_conda.txt \
  --file python_packages_conda.txt \
  -y

mkdir -p "${ENV_PATH}/etc/conda/activate.d" "${ENV_PATH}/etc/conda/deactivate.d"

# Set $MINC_TOOLKIT upon activation 
cat <<EOF > "${ENV_PATH}"/etc/conda/activate.d/activate-minc-toolkit.sh
if [ -n "\${MINC_TOOLKIT:-}" ]; then
  export MINC_TOOLKIT_PREV="\${MINC_TOOLKIT:-}"
fi
export MINC_TOOLKIT="$MINC_ENV_PATH"
EOF

# Unset $MINC_TOOLKIT upon deactivation
cat <<EOF > "${ENV_PATH}"/etc/conda/deactivate.d/deactivate-minc-toolkit.sh
# restore pre-existing MINC_TOOLKIT 
if [ -n "\${MINC_TOOLKIT_PREV:-}" ]; then
  export MINC_TOOLKIT="\${MINC_TOOLKIT_PREV:-}"
  unset MINC_TOOLKIT_PREV
else
  unset MINC_TOOLKIT
fi
EOF

# Install RMINC from Github
echo -e "\nInstalling RMINC from Github..."
conda run -n "$ENV_NAME" --no-capture-output Rscript -e 'devtools::install_github("Mouse-Imaging-Centre/RMINC", ref = "57ef9122311d255f24c44571f9c68972c1c3cc4f", upgrade = "never")'

# Package installation failures can be reported as warnings; verify the result.
conda run -n "$ENV_NAME" --no-capture-output Rscript -e 'library(RMINC); stopifnot(packageDescription("RMINC")$RemoteSha == "57ef9122311d255f24c44571f9c68972c1c3cc4f"); cat("RMINC", as.character(packageVersion("RMINC")), "installed successfully\n")'

# Install MRIcrotome from Github
echo -e "\nInstalling MRIcrotome from Github..."
conda run -n "$ENV_NAME" --no-capture-output Rscript -e 'devtools::install_github("Mouse-Imaging-Centre/MRIcrotome", upgrade = "never")'
conda run -n "$ENV_NAME" --no-capture-output Rscript -e 'library(MRIcrotome); cat("MRIcrotome", as.character(packageVersion("MRIcrotome")), "installed successfully\n")'

# Install Python utils and pyminc using pip
echo -e "\nInstalling python packages using pip..."
conda run -n "$ENV_NAME" --no-capture-output python -m pip install -r python_packages_pip.txt
conda run -n "$ENV_NAME" --no-capture-output python -c 'import utils; from pyminc.volumes.factory import volumeFromFile; print("utils and pyminc imported successfully")'
