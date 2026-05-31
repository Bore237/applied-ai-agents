from langchain_community.utilities import SearxSearchWrapper
from langchain_core.tools import Tool
from src.config import SEARX_HOST

def get_tools():
    search = SearxSearchWrapper(
        searx_host=SEARX_HOST,
        engines=["google", "wikipedia"],
        k=2,
        query_suffix="recipe -video -youtube -forum -reddit ingredients cooking instructions"
    )
    
    web_search_tool = Tool(
        name="recherche",
        func=search.run,
        description="Utile pour chercher des recettes et valider des ingrédients."
    )
    
    return [web_search_tool]