import os
from langchain_community.utilities import SearxSearchWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool
from src.config import SEARX_HOST

def get_tools():
    # Si on détecte qu'on tourne sur Hugging Face (ou si SEARX_HOST n'est pas local)
    if os.getenv("HF_SPACE_ID") or os.getenv("SEARX_HOST") is None:
        # On utilise le wrapper gratuit DuckDuckGo en prod
        ddg_search = DuckDuckGoSearchRun()
        return [
            Tool(
                name="recherche",
                func=ddg_search.run,
                description="Utile pour chercher des recettes de cuisine et des associations d'ingrédients."
            )
        ]
    else:
        # On garde ton SearxNG local pour tes tests chez toi
        search = SearxSearchWrapper(
            searx_host=SEARX_HOST,
            engines=["google", "wikipedia"],
            k=2,
            query_suffix="recipe -video -youtube -forum -reddit ingredients cooking instructions"
        )
        return [
            Tool(
                name="recherche",
                func=search.run,
                description="Utile pour valider des faits ou chercher des recettes."
            )
        ]