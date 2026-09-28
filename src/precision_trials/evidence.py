from precision_trials import knowledge

class EvidenceModule:

    def __init__(self, resources = None):
        self.resources = resources


class AHBADecodingModule(EvidenceModule):

    def __init__(self, resources = None):
        if resources is None:
            resources = knowledge.KnowledgeCollection()
            resources.add("AllenHumanBrainAtlas", knowledge.AllenHumanBrainAtlas())
            resources.add("ReactomePathwayDatabase", knowledge.ReactomePathwayDatabase())

        super().__init__(resources)

