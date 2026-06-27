import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
# from lanchain.agents.middleware import , before_agent, dynamic_prompt, wrap_model_call, ModelRequest, ModelResponse
from langchain.agents.middleware import HumanInTheLoopMiddleware, SummarizationMiddleware #approving rejecting or editing
from tools.agent_tools.mcp_tools import get_mcp_tools

load_dotenv()

SYSTEM_PROMPT_LONG = """Tu es un assistant de gestion d'e-mails autonome et extrêmement rigoureux.
Ton objectif est d'accomplir les tâches demandées par l'utilisateur en utilisant les outils fournis.

RÈGLES D'EXÉCUTION STRICTES :
1. RECHERCHE OBLIGATOIRE : Ne devine jamais un 'msg_id' ou une adresse e-mail. Tu dois TOUJOURS utiliser 'Gmail-Search-Emails' en premier pour trouver l'ID précis d'un e-mail avant d'utiliser des outils comme 'Get-Email-Message-Body' ou 'Gmail-Delete-Email'.
2. VÉRIFICATION AVANT ACTION : Avant de supprimer ou d'envoyer un e-mail, assure-toi d'avoir toutes les informations nécessaires.
3. GESTION DES ERREURS : Si un outil te renvoie une erreur ou un résultat vide, NE RÉPÈTE PAS la même action arrête-toi et explique.
4. UNE SEULE ÉTAPE À LA FOIS : Analyse le résultat du dernier outil avant de décider de la prochaine action.
5. FIN DE TÂCHE : Dès que l'objectif de l'utilisateur est atteint, arrête d'appeler des outils et génère ta réponse finale pour confirmer l'action.

Règle absolue : Si tu te retrouves à utiliser le même outil avec les mêmes arguments deux fois de suite sans succès, tu dois t'arrêter et demander des précisions à l'utilisateur.
"""

SYSTEM_PROMPT = """
    Tu es un assistant Gmail.

    Règles importantes :

    - Utilise un outil uniquement lorsqu'il est indispensable pour répondre.
    - N'appelle jamais deux fois le même outil avec exactement les mêmes paramètres.
    - Si un outil fournit déjà l'information nécessaire, ne le rappelle pas.
    - Une fois l'action demandée terminée, réponds immédiatement à l'utilisateur.
    - Ne vérifie pas plusieurs fois qu'une action a réussi sauf si l'utilisateur le demande.
    - Si aucune information supplémentaire ne peut être obtenue, arrête-toi et réponds.
    - Si un outil retourne une erreur, explique-la. N'essaie pas indéfiniment.
"""
async def init_agent_system():  
    """Initialise les outils MCP, le LLM et l'agent avec son middleware HITL."""
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    summarizer_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    memory = InMemorySaver()
    tools =  await  get_mcp_tools()
    #print(f"Outils chargés avec succès : {[t.name for t in tools]}")
    
    # Configuration du Middleware de Résumé
    summarize_middleware = SummarizationMiddleware(
        model=summarizer_llm,
        trigger=("messages", 6), 
        keep=("messages", 1)   
    )
    
    # Configuration du middleware HITL (Intervention Humaine)
    hitl_middleware = HumanInTheLoopMiddleware(
        interrupt_on={
            "Gmail-Send-Email": {"allowed_decisions": ["approve", "reject"]},
            "Gmail-Delete-Email-Message": {"allowed_decisions": ["approve", "reject"]}
        }
    )

    agent_executor = create_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        middleware=[hitl_middleware, summarize_middleware],
        system_prompt=SYSTEM_PROMPT
    )

    return agent_executor

if __name__ == "__main__":
    asyncio.run(init_agent_system())