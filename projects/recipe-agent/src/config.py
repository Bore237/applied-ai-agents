import os
from dotenv import load_dotenv

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Si tu restes sur SearxNG, configure l'URL via une variable d'environnement
SEARX_HOST = os.getenv("SEARX_HOST", "http://localhost:8080")