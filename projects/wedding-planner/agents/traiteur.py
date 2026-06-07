# traiteur.py
import asyncio
import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_tools
from dotenv import load_dotenv
import os

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

async def agent_traiteur():
    # Vérification de sécurité pour Groq
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : La variable d'environnement 'GROQ_API_KEY' n'est pas configurée.")
        return

    # Extraction et conversion automatique des outils MCP pour LangChain
    tools = await get_mcp_tools(timeout=120)
    traiteur_tools = [
        tool for tool in tools
        if "traiteur" in tool.name
    ]
    
    # Initialisation du modèle gratuit de Groq performant sur les outils
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    # Design du Prompt Système orienté Traiteur
    SYSTEM_PROMPT = """Tu es l'Agent Expert Traiteur et Gastronomie pour l'application de planification de mariage.
    Ton unique but est d'aider les couples à concevoir leur menu de mariage et à valider l'estimation financière.
    
    Tu as accès à des outils connectés pour :
    1. Interroger la base culinaire réelle (TheMealDB) et composer des assortiments de 10 plats.
    2. Calculer automatiquement le coût moyen par personne selon le style demandé.
    3. Injecter directement le montant estimé dans la table des dépenses et sauvegarder les plats retenus.
    
    Styles de menus disponibles que tu peux exploiter : 'viande', 'gourmet', 'vegetarien', 'cocktail'.
    Présente toujours le résultat final de manière élégante et structurée, en mettant en valeur le coût total pour rassurer les mariés."""
    
    # Création du sous-agent conformé à tes spécifications
    agent = create_agent(model=llm, 
                        tools=traiteur_tools, 
                        system_prompt=SYSTEM_PROMPT,
                        debug=True,
    )
    
    # Scénario de test de production complet : Génération + Calcul de coût + Enregistrement BDD
    requete_test = (
        "Bonjour ! Pour le mariage ID 1, nous aimerions proposer un menu de style 'gourmet' "
        "à nos invités. Nous serons 120 personnes au total. "
        "Peux-tu nous générer les propositions de plats et enregistrer le devis dans notre budget ?"
    )
    
    print(f"\n🚀 Lancement de la requête d'analyse Traiteur :\n{requete_test}\n")
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n \n🎯 Rapport final de l'Agent Traiteur :\n")
    final_message = resultat["messages"][-1]

    print(final_message.content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_traiteur())