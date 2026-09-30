import numpy as np
import pandas as pd
from precision_trials import knowledge, utils



class EvidenceModule:

    def __init__(self, resources = None):
        self.resources = resources



class AHBADecodingModule(EvidenceModule):

    def __init__(self, resources = None):
        if resources is None:
            resources = knowledge.KnowledgeResources()
            resources.add("AllenHumanBrainAtlas", knowledge.AllenHumanBrainAtlas())
            resources.add("ReactomePathwayDatabase", knowledge.ReactomePathwayDatabase())

        super().__init__(resources)

    
    def run(self, data, batch_size = 50):

        # Ensure data contains only 1 imaging modality
        if len(data.imaging) != 1:
            raise ValueError(
                "AHBADecodingModule requires exactly one imaging modality."
            )

        # Extract imaging modality
        imgs = list(data.imaging.modalities.values())[0]

        # Fetch image files
        img_files = imgs.image_files

        # Import AHBA microarray coordinates
        coords = pd.read_csv(self.resources.AllenHumanBrainAtlas.coordinates_file)

        # Extract voxel values at coordinates
        voxel_vals = utils.extract_voxel_values(img_files, coords)

        # Convert voxel values to df
        df_voxels = pd.DataFrame(voxel_vals, index = pd.Index(img_files, name = "path"), columns = coords["sample_id"])

        # Import microarray gene expression data
        df_expression = pd.read_csv(self.resources.AllenHumanBrainAtlas.expression_file, index_col = "Gene")

        # Compute image-gene correlation matrix
        correlations = np.full((len(df_expression), len(df_voxels)), 0.0, dtype=np.float64)
        for start in range(0, len(df_voxels), batch_size):
            stop = min(start + batch_size, len(df_voxels))
            df_voxels_batch = df_voxels.iloc[start:stop]
            correlations_batch = utils.correlate_matrices(x = df_expression.to_numpy(), 
                                                          y = df_voxels_batch.to_numpy())

            # Output rows are genes; output columns are images.
            correlations[:, start:stop] = correlations_batch

        self.correlations = correlations

        return
