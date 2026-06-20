import asyncio
import os
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from dotenv import load_dotenv
from tools.agent_tools import *
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential
import json

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

# --- TRANSFORMATION DES AGENTS EN TOOLS ---
GROQ_MODELS = {
    "fast": "llama-3.1-8b-instant",
    "balanced": "llama-3.3-70b-versatile",
    "reasoning": "qwen/qwen3-32b",
    "strong_reasoning": "openai/gpt-oss-120b",
    "deepseek": "deepseek-r1-distill-qwen-32b",
}

USE_GEMINI = True
outils_orchestrateur = [
    outil_agent_planning,
    outil_agent_budget,
    outil_agent_invites,
    outil_agent_flight,
    outil_agent_didier,
    outil_agent_lieux,
    outil_agent_traiteur
]

def extraire_texte_propre(content) -> str:
    """Extrait et rassemble uniquement le texte lisible d'un message LangChain."""
    if isinstance(content, str):
        return content
    
    if isinstance(content, list):
        morceaux = []
        for bloc in content:
            if isinstance(bloc, str):
                morceaux.append(bloc)
            elif isinstance(bloc, dict) and "text" in bloc:
                morceaux.append(bloc["text"])
        return "".join(morceaux)
    
    return str(content)

# --- INITIALISATION DE L'ORCHESTRATEUR ---
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
)
async def agent_orchestrateur():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : 'GROQ_API_KEY' manquante.")
        return
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ Erreur : 'GOOGLE_API_KEY' manquante.")
        return

    # On utilise un modèle performant pour l'orchestration (Llama 3.1 70b ou équivalent si nécessaire)
    if USE_GEMINI:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            streaming=True,
        )
    else:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            streaming=True,
        )
    SYSTEM_PROMPT = SYSTEM_PROMPT_ORCHESTRATEUR

    manager = create_agent(
        model=llm, 
        tools=outils_orchestrateur, 
        system_prompt=SYSTEM_PROMPT,
        debug=False # Très utile ici pour voir le manager dispatcher le travail
    )
    
    # SCÉNARIO DE TEST MULTI-AGENTS (Requête croisée)
    requete_complexe = {
        "name": "Scénario 1: Mariage champêtre en Provence",
        "scenario": {
            "mariage_id": 1,
            "nombre_invites": 80,
            "budget": 18000,
            "ville_residence": "Paris",
            "lieu_cible": "Provence",
            "style_menu": "gourmet",
            "date_mariage": "2026-10-25"
        },
        "steps": [
            "Importe une liste de 80 invités (mix: 40 de Île-de-France, 30 de Lyon, 10 locaux)",
            "Récupère les besoins de vols (estimation pour vols Paris → Nice)",
            "Cherche un domaine en Provence (capacité 80+, ambiance champêtre)",
            "Réserve le lieu et vérifie l'impact budgétaire",
            "Propose un menu gourmet (80 personnes)",
            "Ajoute une sélection de musique romantique pour le dîner",
            "Crée le planning avec tâches critiques"
        ]
    }
    
    content_str = json.dumps(requete_complexe)
    print(f"\n🚀 Lancement de l'Orchestrateur Principal...")
    resultat = await manager.ainvoke({"messages": [HumanMessage(content=content_str)]})
    
    print("\n🎯 Réponse Finale de l'Orchestrateur aux Mariés :\n")
    texte_propre = extraire_texte_propre(resultat["messages"][-1].content)
    print(texte_propre, '\n')

if __name__ == "__main__":
    asyncio.run(agent_orchestrateur())