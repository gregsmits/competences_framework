"""
Base classes to construct the skills base
"""
import json
import networkx as nx
from langchain_core.documents import Document
import tqdm

#add utils to class path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
from indexer import Indexer

class FamilyOfProblems:
    """Class defining a family of problems in skill definitions.
    """

    def __init__(self, label: str, description: str = ""):
        self.label = label
        self.description = description
        self.indexed_problem_id = None
        self.necessary_resources = []
        self.sufficient_resources = []

    def align_pb_family_index(self, indexer : Indexer):
        """Align the problems family of the skill with a given indexer.

        Args:
            indexer (_type_): _description_
        """
        ret_idx = indexer.query(" ; ".join([self.label, self.description]), top_k=1)
        if len(ret_idx) > 0:

            self.indexed_problem_id = ret_idx[0][0].id
            #print(f"\nAligned PB Family:\n\t- {self.label} + {self.description} \n\t- with: {self.indexed_problem_id}")


class Resource:
    """Class defining an internal resource used in skill definitions.
    """

    def __init__(self, description: str, type : str, category: str = None):
        assert (type in ["Savoirs", "Savoir-faire", "Savoir-être", "Unknown"]), "Type must be either 'Savoir-faire' or 'Savoir-être'"
        self.description = description
        self.type = type
        self.category = category
        self.degree = None
        self.indexed_resource_id = None

    def align_resource_index(self, indexer : Indexer):
        """Align the resource with a given indexer.

        Args:
            indexer (_type_): _description_
        """
        ret_idx = indexer.query(self.description, top_k=1) 
        if len(ret_idx) > 0:
            self.indexed_resource_id = ret_idx[0][0].id
#        print(f"\nAligned Resource:\n\t- {self.description} \n\t- with: {indexer.get_document_by_id(self.indexed_resource_id).page_content}")


class Skill:
    """Base skill class defined from a ROME file France Travail
    """

    def __init__(self):
        #generate a unique id for the skill from time in milliseconds
        self.pb_family = None
        self.resources = []
        self.source = ""
        self.title = ""

    
    def load_from_json(self, file_path: str):
        """Load a skill from a json file representing a 
         {
            "resource": "Concevoir des applications informatiques en analysant des besoins d'un commanditaire et en mettant en œuvre les éléments technologiques ou des dispositifs expérimentaux dans des activités de recherche et de développement en mobilisant un large champs de sciences fondamentales et des éléments organisationnels",
            "type": "Savoir-faire",
            "category": "Élaborer un diagnostic d'un système d'information, des réseaux d'entreprise ou d'opérateurs ou d'une organisation sur une problématique spécifique"
        },

        Args:
            file_path (str): _description_
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            self.source = json_data.get("source", "Unknown")
            self.title = json_data.get("label", "unknown")
            self.pb_family = FamilyOfProblems(self.title, " ; ".join(json_data.get("problems_family", [])))
            for r in json_data.get("resources", []):
                if r.get("resource", "") not in [res.description for res in self.resources]:
                    resource = Resource(
                        description=r.get("resource", ""),
                        type=r.get("type", ""),
                        category=r.get("category", None)
                    )
                    self.resources.append(resource)

class SkillsBase:
    """Base class for skill definitions.
    """
    
    def __init__(self, skills : list[Skill] = []):
        self.skills = skills
        self.base = nx.Graph()
        self.aligned = False
        
    def add_skill(self, skill: Skill):
        """Add a skill to the skills base.

        Args:
            skill (Skill): _description_
        """
        self.skills.append(skill)

    def align_with_indexer(self, pb_indexer : Indexer, res_indexer : Indexer):
        """Align the skills base with given indexers.

        Args:
            pb_indexer (Indexer): _description_
            res_indexer (Indexer): _description_
        """
        pbs = dict()
        ress = dict()
        for skill in tqdm.tqdm(self.skills):
            skill.pb_family.align_pb_family_index(pb_indexer)
            if skill.pb_family.indexed_problem_id not in pbs:
                pbs[skill.pb_family.indexed_problem_id] = 1
            else:
                pbs[skill.pb_family.indexed_problem_id] += 1
            for res in tqdm.tqdm(skill.resources):
                res.align_resource_index(res_indexer)
                if res.indexed_resource_id not in ress:
                    ress[res.indexed_resource_id] = 1
                else:   
                    ress[res.indexed_resource_id] += 1
        print("Pb families distribution in skills base:",pbs)
        print("Resources distribution in skills base:",ress)
        self.aligned = True

    def analyze_resources_per_problem(self):
        """The skills base being loaded, necessary and sufficent sets of resources
        per problem can be analyzed.
        Attention: to be called after align_with_indexer()
        """
        if not self.aligned:
            raise Exception("Skills base not aligned with indexers. Please call align_with_indexer() first.")
        
        pbs_res = {}
        for skill in tqdm.tqdm(self.skills):
            if skill.pb_family.indexed_problem_id not in pbs_res:
                pbs_res[skill.pb_family] = []
            pbs_res[skill.pb_family].append([r.indexed_resource_id for r in skill.resources])
        for pb in tqdm.tqdm(pbs_res):
            #necessary resources as the intersection of sets of resources
            nec_res = set()
            suff_res = []
            all_res = set()

            for res_set in tqdm.tqdm(pbs_res[pb]):
                if not nec_res:
                    nec_res = set(res_set)
                else:
                    nec_res = nec_res.intersection(set(res_set))
                suff_res.append(res_set)
                all_res = all_res.union(set(res_set))
            #sufficient resources 
            checked_suff_res = [ s for s in suff_res if [j for j in suff_res if set(j).issubset(set(s)) and set(j) != set(s)] == []]
            pb.necessary_resources = list(nec_res)
            pb.sufficient_resources = checked_suff_res

    def assign_resource_degrees(self) -> dict[str, float]:
        """Compute the degree of a skill in the skills base graph.
        Attention: to be called after align_with_indexer()
        Attention: to be called after analyze_resources_per_problem()
    
        Args:
            skill (Skill): _description_
        Returns:
            int: _description_
        """
        if not self.aligned:
            raise Exception("Skills base not aligned with indexers. Please call align_with_indexer() first.")
        epsilon=0.01
        ret = dict()
        for res in [res for skill in self.skills for res in skill.resources]:
            degree = 0
            nec = 0
            suff = 0
            for skill in self.skills:
                if res.indexed_resource_id in skill.pb_family.necessary_resources:
                    nec += 1
                for res_set in skill.pb_family.sufficient_resources:
                    if res.indexed_resource_id in res_set:
                        suff += 1

            res.degree = nec/len(self.skills) *(1 - epsilon) + suff/len(self.skills) * epsilon
            ret[res.indexed_resource_id] = res.degree
        return ret
    
    def __str__(self):
        """String representation of the skills base.

        Returns:
            str: _description_
        """
        ret = f"Skills Base with {len(self.skills)} skills.\n"
        for skill in self.skills:
            ret += f"- Skill: {skill.title} | Source: {skill.source}\n"
            ret += f"  - Problem Family: {skill.pb_family.label} (Indexed ID: {skill.pb_family.indexed_problem_id})\n"
            ret += f"  - Resources:\n"
            for res in skill.resources:
                ret += f"    * {res.description} | Type: {res.type} | Category: {res.category} | Indexed ID: {res.indexed_resource_id} | Degree: {res.degree}\n"
        return ret


if __name__ == "__main__":
    romfiles = ["/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/data/fiches_rome/ROME_M1302.json",
                "/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/data/fiches_rome/ROME_M1805.json",
                "/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/data/fiches_rome/ROME_M1806.json",
                "/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/data/fiches_rome/ROME_M1802.json",
                "/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/data/fiches_rome/ROME_M1804.json"
    ]
#    exfile = "/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/data/fiches_rncp/RNCP38637.json"  

    rome_skillbase = SkillsBase()
    for exfile in romfiles:
        skill = Skill()
        skill.load_from_json(exfile)
        rome_skillbase.add_skill(skill)
 