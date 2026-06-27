import asyncio
import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent  # Signature moderne et standard de production
from tools.mcp_tools import get_mcp_one_tools
from dotenv import load_dotenv

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

async def agent_lieux():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : GROQ_API_KEY manquante.")
        return

    lieux_tools = await get_mcp_one_tools(name_tools='lieux', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = """
        Tu es l'Agent Expert en recherche et réservation de Lieux pour l'application de mariage.
        
        CRITIQUE : Tu ne dois générer qu'UN SEUL appel d'outil par tour de conversation. 
        Il est strictement interdit de paralléliser ou de deviner des arguments.

        PROCESSUS OBLIGATOIRE EN 2 TOURS DISTINCTS :
        - Tour 1 : Appelle UNIQUEMENT `rechercher_lieux_disponibles`. Tu ne connais pas le `lieux_id` à ce stade, ne tente pas de réserver.
        - Tour 2 : Attends de recevoir le résultat de l'outil. Extrais-en le `lieux_id` réel (ex: 3), puis appelle `reserver_lieux_mariage` avec cet ID précis.

        CONSIGNES STRICTES :
        - Les outils renvoient des dictionnaires contenant des clés 'success', 'data' et 'error'.
        - Si la recherche échoue ("success": false), arrête-toi et explique l'erreur.
        - Ne génère ton rapport final de succès QUE SI l'outil `reserver_lieux_mariage` a retourné "success": true.

        FORMAT DE RAPPORT EXIGÉ EN CAS DE SUCCÈS DE RÉSERVATION :
        ### 🏰 Confirmation de Réservation de Lieu
        - **Nom de l'établissement :** [Nom du lieu]
        - **Localisation :** [Ville du lieu]
        - **Identifiant Unique (ID) :** [ID du lieu]
        
        ### 📊 Métriques Logistiques & Financières
        - **Jauge d'invités validée :** [Nombre d'invités] personnes
        - **Impact Budgétaire :** [Tarif] € (Injecté avec succès dans le module Budget)
        - **Statut global du dossier :** Verrouillé & assigné au Mariage ID [Mariage ID]
    """
    
    # Instanciation native via create_agent
    agent = create_agent(
        model=llm, 
        tools=lieux_tools, 
        system_prompt=SYSTEM_PROMPT,
        debug=True ,
    )
    
    requete_test = (
        "Trouve-moi un lieu disponible sur Paris pour le mariage ID 0 de  60 invités qui rentre dans un budget de 50000€"
    )
    
    print(f"\n🚀 Lancement de la requête d'analyse via create_agent :\n{requete_test}\n")
    
    # Invocation avec passage de l'état des messages attendu par l'architecture
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n🎯 Rapport final de l'Agent Lieux :\n")
    print(resultat["messages"][-1].content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_lieux())