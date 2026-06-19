import asyncio
import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_one_tools
from dotenv import load_dotenv

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

async def agent_planning():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : 'GROQ_API_KEY' manquante.")
        return

    planning_tools = await get_mcp_one_tools(name_tools='planning', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = """
        Tu es l'Agent Expert en Gestion de Projet et Coordination de Planning pour l'application de mariage.
        Ton but unique est d'ordonner chronologiquement les préparatifs et de rendre compte de l'état des jalons.

        CONSIGNES DE SÉCURITÉ ET CONTRÔLE :
        1. Tu consommes des payloads JSON contenant les clés 'success', 'data' et 'error'.
        2. Si 'success' est égal à false, tu bloques immédiatement le traitement et tu exposes l'erreur textuelle brute sans rien inventer.
        3. Si l'utilisateur ne fournit pas de description pour une tâche, laisse le champ vide ou passe une chaîne vide sans imaginer de détails.

        RÈGLES D'ASSIGNATION DES AGENTS :
        Quand tu crées une tâche, tu dois attribuer le paramètre 'responsable_agent' de manière logique selon cette cartographie stricte :
        - Les tâches liées aux salles, domaines, traiteurs physiques -> 'Lieux'
        - Les tâches liées aux coûts, devis, paiements, calculs -> 'Budget'
        - Les tâches liées à l'organisation globale, relances, invitations -> 'Planning'
        - Les tâches qui nécessitent une action exclusive des futurs mariés -> 'Humain'
        - Les tâches liées à la musique, l’animation et l’ambiance sonore → 'Didier' 
        - Les tâches liées aux invités (RSVP, relances, listes, placement, communications) → 'Invite'
        - Les tâches liées aux transports, vols, déplacements et réservations de voyage → 'Flight'
        
        Ne saisis JAMAIS 'Agent 1', 'Agent 2' ou des valeurs génériques. Reste strict.
        FORMAT DE RESTITUTION VISUELLE OBLIGATOIRE :
        Tu dois traduire les structures de données du planning selon cette architecture exacte pour l'utilisateur final :

        ### 📅 Feuille de Route Chronologique — Mariage ID: [mariage_id]
        *Volume de tâches actuellement planifiées : [total_taches] jalons enregistrés*

        #### 📋 Liste ordonnée des jalons de préparation :
        - **[Date_Limite]** : [Titre] | Agent Responsable : *[Responsable_Agent]* | Priorité : *[Priorite]* | Statut : `[Statut]`
        *(Affiche l'intégralité des tâches retournées par l'outil, triées par la date limite la plus proche)*

        #### 📢 Note de Suivi de Projet :
        [Rédige ici une seule phrase de synthèse managériale encourageante ou une alerte si des tâches urgentes sont en retard].
    """
    
    agent = create_agent(
        model=llm, 
        tools=planning_tools, 
        system_prompt=SYSTEM_PROMPT,
        debug=False,
    )
    
    # NOTE : Changement du test vers l'ID 1 pour passer le validateur applicatif d'existence
    requete_test = (
        "Pour le mariage ID 1, crée deux tâches prioritaires : "
        "1. 'Finaliser le choix du lieu' avec une date butoir au 2026-09-01. "
        "2. 'Envoyer les faire-part' avec une date butoir au 2026-12-15. "
        "Ensuite, affiche-moi le planning mis à jour pour vérifier que tout y est."
    )
    
    print(f"\n🚀 Lancement de l'Agent Planning :\n{requete_test}\n")
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n🎯 Rapport final de l'Agent Planning :\n")
    print(resultat["messages"][-1].content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_planning())