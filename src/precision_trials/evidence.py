import os
from pathlib import Path

import numpy as np
import pandas as pd
from precision_trials import knowledge, utils
from precision_trials.datasets.core import ParticipantDataset

from scipy.spatial.distance import pdist, squareform
from brainsmash.mapgen.base import Base as BrainSMASHBase

from tempfile import TemporaryDirectory

R_DIR = Path(__file__).parent / "R"


class EvidenceModule:

    def __init__(self, resources = None):
        self.resources = resources



class AHBADecodingModule(EvidenceModule):

    def __init__(self, resources = None):
        if resources is None:
            resources = knowledge.KnowledgeResources()
            resources.add(knowledge.AllenHumanBrainAtlas())
            resources.add(knowledge.ReactomePathwayDatabase())

        super().__init__(resources)

    
    def run(self, data, workdir = None, batch_size = 50, n_files = None, n_jobs = 1, gsea_null = "random"):

        """
        Run AHBA decoding module. 

        Parameters
        ----------
        data : ParticipantDataset
            ParticipantDataset object containing imaging data.
        workdir : str or Path, optional
            Directory to store intermediate files. If None, a temporary directory is used.
        batch_size : int, optional
            Batch size for correlation computation. Default is 50.
        n_files : int, optional
            Number of imaging files to process. If None, all files are processed.
        n_jobs : int, optional
            Number of parallel jobs for voxel extraction. Default is 1.
        gsea_null : str, optional
            Null model for GSEA. Options are "random" or "spatial". Default is "random".

        """

        # Ensure data is ParticipantDataset object
        if not isinstance(data, ParticipantDataset):
            raise TypeError(
                f"Expected {ParticipantDataset.__name__}, "
                f"got {type(data).__name__}."
            )

        # Ensure data contains only 1 imaging modality
        if len(data.imaging) != 1:
            raise ValueError(
                "AHBADecodingModule requires exactly one imaging modality."
            )

        # Extract imaging modality
        imgs = list(data.imaging.modalities.values())[0]

        # Fetch image files
        img_files = imgs.image_files
        if n_files is not None:
            img_files = img_files[:n_files]

        # Import AHBA microarray coordinates
        coords = self.resources.get("AllenHumanBrainAtlas").load_coordinates()

        # Extract voxel values at AHBA microarray coordinates
        voxel_mat = utils.extract_voxel_values(img_files, coords, n_jobs = n_jobs)

        self._decode_images(voxels = voxel_mat, workdir = workdir, batch_size = batch_size, n_jobs = n_jobs)


        if gsea_null == "spatial":

            # Compute distance matrix between AHBA microarray coordinates
            distances = squareform(pdist(coords[["x", "y", "z"]].to_numpy(), metric="euclidean"))

            surrogates = BrainSMASHBase(x = voxel_mat[0,:], D = distances, n_jobs = 1)(n = 1)

            self._decode_images(voxels = surrogates, workdir = workdir, batch_size = batch_size, n_jobs = n_jobs)


        return


    def _decode_images(self, voxels, workdir = None, batch_size = 50, n_jobs = 1):

        """
        
        Parameters
        ----------
        voxels : np.ndarray
            2D array of voxel values (n_images x n_voxels).
        workdir : str or Path, optional
            Directory to store intermediate files. If None, a temporary directory is used.
        batch_size : int, optional
            Batch size for correlation computation. Default is 50.
        n_jobs : int, optional
            Number of parallel jobs for correlation computation. Default is 1.
        """

        # Import microarray gene expression data
        df_expression = self.resources.get("AllenHumanBrainAtlas").load_expression()

        # Extract gene names
        genes = df_expression.index.to_numpy()

        # Compute image-gene correlation matrix
        correlations = utils.correlate_matrices(x = df_expression.to_numpy(), 
                                                y = voxels,
                                                batch_size = batch_size)

        if workdir is None:

            with TemporaryDirectory() as tmpdir:

                enrichment = self._run_gsea(correlations, genes, workdir = Path(tmpdir))

        else:

            if not os.path.exists(workdir):
                os.makedirs(workdir)

            enrichment = self._run_gsea(correlations, genes, workdir = Path(workdir))

        return

        

    # def _compute_gene_correlations(self, voxels, batch_size = 50):

    #     """

    #     """

    #     # Import microarray gene expression data
    #     df_expression = self.resources.get("AllenHumanBrainAtlas").load_expression()

    #     # Extract gene names
    #     genes = df_expression.index.to_numpy()

    #     # Compute image-gene correlation matrix
    #     correlations = utils.correlate_matrices(x = df_expression.to_numpy(), 
    #                                             y = voxels,
    #                                             batch_size = batch_size)

    #     return correlations, genes


    def _run_gsea(self, correlations, genes, workdir = None, min_size = 15, max_size = 500): 

        """
        Run Gene Set Enrichment Analysis (GSEA) using R backend.

        Parameters
        ----------
        correlations : np.ndarray
            2D array of correlation values (n_genes x n_images).
        genes : np.ndarray
            1D array of gene names corresponding to the rows of the correlations matrix.
        workdir : str or Path, optional
            Directory to store intermediate files. If None, a temporary directory is used.
        min_size : int, optional
            Minimum size of gene sets to consider. Default is 15.
        max_size : int, optional
            Maximum size of gene sets to consider. Default is 500.

        Returns
        -------
        gsea_results : dict
            Dictionary containing GSEA results with keys 'ES', 'NES', 'pvals', and 'pathways', each mapping to a pandas DataFrame.
        """

        # Export correlations and genes to CSV files for R script
        correlations_file = workdir / "AHBADecodingModule_correlations.csv"
        pd.DataFrame(correlations, index = pd.Index(genes, name = "gene")).to_csv(correlations_file)

        # images_file = f"{tmpdir}/AHBADecodingModule_images.csv"
        # pd.DataFrame({'file': image_files}).to_csv(images_file, index=False)

        r_kwargs = dict(
            ranks_file = correlations_file,
            mappings_file = self.resources.get("ReactomePathwayDatabase").mappings_file,
            output_dir = workdir,
            min_size = min_size,
            max_size = max_size
        )

        utils.run_r_script(script = R_DIR / "gsea.R", **r_kwargs)

        gsea_results = {
            'ES': pd.read_csv(workdir / "ES.csv"),
            'NES': pd.read_csv(workdir / "NES.csv"),
            'pvals': pd.read_csv(workdir / "pvals.csv"),
            'pathways': pd.read_csv(workdir / "pathways.csv")
        }

        return gsea_results

