import asyncio
import os
from datetime import datetime  
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.mcp_tools import get_mcp_one_tools
from dotenv import load_dotenv
import json

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

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

    # 2. On instancie un nouveau StructuredTool en conservant les métadonnées et le schéma d'origine
    return StructuredTool(
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        coroutine=_wrapped_coroutine,
        func=_sync_fallback
    )
    

async def agent_flight():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Erreur : La variable d'environnement 'GROQ_API_KEY' n'est pas configurée.")
        return

    transport_tools = await get_mcp_one_tools(name_tools='flight', timeout=120)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    # 2. Récupérez la date du jour au format attendu par votre outil (JJ/MM/AAAA)
    date_aujourdhui = datetime.now().strftime("%d/%m/%Y")
    
    # 3. Injectez-la directement dans le prompt système
    SYSTEM_PROMPT = f"""Tu es l'Agent Expert en Logistique et Transports Aériens pour l'application de mariage.
        Ton but est de vérifier si un déplacement est nécessaire pour les mariés et d'estimer les coûts de transport.
        
        ATTENTION : La date d'aujourd'hui est le {date_aujourdhui}. 
        Pour toute recherche de vol, tu DOIS impérativement choisir des dates futures par rapport à aujourd'hui (par exemple, dans quelques mois).
        
        Procédure stricte à suivre :
        1. Utilise l'outil 'recuperer_villes_mariage' pour connaître la ville d'origine et la ville de destination.
        2. Si les deux villes sont identiques, s'arrêter et informer qu'aucun vol n'est nécessaire.
        3. Si les villes sont différentes, utilise les outils de vol (comme ceux de Kiwi.com) pour chercher un itinéraire.
        4. Calcule le coût total pour les mariés (2 billets) et estime le temps de trajet.
        5. Enregistre le résultat final en utilisant l'outil 'enregistrer_frais_transport'.
        
        FORMAT DE RAPPORT EXIGÉ (TRÈS IMPORTANT) :
        Dans ton message final, tu ne dois PAS te contenter de dire que le workflow a réussi. 
        Tu DOIS impérativement afficher un rapport structuré avec les données exactes récupérées :
        
        ### ✈️ Détails Logistiques du Vol
        - **Itinéraire :** [Ville Départ] -> [Ville Arrivée]
        - **Durée du trajet :** [X] heures
        - **Nombre d'escales :** [X] escale(s)
        
        ### 💰 Calcul du Budget (2 Billets)
        - **Prix unitaire :** [X] [Devise]
        - **Coût Total (2 passagers) :** [Calcul du prix x 2] [Devise]
        - **Statut de l'enregistrement :** Confirmé en base de données via 'enregistrer_frais_transport'.
        
        Si un tool retourne '"ok": false', tu dois arrêter immédiatement le workflow, expliquer l'erreur constatée et ne jamais appeler le tool d'enregistrement."""
    
    safe_tools = [filter_kiwi_payload(t) for t in transport_tools]

    agent = create_agent(
        model=llm, 
        tools=safe_tools, 
        system_prompt=SYSTEM_PROMPT,
        debug=True,
    )
    
    requete_test = (
        "Vérifie la logistique de transport pour le mariage ID 1. "
        "Si un voyage est nécessaire, cherche un vol adapté sur Kiwi, "
        "calcule le prix pour 2 billets et enregistre les dépenses."
    )
    
    print(f"\n🚀 Lancement de la requête logistique :\n{requete_test}\n")
    resultat = await agent.ainvoke({"messages": [HumanMessage(content=requete_test)]})
    
    print("\n \n🎯 Rapport final de l'Agent Flight :\n")
    final_message = resultat["messages"][-1]
    print(final_message.content, '\n')

if __name__ == "__main__":
    asyncio.run(agent_flight())