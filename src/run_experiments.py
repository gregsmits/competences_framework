from skill_def.skill_base import *
from utils.indexer import Indexer
import utils.skill_loader as skillloader
import uuid
import os, sys
import tqdm
from utils.comparators import spearman_correlation, raw_differences
import math


#########################################
# Context of the experiments
#########################################

#Analysis of the university program INFO-FIP (RNCP38637) and associated ROME skills
university_program = "IMTATLANTIQUE-FIP"
RNCPCODE = "RNCP38637"
rncp_file = "data/fiches_rncp/RNCP38637.json"

#Associated ROME FILES
rome_files = ["data/fiches_rome/ROME_M1302.json", "data/fiches_rome/ROME_M1802.json",  "data/fiches_rome/ROME_M1804.json",  "data/fiches_rome/ROME_M1805.json",  "data/fiches_rome/ROME_M1806.json"]


#Associated JOB OFFERS
job_offers_directory = "data/offres_emploi_JSON/"

#########################################
# Creation of the three skills-bases
#########################################

#RNCP SKILLS BASE FIP training (RNCP38637)
skillrncp = skillloader.load_from_json(rncp_file)
skills_base_rncp = SkillsBase(skills=[])
skills_base_rncp.add_skill(skillrncp)


#ROME SKILLS BASE
skills_base_rome = SkillsBase(skills=[])
for rome_file in rome_files:
    skill_rome = Skill()
    skill_rome.load_from_json(rome_file)
    skills_base_rome.add_skill(skill_rome)

#JOB OFFERS SKILLS BASE
skills_base_job_offers = skillloader.load_base_from_directory(job_offers_directory)


#########################################
# Loading of the ROME indexers
#########################################
pbs_indexer_name = RNCPCODE+"_problems_family.idx"
resources_indexer_name = RNCPCODE+"_resources.idx"

if pbs_indexer_name not in os.listdir():
    raise Exception(f"Index {pbs_indexer_name} does not exist. Create it first using the createindexes.py script")

if resources_indexer_name not in os.listdir():
    raise Exception(f"Index {resources_indexer_name} does not exist. Create it first using the createindexes.py script")
else:
    #Load existing indexers
    tqdm.tqdm.write(f"Loading existing indexes: {pbs_indexer_name} and {resources_indexer_name}")
    pbs_indexer = Indexer(index_name=pbs_indexer_name)
    resources_indexer = Indexer(index_name=resources_indexer_name)
    tqdm.tqdm.write("Indexes loaded successfully.")

#########################################
# Alignment of the three skills bases with the ROME indexers
#########################################
#(skills_base_rncp, "RNCP38637 skills base"),
for sb, name in tqdm.tqdm([ (skills_base_rome, "ROME skills base"), (skills_base_job_offers, "Job offers skills base")]):
    tqdm.tqdm.write(f"Aligning {name} with ROME indexers.")
    sb.align_with_indexer(pb_indexer=pbs_indexer, res_indexer=resources_indexer)
    tqdm.tqdm.write("Alignment done successfully.")

sys.exit(0)
#########################################
# Analysis of resources per problem for the three skills bases
#########################################
skills_base_rncp.analyze_resources_per_problem()
skills_base_rome.analyze_resources_per_problem()
skills_base_job_offers.analyze_resources_per_problem()


#########################################
# Compare resources rankings between the three skills bases
#########################################

weighted_resources_rncp = skills_base_rncp.assign_resource_degrees()
weighted_resources_rome = skills_base_rome.assign_resource_degrees()
weighted_resources_job_offers = skills_base_job_offers.assign_resource_degrees()


#Compare ROME SKILLS BASE with RNCP38637 SKILLS BASE
print("\nComparing ranked resources between ROME skills base and RNCP38637 skills base:")
print(f"\t- Number of resources in common: {len(set(weighted_resources_rome.keys()).intersection(set(weighted_resources_rncp.keys())))} out of {len(weighted_resources_rome)} for ROME and {len(weighted_resources_rncp)} for RNCP38637.")
spearman_rome_rncp = spearman_correlation(weighted_resources_rome, weighted_resources_rncp)
print(f"\t- Spearman correlation: {spearman_rome_rncp}")
print("\t- Main differences :")
differences_rome_rncp = raw_differences(weighted_resources_rome, weighted_resources_rncp)
sorted_differences_rome_rncp = dict(sorted(differences_rome_rncp.items(), key=lambda item: abs(item[1]), reverse=True))
for res_id, diff in list(sorted_differences_rome_rncp.items())[:10]:
    print(f"\t\t-Resource ID: {resources_indexer.get_document_by_id(res_id).page_content}, Degree difference (ROME - RNCP38637): {diff}")


#Compare ROME SKILLS BASE with JOB OFFERS SKILLS BASE
print("\n\nComparing ranked resources between ROME skills base and Job offers skills base:")
print(f"\t- Number of resources in common: {len(set(weighted_resources_rome.keys()).intersection(set(weighted_resources_job_offers.keys())))} out of {len(weighted_resources_rome)} for ROME and {len(weighted_resources_job_offers)} for Job offers.")
spearman_rome_joboffers = spearman_correlation(weighted_resources_rome, weighted_resources_job_offers)
print(f"\t- Spearman correlation: {spearman_rome_joboffers}")
print("\t- Main differences :")
differences_rome_joboffers = raw_differences(weighted_resources_rome, weighted_resources_job_offers)
sorted_differences_rome_joboffers = dict(sorted(differences_rome_joboffers.items(), key=lambda item: abs(item[1]), reverse=True))
for res_id, diff in list(sorted_differences_rome_joboffers.items())[:10]:
    print(f"\t\t-Resource ID: {resources_indexer.get_document_by_id(res_id).page_content}, Degree difference (ROME - Job offers): {diff}")


#Compare RNCP38637 SKILLS BASE with JOB OFFERS SKILLS BASE
print("\n\nComparing ranked resources between RNCP38637 skills base and Job offers skills base:")
print(f"\t- Number of resources in common: {len(set(weighted_resources_rncp.keys()).intersection(set(weighted_resources_job_offers.keys())))} out of {len(weighted_resources_rncp)} for RNCP38637 and {len(weighted_resources_job_offers)} for Job offers.")
spearman_rncp_joboffers = spearman_correlation(weighted_resources_rncp, weighted_resources_job_offers)
print(f"\t- Spearman correlation: {spearman_rncp_joboffers}")
print("\t- Main differences :")
differences_rncp_joboffers = raw_differences(weighted_resources_rncp, weighted_resources_job_offers)
sorted_differences_rncp_joboffers = dict(sorted(differences_rncp_joboffers.items(), key=lambda item: abs(item[1]), reverse=True))
for res_id, diff in list(sorted_differences_rncp_joboffers.items())[:10]:
    print(f"\t\t-Resource ID: {resources_indexer.get_document_by_id(res_id).page_content}, Degree difference (RNCP38637 - Job offers): {diff}")


###############################
# Implementation of indicators
###############################
'''Core set- and weight-based indicators'''

def jaccard_similarity(RA, RB):
    return len(RA & RB) / len(RA | RB) if (RA | RB) else 0.0


def coverage_ratio(RA, RB):
    return len(RA & RB) / len(RA) if RA else 0.0


def weighted_coverage(weights_A, weights_B):
    RA, RB = set(weights_A), set(weights_B)
    numerator = sum(weights_A[r] for r in RA & RB)
    denominator = sum(weights_A.values())
    return numerator / denominator if denominator > 0 else 0.0


def missing_importance_mass(weights_A, weights_B):
    RA, RB = set(weights_A), set(weights_B)
    return sum(weights_A[r] for r in RA - RB)


def mean_absolute_degree_shift(weights_A, weights_B):
    RAB = set(weights_A) & set(weights_B)
    if not RAB:
        return 0.0
    return sum(abs(weights_A[r] - weights_B[r]) for r in RAB) / len(RAB)


'''Distrbiubtion indicators'''


def gini_coefficient(weights):
    values = sorted(weights.values())
    n = len(values)
    if n == 0:
        return 0.0
    cumulative = sum((i + 1) * v for i, v in enumerate(values))
    return (2 * cumulative) / (n * sum(values)) - (n + 1) / n


def entropy(weights):
    total = sum(weights.values())
    if total == 0:
        return 0.0
    return -sum(
        (w / total) * math.log(w / total)
        for w in weights.values()
        if w > 0
    )


print("\n\nAdditional contrastive indicators")

def run_indicators(name_A, weights_A, name_B, weights_B):
    RA, RB = set(weights_A), set(weights_B)

    print(f"\n{name_A} vs {name_B}")
    print(f"  Jaccard similarity: {jaccard_similarity(RA, RB):.4f}")
    print(f"  Coverage ({name_A} → {name_B}): {coverage_ratio(RA, RB):.4f}")
    print(f"  Weighted coverage ({name_A} → {name_B}): {weighted_coverage(weights_A, weights_B):.4f}")
    print(f"  Missing importance mass ({name_A} \\ {name_B}): {missing_importance_mass(weights_A, weights_B):.4f}")
    print(f"  Mean absolute degree shift: {mean_absolute_degree_shift(weights_A, weights_B):.4f}")
    print(f"  Gini({name_A}): {gini_coefficient(weights_A):.4f}")
    print(f"  Gini({name_B}): {gini_coefficient(weights_B):.4f}")
    print(f"  Entropy({name_A}): {entropy(weights_A):.4f}")
    print(f"  Entropy({name_B}): {entropy(weights_B):.4f}")


run_indicators("ROME", weighted_resources_rome, "RNCP38637", weighted_resources_rncp)
run_indicators("ROME", weighted_resources_rome, "JobOffers", weighted_resources_job_offers)
run_indicators("RNCP38637", weighted_resources_rncp, "JobOffers", weighted_resources_job_offers)


