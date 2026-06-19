import asyncio
import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_one_tools
from dotenv import load_dotenv

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

async def agent_traiteur():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : GROQ_API_KEY manquante.")
        return

    traiteur_tools = await get_mcp_one_tools(name_tools="traiteur", timeout=30)
    
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = """
        Tu es l'Agent Expert Traiteur et Gastronomie pour l'application de planification de mariage.
        Ton but exclusif est de générer les assortiments de menus et de valider les écritures financières associées.

        CONSIGNES DE CONTRÔLE DES DONNÉES :
        1. Tu manipules des outils retournant des structures JSON complexes contenant les clés 'success', 'data' et 'error'.
        2. Si la clé 'success' est égale à false, tu bloques immédiatement le traitement et tu exposes la clé 'error' sans inventer de résultats fictifs.
        3. Ne prends jamais d'initiative de style de menu hors de la liste : 'viande', 'gourmet', 'vegetarien', 'cocktail'.
        4. Une fois le tools  obtenir_menus_traiteur appeler et le resultat retourné stop execution 

        FORMAT DE RESTITUTION VISUELLE OBLIGATOIRE :
        Tu dois traduire le dictionnaire brut renvoyé par l'outil de cette manière exacte pour l'utilisateur final :

        ### 🍽️ Proposition de Menu de Mariage — Style: [Style_Applique]
        *Nombre de convives pris en charge : [Nombre_Invites] personnes et [limit_nombre_plat] plats*

        #### 📋 Liste des Propositions Culinaire Retenues :
        - [Nom du Plat] (*[Catégorie]*) — [Prix] € / pers
        *(Affiche l'intégralité des 10 plats transmis par l'outil)*

        #### 💰 Analyse Financière de la Prestation
        - **Tarif unitaire estimé :** [Prix_Moyen_Par_Personne] € / invité
        - **Coût Global Projeté :** [Cout_Total_Estime] €
        - **Statut de l'opération :** Écritures enregistrées avec succès en Base de Données.
    """
    
    agent = create_agent(
        model=llm, 
        tools=traiteur_tools, 
        system_prompt=SYSTEM_PROMPT,
        debug=True
    )
    
    requete_test = (
        "Bonjour ! Pour le mariage ID 1, nous aimerions proposer un menu de style 'gourmet' de 5 plats"
        "à nos invités. Nous serons 120 personnes au total. "
        "Peux-tu nous générer les propositions de plats et enregistrer le devis dans notre budget ?"
    )
    
    print(f"\n🚀 Lancement de la requête d'analyse Traiteur :\n{requete_test}\n")
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n🎯 Rapport final de l'Agent Traiteur :\n")
    print(resultat["messages"][-1].content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_traiteur())