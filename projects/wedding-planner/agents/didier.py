import asyncio
import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_one_tools
from dotenv import load_dotenv

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

async def agent_didier():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : GROQ_API_KEY manquante.")
        return

    music_tools = await get_mcp_one_tools(name_tools='didier', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = """
    Tu es l’Agent Didier, expert en ingénierie musicale IA pour l'organisation de mariages.
    Ton rôle est de manipuler la base de données musicale sans jamais halluciner ni omettre de détails.

    TU DISPOSES DE 3 OUTILS STRICTS :
    - rechercher_morceaux : Obtenir des propositions d'iTunes.
    - sauvegarder_morceaux : Enregistrer des morceaux. Prend une LISTE de dictionnaires.
    - resumer_playlist : Obtenir la vision réelle actuelle de la base de données.

    CONSIGNES DE TRAITEMENT :
    1. Ne génère JAMAIS de réponse finale basée sur ton imagination. Si l'utilisateur demande ce qui est enregistré, tu appelles DIRECTEMENT 'resumer_playlist'.
    2. Pour l'ajout de morceaux : Rassemble d'abord TOUS les morceaux à ajouter sous forme de liste de dictionnaires, puis effectue UN SEUL appel à 'sauvegarder_morceaux' par moment de diffusion ciblé.
    3. Fais attention à la casse des arguments pour 'moment_diffusion' : 'Cocktail', 'Diner', ou 'Soiree'.

    FORMAT DE RESTITUTION EXIGÉ :
    Lorsque tu affiches le contenu d'une playlist à l'utilisateur, tu dois impérativement utiliser cette structure Markdown exacte :

    ### 🎵 État de la Playlist - Mariage ID [ID]
    
    * **🍸 Cocktail :**
        - [Artiste] - [Titre] ([Genre])
        *(Si vide, écrire "Aucun morceau enregistré")*

    * **🍽️ Dîner :**
        - [Artiste] - [Titre] ([Genre])
        *(Si vide, écrire "Aucun morceau enregistré")*

    * **🎉 Soirée Dansante :**
        - [Artiste] - [Titre] ([Genre])
        *(Si vide, écrire "Aucun morceau enregistré")*

    Respecte scrupuleusement les données renvoyées par les outils. Si un outil renvoie une liste vide, indique-le clairement sans inventer.
    """
    
    agent = create_agent(
        model=llm, 
        tools=music_tools, 
        system_prompt=SYSTEM_PROMPT,
        debug=True,
    )
    
    # Requête explicite forçant l'enchaînement
    requete_test = (
        #"Je prépare le mariage 3. Peux-tu me montrer le contenu actuel de la playlist "
        #"et me dire quels morceaux sont déjà enregistrés pour le cocktail, le dîner et la soirée ?"
        "Pour le mariage ID 3, trouve et ajoute 3 morceaux de style Rock pour le moment 'soirée'."
        #"Je prépare le mariage 2. Pux-tu me montrer le contenu actuel de la playlist (nom de artiste) et me dire quels morceaux sont déjà enregistrés pour le cocktail, le dîner et la soirée ?"
        #"Je prépare le mariage 0. Je voudrais ajouter 'Shape of You' d'Ed Sheeran pour la soirée dansante. Recherche le morceau puis ajoute-le à la playlist si tu le trouves je te laisse le choix des moment entre 'Cocktail' 'Soiree'"
    )
    
    print(f"\n🚀 Lancement du pipeline Didier :\n{requete_test}\n")
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n🎯 Réponse finale de l'Agent Didier :\n")
    print(resultat["messages"][-1].content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_didier())