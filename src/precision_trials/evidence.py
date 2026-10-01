import numpy as np
import pandas as pd
from precision_trials import knowledge, utils
from precision_trials.datasets.core import ParticipantDataset



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

    
    def run(self, data, gene_set = None, batch_size = 50, n_files = None, n_jobs = 1):

        """

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

        self.image_files = img_files

        # Import AHBA microarray coordinates
        coords = self.resources.get("AllenHumanBrainAtlas").load_coordinates()

        # Extract voxel values at coordinates
        voxel_vals = utils.extract_voxel_values(img_files, coords, n_jobs = n_jobs)

        # Convert voxel values to df
        df_voxels = pd.DataFrame(voxel_vals, index = pd.Index(img_files, name = "path"), columns = coords.index)

        # Import microarray gene expression data
        df_expression = self.resources.get("AllenHumanBrainAtlas").load_expression()

        self.genes = df_expression.index.to_numpy()

        # Compute image-gene correlation matrix
        correlations = utils.correlate_matrices(x = df_expression.to_numpy(), 
                                                y = df_voxels.to_numpy(),
                                                batch_size = batch_size)

        self.correlations = correlations

        # if gene_set is None:
        #     order = np.argsort(correlations, axis = 0)[::-1]
        #     correlations_ordered = np.take_along_axis(correlations, order, axis=0)
        #     genes = df_expression.index.to_numpy()
        #     genes_ranked = genes[order]

        return
