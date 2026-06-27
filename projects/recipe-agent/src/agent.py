# src/agent.py
import base64
import logging
import sqlite3
from typing import Optional, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.config import GOOGLE_API_KEY, GROQ_API_KEY
from src.schemas import RecipeResponse, ChefState
from src.prompts import SYSTEM_PROMPT
from src.tools import get_tools # SearxNG / DuckDuckGo

logging.basicConfig(level=logging.INFO)


class ChefAgentGraph:
    def __init__(self, model_name: str, local_search = False,  db_path: str = "chef_memory.db"):
        self.db_path = db_path
        self.model_name = model_name
        self.llm = self._init_llm()
        self.local_search = local_search

        # Connexion SQLite persistante pour la mémoire de LangGraph
        conn = sqlite3.connect(db_path, check_same_thread=False)
        self.memory = SqliteSaver(conn)
        self._init_custom_db()

        self.search_tool = self._init_search_tool()
        self.graph = self._build_graph()
    
    def _init_custom_db(self):
        """Crée la table d'historique pour l'application Streamlit."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recipe_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT,
                    title TEXT,
                    match_score INTEGER,
                    temps_preparation INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _init_llm(self):
        """Initialise le LLM principal selon le choix de l'utilisateur."""
        if self.model_name == "gemini":
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, google_api_key=GOOGLE_API_KEY)
        return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, api_key=GROQ_API_KEY)

    def _init_search_tool(self):
        """Récupère le premier outil de recherche disponible (SearxNG ou DDG)."""
        tools = get_tools(self.local_search)
        return tools[0] if isinstance(tools, list) else tools
    
    # ------------------------------------------
    # NODES (Les étapes de ton pipeline)
    # ------------------------------------------
    def _extract_from_image_node(self, state: ChefState) -> Dict[str, Any]:
        """Étape 1 : Si une image est fournie, on extrait les ingrédients avec Gemini Vision."""
        if not state.get("image_filepath"):
            return {"extracted_ingredients": []}

        logging.info("📸 Analyse de l'image du frigo en cours...")
        try:
            with open(state["image_filepath"], "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")

            vision_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=GOOGLE_API_KEY)
            
            msg = HumanMessage(content=[
                {"type": "text", "text": "Liste uniquement les ingrédients visibles sur cette image, séparés par des virgules. Sois précis. Pas d'introduction ni de conclusion."},
                {"type": "image", "base64": b64_data, "mime_type": "image/png"}
            ])
            
            response = vision_llm.invoke([msg])
            ingredients = [i.strip() for i in response.content.split(",") if i.strip()]
            return {"extracted_ingredients": ingredients}
            
        except Exception:
            logging.exception("Erreur lors de l'analyse de l'image.")
            return {"extracted_ingredients": []}

    def _prepare_ingredients_node(self, state: ChefState) -> Dict[str, Any]:
        """Étape 2 : Fusionne le texte utilisateur et les ingrédients extraits de la photo."""
        text_ing = [i.strip() for i in state["text_input"].split(",") if i.strip()]
        img_ing = state.get("extracted_ingredients", [])
        
        # Union des deux listes pour éviter les doublons grossiers
        all_ingredients = list(set(text_ing + img_ing))
        logging.info(f"🥗 Ingrédients consolidés : {all_ingredients}")
        return {"all_ingredients": all_ingredients}

    def _search_online_node(self, state: ChefState) -> Dict[str, Any]:
        """Étape 3 : Recherche sur le web les meilleures recettes basées sur les ingrédients."""
        ingredients_str = ", ".join(state["all_ingredients"])
        query = f"recettes de cuisine avec ces ingrédients : {ingredients_str}"
        
        logging.info(f"🔍 Recherche web lancée : {query}")
        try:
            # Appel direct de l'outil (SearxNG ou DuckDuckGo)
            search_results = self.search_tool.invoke(query)
            return {"raw_search_results": str(search_results)}
        except Exception:
            logging.exception("Erreur lors de la recherche en ligne.")
            return {"raw_search_results": "Aucun résultat trouvé sur le web."}
        
    def _rank_and_format_node(self, state: ChefState) -> Dict[str, Any]:
        """Étape 4 : Sélectionne les 3 meilleures recettes, calcule leur score et applique le schéma Pydantic."""
        logging.info("🍳 Sélection, notation et structuration des 3 meilleures recettes...")
        
        # On force le LLM à répondre selon ton schéma Pydantic 'RecipeResponse'
        structured_llm = self.llm.with_structured_output(RecipeResponse)
        
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Ingrédients disponibles : {state['all_ingredients']}\n\n"
            f"Résultats de recherche web associés :\n{state['raw_search_results']}\n\n"
            "Mission :\n"
            "1. Analyse les résultats de recherche et sélectionne exactement les 3 meilleures recettes faisables.\n"
            "2. Pour chaque recette, calcule un score de correspondance (0 à 100) basé sur le ratio "
            "d'ingrédients possédés par l'utilisateur par rapport aux ingrédients requis par la recette.\n"
            "3. Génère la réponse en respectant strictement la structure demandée."
        )
        
        try:
            recipes_structured = structured_llm.invoke([HumanMessage(content=prompt)])
            return {"final_recipes": recipes_structured}
        except Exception:
            logging.exception("Erreur lors du formatage final.")
            return {"final_recipes": None}
        
    def _build_graph(self):
        builder = StateGraph(ChefState)

        # Ajout des nœuds
        builder.add_node("extract_image", self._extract_from_image_node)
        builder.add_node("prepare_ingredients", self._prepare_ingredients_node)
        builder.add_node("search_online", self._search_online_node)
        builder.add_node("rank_and_format", self._rank_and_format_node)

        # Définition des liens (Pipeline Linéaire et Propre)
        builder.add_edge(START, "extract_image")
        builder.add_edge("extract_image", "prepare_ingredients")
        builder.add_edge("prepare_ingredients", "search_online")
        builder.add_edge("search_online", "rank_and_format")
        builder.add_edge("rank_and_format", END)

        # Compilation avec sauvegarde de session (mémoire)
        return builder.compile(checkpointer=self.memory)
    
    def _save_recipes_to_stats(self, thread_id: str, recipes_response: Optional[RecipeResponse]):
        """Insère les recettes générées dans la table de statistiques."""
        if not recipes_response or not recipes_response.recipes:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for recipe in recipes_response.recipes:
                cursor.execute(
                    "INSERT INTO recipe_history (thread_id, title, match_score, temps_preparation) VALUES (?, ?, ?, ?)",
                    (thread_id, recipe.title, recipe.match_score, recipe.temps_preparation)
                )
            conn.commit()

    def format_to_markdown(self, recipe_response: Optional[RecipeResponse]) -> str:
        """Transforme l'objet Pydantic mis à jour en un beau Markdown pour Gradio."""
        if not recipe_response or not recipe_response.recipes:
            return "### ❌ Désolé, je n'ai pas pu générer ou structurer de recettes pour le moment."

        md = "# 🍳 Voici les 3 meilleures recettes sélectionnées :\n\n"
        for idx, recipe in enumerate(recipe_response.recipes, 1):
            md += f"## {idx}. {recipe.title}\n"
            md += f"⏱️ **Temps de préparation :** {recipe.temps_preparation} min | **🎯 Score :** {recipe.match_score}/100\n\n"
            md += f"> 💡 *{recipe.justification}*\n\n"
            
            # Ingrédients requis
            md += "### 🛒 Ingrédients nécessaires :\n"
            for ing in recipe.ingredients_required:
                md += f"- {ing}\n"
            
            # Gestion propre des ingrédients manquants
            md += "\n### ❌ À acheter / Ingrédients manquants :\n"
            if recipe.ingredients_manquant:
                for ing_males in recipe.ingredients_manquant:
                    qty_str = f" ({ing_males.quantity})" if ing_males.quantity else ""
                    md += f"- **{ing_males.name}**{qty_str}\n"
            else:
                md += "- *Aucun ! Vous avez déjà tout dans votre frigo !* 🎉\n"
            
            # Instructions
            md += "\n### 📝 Instructions de préparation :\n"
            for step_idx, step in enumerate(recipe.instructions, 1):
                md += f"{step_idx}. {step}\n"
            md += "\n" + "---" + "\n\n"
        
        return md

    # CONSTRUCTION DU GRAPH
    def run(self, text_input: str, image_filepath: str = None, thread_id: str = "1") -> str:
        """Point d'entrée principal qui retourne directement le Markdown prêt pour Gradio."""
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "text_input": text_input,
            "image_filepath": image_filepath,
            "extracted_ingredients": [],
            "all_ingredients": [],
            "raw_search_results": "",
            "final_recipes": None
        }
        
        # Le graphe s'exécute de manière linéaire
        final_state = self.graph.invoke(initial_state, config=config)
        recipes_data = final_state.get("final_recipes")

        # Sauvegarde asynchrone/directe dans tes stats avant de renvoyer le markdown
        self._save_recipes_to_stats(thread_id, recipes_data)

        # Conversion finale en Markdown textuel
        return self.format_to_markdown(final_state.get("final_recipes"))

    def get_graph_image(self) -> bytes:
        """Retourne l'image PNG du workflow LangGraph."""
        # draw_mermaid_png utilise un appel API vers mermaid.ink par défaut si pygraphviz n'est pas installé
        return self.graph.get_graph().draw_mermaid_png()