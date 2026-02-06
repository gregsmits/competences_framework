"""
Class defining a skill extracted from a ROME file.
Serve as a reference for other skill definitions.
"""

class ROMESkill:
    """Base skill class defined from a ROME file France Travail
    """

    def __init__(self, description: str, type : str, category: str = None):
        assert (type in ["Savoir", "Savoir-faire", "Savoir-être"]), "Type must be either 'Savoir-faire' or 'Savoir-être'"
        self.description = description
        self.type = type
        self.category = category


    def use_skill(self):
        return f"Using skill: {self.name} with power {self.power}!"


