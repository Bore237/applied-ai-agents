import os
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_one_tools
from schemas.prompt import *
from schemas.config import ALL_SYSTEM_PROMPTS
from langchain_core.tools import StructuredTool
import json

async def executer_agent_planning(consigne: str) -> str:
    """Fonction maîtresse appelée par l'orchestrateur."""
    tools = await get_mcp_one_tools(name_tools='planning', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = ALL_SYSTEM_PROMPTS['planning'] #SYSTEM_PROMPT_PLANNING
    
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=consigne)]})
    return resultat["messages"][-1].content

async def executer_agent_budget(consigne: str) -> str:
    """Fonction maîtresse appelée par l'orchestrateur."""
    tools = await get_mcp_one_tools(name_tools='budget', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = ALL_SYSTEM_PROMPTS['budget'] #SYSTEM_PROMPT_BUDGET    
    
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=consigne)]})
    return resultat["messages"][-1].content

async def executer_agent_didier(consigne: str) -> str:
    """Fonction maîtresse appelée par l'orchestrateur."""
    tools = await get_mcp_one_tools(name_tools='didier', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = ALL_SYSTEM_PROMPTS['didier'] #SYSTEM_PROMPT_DIDIER    
    
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=consigne)]})
    return resultat["messages"][-1].content

def extract_json(raw):
    if isinstance(raw, str):
        return json.loads(raw)

    if isinstance(raw, list):
        # cas ToolMessage content=[{"text": "..."}]
        raw = raw[0]

    if isinstance(raw, dict) and "text" in raw:
        return json.loads(raw["text"])

    raise ValueError(f"Format Kiwi inattendu: {type(raw)}")


def filter_kiwi_payload(tool):
    if tool.name != "search-flight":
        return tool

    # 1. On définit la nouvelle logique asynchrone
    async def _wrapped_coroutine(**kwargs):
        # On appelle le tool MCP d'origine proprement via ainvoke
        raw_result = await tool.ainvoke(kwargs)
        
        try:
            flights = extract_json(raw_result)
            if not isinstance(flights, list) or len(flights) == 0:
                return {
                    "success": False,
                    "data": None,
                    "error": "Aucun vol trouvé"
                }
            
            # On extrait uniquement le premier vol (le meilleur)
            best = flights[0]

            return {
                "success": True,
                "data": {
                    "prix": best.get("price"),
                    "devise": best.get("currency", "EUR"),
                    "ville_depart": best.get("cityFrom"),
                    "ville_arrivee": best.get("cityTo"),
                    "duree_h": round(best.get("totalDurationInSeconds", 0) / 3600, 1),
                    "escales": len(best.get("layovers", []))
                },
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    # Fonction de repli obligatoire pour la signature synchrone de StructuredTool
    def _sync_fallback(*args, **kwargs):
        raise NotImplementedError("Ce wrapper supporte uniquement l'exécution asynchrone via ainvoke.")

    # On instancie un nouveau StructuredTool en conservant les métadonnées et le schéma d'origine
    return StructuredTool(
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        coroutine=_wrapped_coroutine,
        func=_sync_fallback
    )


async def executer_agent_flight(consigne: str) -> str:
    """Fonction maîtresse appelée par l'orchestrateur."""
    tools = await get_mcp_one_tools(name_tools='flight', timeout=30)
    tools = [filter_kiwi_payload(t) for t in tools]

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = ALL_SYSTEM_PROMPTS['flight'] #SYSTEM_PROMPT_FLIGHT    
    
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=consigne)]})
    return resultat["messages"][-1].content

async def executer_agent_invites(consigne: str) -> str:
    """Fonction maîtresse appelée par l'orchestrateur."""
    tools = await get_mcp_one_tools(name_tools='invites', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = ALL_SYSTEM_PROMPTS['invites']  #SYSTEM_PROMPT_INVITES    
    
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=consigne)]})
    return resultat["messages"][-1].content

async def executer_agent_lieux(consigne: str) -> str:
    """Fonction maîtresse appelée par l'orchestrateur."""
    tools = await get_mcp_one_tools(name_tools='lieux', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = ALL_SYSTEM_PROMPTS['lieux']  #SYSTEM_PROMPT_LIEUX    
    
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=consigne)]})
    return resultat["messages"][-1].content

async def executer_agent_traiteur(consigne: str) -> str:
    """Fonction maîtresse appelée par l'orchestrateur."""
    tools = await get_mcp_one_tools(name_tools='traiteur', timeout=30)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    SYSTEM_PROMPT = ALL_SYSTEM_PROMPTS['traiteur']  #SYSTEM_PROMPT_TRAITEUR 
    
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=consigne)]})
    return resultat["messages"][-1].content