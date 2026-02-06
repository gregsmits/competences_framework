import os
import json
import ollama
from PyPDF2 import PdfReader

# Chemins à configurer
DOSSIER_SOURCE = "/Volumes/Data/Research/Publications/2026/EDM/experiments/RawData/ENSSAT_jobOffers/2022"
DOSSIER_DESTINATION = "/Volumes/Data/Research/Publications/2026/EDM/experiments/skills-base/data/offres_emploi_JSON_enssat/2022"

if not os.path.exists(DOSSIER_DESTINATION):
    os.makedirs(DOSSIER_DESTINATION)

def extraire_texte_pdf(chemin_pdf):
    reader = PdfReader(chemin_pdf)
    texte = ""
    for page in reader.pages:
        texte += page.extract_text()
    return texte

def formater_avec_llama(texte_pdf):
    prompt = f"""
    You are an expert in the analysis of job offers. Analyse the following text from a job offer and return ONLY a JSON object.
    The JSON must have two keys:
    1. "problem_family" : the exact job title.
    2. "resources" : a list of sentences including tasks, skills, and soft skills.

    Texte :
    {texte_pdf}
    """
    
    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': prompt},
    ])
    
    # Nettoyage pour s'assurer de n'avoir que le JSON
    contenu = response['message']['content']
    return contenu[contenu.find("{"):contenu.rfind("}")+1]

# Boucle sur les 119 fichiers
filenb=1
for fichier in os.listdir(DOSSIER_SOURCE):
    if fichier.endswith(".pdf"):
        print(f"Traitement de {fichier}...")
        
        try:
            # 1. Extraction
            texte = extraire_texte_pdf(os.path.join(DOSSIER_SOURCE, fichier))
            
            # 2. Structuration par l'IA
            json_str = formater_avec_llama(texte)
            donnees = json.loads(json_str)
            
            # 3. Écriture du fichier JSON
            #nom_json = fichier.replace(".pdf", ".json")
            nom_json = f"joboffer_{filenb}.json"
            with open(os.path.join(DOSSIER_DESTINATION, nom_json), "w", encoding="utf-8") as f:
                json.dump(donnees, f, indent=4, ensure_ascii=False)
                filenb+=1
                
        except Exception as e:
            print(f"Erreur sur le fichier {fichier}: {e}")

print("Terminé !")