import uuid
import os
from langchain_core.documents import Document

from skill_def.skill_base import *
from utils.indexer import Indexer

#Analysis of the university program INFO-FIP (RNCP38637) and associated ROME skills
university_program = "IMTATLANTIQUE-FIP"
RNCPCODE = "RNCP38637"

#Create the skills-base from ROME files
# Load JSON FILES, INDEX RESOURCES AND FAMILIES OF PROBLEMS
rome_files = ["data/fiches_rome/ROME_M1302.json", "data/fiches_rome/ROME_M1802.json",  "data/fiches_rome/ROME_M1804.json",  "data/fiches_rome/ROME_M1805.json",  "data/fiches_rome/ROME_M1806.json"]


#Create a skills-base from its attached ROME files
#ROME files associated with RNCP38637

skills_base_rome = SkillsBase(skills=[])
for rome_file in rome_files:
    skill_rome = Skill()
    skill_rome.load_from_json(rome_file)
    skills_base_rome.add_skill(skill_rome)

assert (len(skills_base_rome.skills) == len(rome_files)), "All skills not loaded"

pbs_indexer_name = RNCPCODE+"_problems_family.idx"
resources_indexer_name = RNCPCODE+"_resources.idx"

#Index of families of problems
#generate index for families of problems if it does not exist
#check if index exists
if pbs_indexer_name not in os.listdir():
    print(f"Index {pbs_indexer_name} does not exist. It will be created.")

    docs_pbs = []
    ids_pbs = []
 
    print("************ Indexing families of problems ************")
    for skill in skills_base_rome.skills:
        #Index families of problems


        doc = Document(page_content=(skill.pb_family.label+skill.pb_family.description), metadata={"skill_title": skill.title})
        print(f"\t-INDEXING THE FAMILY OF PROBLEMS: {doc}")
        docs_pbs.append(doc)
        ids_pbs.append(uuid.uuid4())
    #save the index
    pbs_indexer = Indexer(index_name=pbs_indexer_name)
    pbs_indexer.index_documents(    
        documents=docs_pbs,
        ids=ids_pbs 
    )
    pbs_indexer.save_index()

if resources_indexer_name not in os.listdir():
    docs_res = []
    ids_res = []
    temp = []
    #Index resources

    print("************ Indexing resources ************")
    for skill in skills_base_rome.skills:
        for res in skill.resources:
            doc = Document(page_content=res.description, metadata={
    #            "skill_title": skill.title,
                "resource_type": res.type,
                "resource_category": res.category
            })
            if res.description not in temp:
                temp.append(res.description)
                print(f"\t-INDEXING RESOURCE: {doc}")
                docs_res.append(doc)
                ids_res.append(uuid.uuid4())
    resources_indexer = Indexer(index_name=resources_indexer_name)
    resources_indexer.index_documents(
        documents=docs_res,
        ids=ids_res
    )
    resources_indexer.save_index()
else:
    #Load existing indexers
    print(f"Loading existing indexes: {pbs_indexer_name} and {resources_indexer_name}")
    pbs_indexer = Indexer(index_name=pbs_indexer_name)
    resources_indexer = Indexer(index_name=resources_indexer_name)



# #test align rome skills base with itself
# print("\n\n************\nAlign ROME skills base with ROME indexers.")
# skills_base_rome.align_with_indexer(pb_indexer=pbs_indexer, res_indexer=resources_indexer)
# skills_base_rome.analyze_resources_per_problem()
# skills_base_rome.assign_resource_degrees()
# print("Rankes list of resources for the ROME base:")
# for resd in skills_base_rome.rank_resources():
#     print(f"\t-Resource: {resd[0].description} | Degree: {resd[1]}")

#skills_base_rome.align_with_indexer(pb_indexer=pbs_indexer, res_indexer=resources_indexer)

# print("\n\n************\nAligned RNCP skills base with ROME indexers.")
# skills_base_rncp.align_with_indexer(pb_indexer=pbs_indexer, res_indexer=resources_indexer)
# skills_base_rncp.analyze_resources_per_problem()
# skills_base_rncp.assign_resource_degrees()
# print("Rankes list of resources for the RNCP skills base:")
# for resd in skills_base_rncp.rank_resources():
#     print(f"\t-Resource: {resd[0].description} | Degree: {resd[1]}")


# if False:
#     #Search alignment between RNCP resources and ROME resources
#     for res in skillrncp.resources:
#         print(f"*************\nRNCP Resource: {res.description}")
#         results = resources_indexer.query(query=res.description, top_k=2)
#         for i, result in enumerate(results):
#             print(f"\t-Match {i+1}: {result.page_content} (Metadata: {result.metadata})")
#         print(f"*************\n")
