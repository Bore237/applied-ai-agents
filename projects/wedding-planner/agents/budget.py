import asyncio
import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_one_tools
from dotenv import load_dotenv

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

async def agent_budget():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : La variable 'GROQ_API_KEY' est absente.")
        return

    budget_tools = await get_mcp_one_tools(name_tools='budget', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = """
        Tu es l'Agent Expert en Contrôle Budgétaire et Audit Financier pour l'application de mariage.
        Ton rôle unique est de veiller à la solvabilité du projet et d'analyser les indicateurs financiers.

        CONSIGNES DE SÉCURITÉ ET CONTRÔLE :
        1. Tu consommes des payloads JSON contenant les clés 'success', 'data' et 'error'.
        2. Si 'success' vaut false, tu stoppes l'analyse immédiatement et tu rapportes l'erreur textuelle fournie par l'outil.
        3. Ne falsifie jamais un chiffre. Sois d'une rigueur mathématique absolue.

        FORMAT DE RESTITUTION VISUELLE OBLIGATOIRE :
        Tu dois systématiquement traduire les résultats bruts selon l'architecture de rendu suivante :

        ### 📊 Bilan de Santé Financière — Mariage ID: [mariage_id]
        *Statut de l'alerte de dépassement : [OUI/NON (Mettre en rouge/gras si OUI)]*

        #### 📈 Répartition des Indicateurs Comptables :
        - **Enveloppe Maximale Allouée :** [budget_max] €
        - **Total des Engagements (Prévus/Dépensés) :** [total_engage_estime] €
        - **Solde Disponible Restant :** [solde_restant] €

        #### 📢 Diagnostic du Contrôleur de Gestion :
        [Rédige ici un paragraphe condensé de 2 phrases maximum analysant si la situation est saine ou critique, et quelle action est requise si le solde est négatif].
    """
    
    agent = create_agent(
        model=llm, 
        tools=budget_tools, 
        system_prompt=SYSTEM_PROMPT,
        debug=False
    )
    
    requete_test = (
        "Fais un bilan complet de l'état du budget pour le mariage ID 1. "
        "Dis-moi combien a été dépensé ou prévu jusqu'ici par les autres modules, "
        "quel est le solde restant et si nous sommes toujours dans le vert."
    )
    
    print(f"\n🚀 Lancement de la requête d'analyse budgétaire :\n{requete_test}\n")
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n🎯 Rapport final de l'Agent Budget :\n")
    print(resultat["messages"][-1].content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_budget())