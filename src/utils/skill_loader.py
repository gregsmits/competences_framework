
import json
import sys
#add utils to class path
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skill_def'))
from skill_base import Skill, SkillsBase, Resource, FamilyOfProblems
from indexer import Indexer



def load_from_json(file_path: str) -> Skill:
    """Load a skill from a json file representing a 
        {
        "resource": "Concevoir des applications informatiques en analysant des besoins d'un commanditaire et en mettant en œuvre les éléments technologiques ou des dispositifs expérimentaux dans des activités de recherche et de développement en mobilisant un large champs de sciences fondamentales et des éléments organisationnels",
        "type": "Savoir-faire",
        "category": "Élaborer un diagnostic d'un système d'information, des réseaux d'entreprise ou d'opérateurs ou d'une organisation sur une problématique spécifique"
    },

    Args:
        file_path (str): _description_
    """
    s = Skill()

    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        s.source = json_data.get("source", "Unknown")
        s.title = json_data.get("label", "unknown")
        s.pb_family = FamilyOfProblems(s.title, " ; ".join(json_data.get("problems_family", [])))
        for r in json_data.get("resources", []):
            if r.get("resource", "") not in [res.description for res in s.resources]:
                resource = Resource(
                    description=r.get("resource", ""),
                    type=r.get("type", ""),
                    category=r.get("category", None)
                )
                s.resources.append(resource)
    return s

def load_from_job_offer(file_path: str) -> Skill:
    """Load a skill from a job offer pdf file.

    Args:
        file_path (str): _description_
    """
    s = Skill()

    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        s.source = "job_offer  "
        s.title = json_data.get("label", "unknown")
        s.pb_family = FamilyOfProblems(s.title, json_data.get("problem_family", "unknown"))
        for res in json_data.get("resources", []):
            resource = Resource(
                description=res,
                type="Unknown",
                category="Unknown"
            )
            s.resources.append(resource)
    return s


def load_base_from_directory(directory: str) -> SkillsBase:
    """Load a skills base from a directory containing json files.

    Args:
        directory (str): _description_
    """
    skills = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            skill = load_from_job_offer(file_path)
            skills.append(skill)
    return SkillsBase(skills=skills)

if __name__ == "__main__":
    #load indexers
    pbs_indexer_name = "/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/RNCP38637_problems_family.idx"
    resources_indexer_name = "/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/RNCP38637_resources.idx"
    import tqdm
    print(f"***\nLoading existing indexes: {pbs_indexer_name} and {resources_indexer_name}")
    
    tqdm.tqdm.write("Loading indexes...")
    pbs_indexer = Indexer(index_name=pbs_indexer_name)
    resources_indexer = Indexer(index_name=resources_indexer_name)
    tqdm.tqdm.write("\tIndexes loaded successfully.")

    #test loading a skills base from a directory
    if True:
        tqdm.tqdm.write("Loading skills base from job offers...")
        skills_base = load_base_from_directory("/Volumes/Data/Research/Publications/2026/EDM/experiments/compcomp/data/offres_emploi_JSON/Temp/")
        tqdm.tqdm.write(f"\tSkills base loaded successfully ({len(skills_base.skills)}) skills.")
        tqdm.tqdm.write("***Align skills base with indexers.")
        skills_base.align_with_indexer(pb_indexer=pbs_indexer, res_indexer=resources_indexer)
        tqdm.tqdm.write("\tAlignment done successfully.")

        tqdm.tqdm.write("***Resources analysis.")
        skills_base.analyze_resources_per_problem()
        skills_base.assign_resource_degrees()
        tqdm.tqdm.write("\tResource analysis done successfully.")

        print("RESULTS : Ranked list of resources for the ROME base:")
        for resd in skills_base.rank_resources():
            doc = resources_indexer.get_document_by_id(resd[0])
            print(f"\t-Resource: {doc.page_content} | Degree: {resd[1]}")
            
    if False:
        # #test loading a skill from a json file
        loader = SkillLoader()
        skill = loader.load_from_json("/Volumes/Data/Research/Publications/2026/AIED/experiments/compcomp/data/fiches_rncp/RNCP38637.json")
        print(f"Loaded skill: {skill.title} from source: {skill.source}")
        print(f"Problems family: {skill.pb_family.label} - {skill.pb_family.description}")
        for res in skill.resources:
            print(f"Resource: {res.description} - Type: {res.type} - Category: {res.category}")