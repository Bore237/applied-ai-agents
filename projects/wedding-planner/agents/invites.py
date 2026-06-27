# agent_invites.py
import asyncio
import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_one_tools
from dotenv import load_dotenv
from schemas.prompt import SYSTEM_PROMPT_INVITES

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

async def agent_invites():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : 'GROQ_API_KEY' manquante.")
        return

    invites_tools = await get_mcp_one_tools(name_tools='invites', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = SYSTEM_PROMPT_INVITES

    agent = create_agent(
        model=llm, 
        tools=invites_tools, 
        system_prompt=SYSTEM_PROMPT,
        debug=True,
    )
    
    # Simulation de la donnée tabulaire convertie en liste de dicts en amont
    data_tabulaire_simulee = [
        {"nom": "Dupont", "prenom": "Jean", "email": "jean.dupont@mail.com", "statut_rsvp": "En_Attente"," besoin_vol": "Oui", "ville_origine": "Nice"},
        {"nom": "Martin", "prenom": "Claire", "email": "claire.martin@mail.com","statut_rsvp": "En_Attente", "besoin_vol": "Non", "ville_origine": "Paris"},
        {"nom": "Durand", "prenom": "Marc", "email": "marc.durand@mail.com", "statut_rsvp": "En_Attente", "besoin_vol": "Oui", "ville_origine": "Nice"},
        {"nom": "Levier", "prenom": "Sophie", "email": "sophie.l@mail.com", "statut_rsvp": "En_Attente", "besoin_vol": "Oui", "ville_origine": "Toulouse"},
        # Doublon volontaire pour tester la sécurité du tool :
        {"nom": "Dupont", "prenom": "Jean", "email": "jean.dupont@mail.com", "statut_rsvp": "En_Attente", "besoin_vol": "Oui", "ville_origine": "Nice"}
    ]
    

    requete_test = """
        Prends en charge cette liste d'invités pour le mariage ID 1 et intègre-la en base de données. 
        Données : [
            {"nom": "Lefebvre", "prenom": "Thomas", "email": "thomas.l@mail.com", "besoin_vol": "Oui", "ville_origine": "Lille"},
            {"nom": "Gomez", "prenom": "Anita", "email": "anita.g@mail.com", "besoin_vol": "Oui", "ville_origine": "Lille"}
        ]
        Donne-moi la synthèse de l'import et les statistiques de vols.
    """

    requete_test = """
    L'invi-té avec l'ID 3 vient de m'informer qu'il ne pourra malheureusement pas venir au mariage. 
    Modifie son statut RSVP en 'Decline' en utilisant l'outil approprié. 
    Affiche-moi ensuite le rapport mis à jour pour que je voie l'impact sur le nombre total d'invités actifs et sur les besoins de vols.
    """

    r7equete_test = """
    Pour le mariage ID 1, extrait uniquement les besoins de vols actuels de la base de données. 
    J'ai besoin de connaître la répartition exacte par ville d'origine pour la transmettre à notre expert aérien. 
    Présente le résultat selon ton format habituel.
    """
    requ7ete_test = requete_test = f"""
    Prends en charge cette liste d'invités pour le mariage ID 1 et intègre-la en base de données. 
    Fais-moi ensuite un rapport du nombre total d'invités à jour et liste précisément les villes de départ 
    qui nécessitent qu'on cherche des vols, avec le nombre de voyageurs par ville.
    
    Données : {data_tabulaire_simulee}
    """
    
    print(f"\n🚀 Lancement de l'Agent Invités...")
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n🎯 Rapport final de l'Agent Invités :\n")
    print(resultat["messages"][-1].content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_invites())