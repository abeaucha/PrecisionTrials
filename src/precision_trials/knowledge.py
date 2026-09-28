from pathlib import Path

class KnowledgeCollection:

    def __init__(self):
        pass

    def add(self, name, resource):
        setattr(self, name, resource)
    

class AllenHumanBrainAtlas:

    name = "AllenHumanBrainAtlas"

    def __init__(self, knowledge_dir = "knowledge/AllenHumanBrainAtlas/"):
        self.knowledge_dir = Path(knowledge_dir)
        self.expression_file = self.knowledge_dir / "AHBA_microarray_expression.csv"
        self.metadata_file = self.knowledge_dir / "AHBA_microarray_metadata.csv"
        self.coordinates_file = self.knowledge_dir / "AHBA_microarray_coordinates_mni_icbm152_sym_09c.csv"
        self.annotations_file = self.knowledge_dir / "AHBA_microarray_sample_annotations.csv"


class ReactomePathwayDatabase:

    name = "ReactomePathwayDatabase"

    def __init__(self, knowledge_dir = "knowledge/"):
        self.knowledge_dir = Path(knowledge_dir)