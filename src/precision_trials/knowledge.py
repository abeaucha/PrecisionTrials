
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

class KnowledgeResources:

    def __init__(self, *resources):
        self.resources = {}
        self.add(*resources)

    def __repr__(self):
        if not self.resources:
            return f"{self.__class__.__name__}()"
        out = f"{self.__class__.__name__}({list(self.resources.keys())})"
        return out

    def add(self, *resources):

        for resource in resources:
            if not isinstance(resource, KnowledgeResource):
                raise TypeError(
                    f"Expected {KnowledgeResource.__name__}, "
                    f"got {type(resource).__name__}."
            )

            self.resources[resource.key] = resource

    def get(self, key):
        return self.resources[key]



class KnowledgeResource(ABC):

    def __init__(self):
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}"
        
    @property
    def key(self):
        return f"{self.__class__.__name__}"



class AllenHumanBrainAtlas(KnowledgeResource):

    def __init__(self, knowledge_dir = "knowledge/AllenHumanBrainAtlas/"):
        self.knowledge_dir = Path(knowledge_dir)
        self.expression_file = self.knowledge_dir / "AHBA_microarray_expression.csv"
        self.metadata_file = self.knowledge_dir / "AHBA_microarray_metadata.csv"
        self.coordinates_file = self.knowledge_dir / "AHBA_microarray_coordinates_mni_icbm152_sym_09c.csv"
        self.annotations_file = self.knowledge_dir / "AHBA_microarray_sample_annotations.csv"

    def load_expression(self, index_col = "Gene"):
        """Load AHBA microarray expression data"""
        return pd.read_csv(self.expression_file, index_col = index_col)

    def load_metadata(self, index_col = "sample_id"):
        """Load AHBA microarray metadata"""
        return pd.read_csv(self.metadata_file, index_col = index_col)

    def load_coordinates(self, index_col = "sample_id"):
        """Load AHBA microarray sample coordinates"""
        return pd.read_csv(self.coordinates_file, index_col = index_col)

    def load_annotations(self, index_col = "sample_id"):
        """Load AHBA microarray sample quality annotations"""
        return pd.read_csv(self.annotations_file, index_col = index_col)



class ReactomePathwayDatabase(KnowledgeResource):

    def __init__(self, knowledge_dir = "knowledge/ReactomePathwayDatabase"):
        self.knowledge_dir = Path(knowledge_dir)
        self.mappings_file = self.knowledge_dir / "Human_Reactome_June_01_2025_symbol.gmt"
        self.background_file = self.knowledge_dir / "sagittal_gene_table_normalized_filtered.csv"