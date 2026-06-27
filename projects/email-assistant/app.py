# app.py
import streamlit as st
import asyncio
from langgraph.types import Command
from agent_core import init_agent_system

st.set_page_config(page_title="MCP Email Assistant", page_icon="✉️", layout="centered") #wide
st.title("✉️ MCP Email Assistant AI (avec HITL)")

# --- CONFIGURATION DU THREAD ET DE L'AGENT ---
THREAD_ID = "streamlit_session_v1"
config = {"configurable": {"thread_id": THREAD_ID}}

# Initialisation asynchrone de l'agent dans le session_state si non présent
if "agent" not in st.session_state:
    with st.spinner("Connexion au serveur MCP et initialisation de l'agent..."):
        # Astuce pour faire tourner de l'async au démarrage de Streamlit
        st.session_state.agent = asyncio.run(init_agent_system())
    st.session_state.messages = []
    st.session_state.awaiting_approval = False

agent = st.session_state.agent

# --- AFFICHAGE DE L'HISTORIQUE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- VÉRIFICATION DE L'ÉTAT DU GRAPHE ---
# On regarde si le graphe est actuellement en pause (HITL)
current_state = asyncio.run(agent.aget_state(config))
is_paused = bool(current_state.next)

# --- CAS 1 : L'AGENT REQUIERT UNE VALIDATION HUMAINE ---
if is_paused:
    st.warning("⚠️ **Action critique détectée :** L'agent souhaite exécuter un outil sensible.")
    
    # 1. On récupère le dernier message et on compte le NOMBRE RÉEL d'appels d'outils
    last_messages = current_state.values.get("messages", [])
    num_tool_calls = 1  # Sécurité par défaut
    
    if last_messages:
        last_agent_msg = last_messages[-1]
        st.info(f"**Intention de l'agent :**\n{last_agent_msg.content}")
        
        # On extrait les tool_calls s'ils existent
        tool_calls = getattr(last_agent_msg, "tool_calls", [])
        if tool_calls:
            num_tool_calls = len(tool_calls)
            st.caption(f"🔧 _Nombre d'actions en parallèle à valider : {num_tool_calls}_")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🟢 Approuver l'action", use_container_width=True):
            with st.spinner("Exécution approuvée..."):
                # Dynamisation : on crée autant de décisions d'approbation qu'il y a de tool_calls
                decisions = [{"type": "approve"} for _ in range(num_tool_calls)]
                
                res = asyncio.run(agent.ainvoke(
                    Command(resume={"decisions": decisions}), 
                    config=config
                ))
                st.session_state.messages.append({"role": "assistant", "content": res["messages"][-1].content})
            st.rerun()
            
    with col2:
        if st.button("🔴 Refuser l'action", use_container_width=True):
            with st.spinner("Exécution annulée..."):
                # Dynamisation : on crée autant de décisions de rejet qu'il y a de tool_calls
                decisions = [
                    {"type": "reject", "message": "L'utilisateur a annulé l'action."} 
                    for _ in range(num_tool_calls)
                ]
                
                res = asyncio.run(agent.ainvoke(
                    Command(resume={"decisions": decisions}), 
                    config=config
                ))
                st.session_state.messages.append({"role": "assistant", "content": res["messages"][-1].content})
            st.rerun()
            
# --- CAS 2 : DISCUSSION CLASSIQUE ---
else:
    if user_input := st.chat_input("Demandez-moi de lister, chercher ou envoyer un e-mail..."):
        # Affichage immédiat du message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        # Lancement de l'agent
        with st.chat_message("assistant"):
            with st.spinner("L'agent réfléchit..."):
                response = asyncio.run(agent.ainvoke({"messages": [("user", user_input)]}, config=config))
                
                # On revérifie l'état immédiatement après l'exécution
                check_state = asyncio.run(agent.aget_state(config))
                
                if check_state.next:
                    st.rerun()  # On force le re-render pour afficher les boutons HITL
                else:
                    content = response["messages"][-1].content
                    st.markdown(content)
                    st.session_state.messages.append({"role": "assistant", "content": content})