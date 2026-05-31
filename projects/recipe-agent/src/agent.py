from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent # Ou ta fonction 'create_agent' personnalisée

from src.config import GOOGLE_API_KEY, GROQ_API_KEY
from src.prompts import SYSTEM_PROMPT
from src.tools import get_tools

def init_chef_agent():
    # Initialisation du LLM avec support du streaming
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY,
        streaming=True
    )

    llm = llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.3,
        streaming=True
    )

    tools = get_tools()
    memory = InMemorySaver()

    # Création de l'agent orchestré
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    return agent