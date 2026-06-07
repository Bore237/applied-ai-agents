# client_lieux.py
import asyncio
import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_tools
from dotenv import load_dotenv
import os

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

async def agent_lieux():
    # Vérification de sécurité pour Groq
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : La variable d'environnement 'GROQ_API_KEY' n'est pas configurée.")
        return

    # Extraction et conversion automatique des outils MCP pour LangChain
    lieux_tools = await get_mcp_tools(timeout=120)
    
    # Initialisation du modèle gratuit de Groq performant sur les outils
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    # Design du Prompt Système
    SYSTHEM_PROMT = """"Tu es l'Agent Expert en recherche et réservation de Lieux pour l'application de mariage.
        Ton unique but est d'aider les utilisateurs à trouver la salle idéale et à valider la réservation.
        
        Tu as accès à des outils connectés à la base de données pour :
        1. Rechercher des lieux selon le style ou le budget maximum.
        2. Vérifier la capacité d'accueil et valider définitivement une réservation pour un mariage.
        
        Sois précis, utilise les IDs des lieux lors des confirmations de réservation."""
    
    # Création du sous-agent conformément aux spécifications demandées
    agent = create_agent(model=llm, 
                        tools=lieux_tools, 
                        system_prompt=SYSTHEM_PROMT,
                        debug=True,
    )
    
    # Scenario de test de production complet : Recherche + Réservation automatique
    requete_test = (
        "Trouve-moi un lieu disponible avec un style 'Pavillon' ou 'similaire'. "
        "Si tu en trouves un qui rentre dans un budget de 50000€, et si c'est situer a Paris réserve-le directement "
        "pour le mariage ID 1, sachant que nous aurons 60 invités."
    )
    
    print(f"\n🚀 Lancement de la requête d'analyse :\n{requete_test}\n")
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n \n🎯 Rapport final de l'Agent Lieux :\n")
    final_message = resultat["messages"][-1]

    print(final_message.content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_lieux())
