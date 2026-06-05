# src/agent.py
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver 
from langchain.agents import create_agent

from src.config import GOOGLE_API_KEY, GROQ_API_KEY
from src.schemas import RecipeResponse
from src.prompts import SYSTEM_PROMPT
from src.tools import get_tools # SearxNG / DuckDuckGo
import logging

logging.basicConfig(
    level=logging.INFO
)


class ChefAgentContext:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.llm = self._init_llm()
        
        # On remet ta mémoire / checkpointer ici pour qu'elle persiste par session
        self.memory = InMemorySaver() 
        
        # Variable temporaire pour stocker l'image de la requête en cours
        self.current_image_b64 = None 
        self.agent = self._build_agent()


    def _init_llm(self):
        """Factory pour interchanger le modèle choisi dans Gradio."""
        if self.model_name == "gemini-2.5-flash":
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3, google_api_key=GOOGLE_API_KEY)
        elif self.model_name == "llama-3.3-70b":
            return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3, api_key=GROQ_API_KEY)
        else:
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)

    def _vision_tool_execution(self, query: str = "") -> str:
        """La logique de ton sous-agent Vision encapsulée dans une fonction de Tool."""
        if not self.current_image_b64:
            return "Aucune photo n'a été partagée par l'utilisateur pour cette recette."
            
        # On utilise un modèle vision rapide pour l'extraction textuelle
        vision_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=GOOGLE_API_KEY)
        
        msg = HumanMessage(content=[
            {"type": "text", "text": "Return only a comma-separated list of ingredients. No explanations."},
            {"type": "image", "base64": self.current_image_b64, "mime_type": "image/png"}
        ])
        
        try:
            response = vision_llm.invoke([msg])
        except Exception:
            logging.exception("Vision failed")
            return ""
        
        return response.content

    def _build_agent(self):
        """On rassemble tes outils et on instancie EXACTEMENT ton create_agent d'origine."""
        # 1. Ton outil de recherche web (SearxNG ou DuckDuckGo)
        search_tools = get_tools()
        
        # 2. Ton sous-agent de vision transformé en Tool (Ton idée de génie)
        vision_tool = Tool(
            name="analyser_image_frigo",
            func=self._vision_tool_execution,
            description="Utile uniquement si l'utilisateur a chargé une photo. Cet outil extrait la liste textuelle des ingrédients présents sur l'image."
        )
        
        # Si search_tools est une liste, on utilise '+' pour fusionner les deux listes
        if isinstance(search_tools, list):
            tools = search_tools + [vision_tool]
        else:
            tools = [search_tools, vision_tool]
        
        # On recrée ton agent avec ta structure exacte
        agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=self.memory,
            response_format=RecipeResponse 
        )
        return agent

    def run(self, text_input: str, image_filepath: str = "", thread_id: str = "1"):
        """Méthode principale appelée par l'application."""
        # Si Gradio envoie une image, on la convertit en base64 pour notre outil interne
        if image_filepath:
            with open(image_filepath, "rb") as f:
                self.current_image_b64 = base64.b64encode(f.read()).decode("utf-8")
        else:
            self.current_image_b64 = None
        
        # Configuration de la session de rechargement (Mémoire)
        config = {"configurable": {"thread_id": thread_id}}
        
        # On prépare le message d'entrée de l'agent principal
        user_prompt = f"Ingrédients fournis textuellement : {text_input}."
        if image_filepath:
            user_prompt += " J'ai aussi déposé une image de mes ingrédients. Sers-toi de ton outil 'analyser_image_frigo' pour voir ce qu'il y a dedans."

        # Exécution de l'agent ReAct
        try:
            result = self.agent.invoke({"messages": [HumanMessage(content=user_prompt)]}, config=config)
        except Exception:
            logging.exception("Aggent failed")
            return []
        
        # On retourne la réponse finale (qui respectera le format RecipeResponse si configuré)
        return result["messages"]