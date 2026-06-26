# app.py
import streamlit as st
import pandas as pd
import sqlite3
import os
import uuid
from src.agent import ChefAgentGraph

# Configuration de la page
st.set_page_config(page_title="Chef AI Dashboard", layout="wide", page_icon="🍳")

# Variables de session cruciales pour le cycle de vie de Streamlit
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())  # ID unique de session pour SQLite

if "messages" not in st.session_state:
    st.session_state.messages = []  # Historique visuel du chat

DB_PATH = "chef_memory.db"

# ==========================================
# SIDEBAR : CONFIGURATION & STATISTIQUES
# ==========================================
with st.sidebar:
    st.title("⚙️ Configuration du Chef")
    
    # 1. Sélections utilisateur
    model_choice = st.selectbox(
        "Modèle de langage :", 
        ["gemini-2.5-flash", "llama-3.3-70b"],
        index=0
    )
    
    search_mode = st.toggle(
        "Activer la recherche locale uniquement", 
        value=False,
        help="Si activé, l'agent n'interrogera pas le web et utilisera son catalogue local."
    )
    
    # Bouton de réinitialisation de la session en cours
    if st.button("🔄 Nouvelle discussion", width="stretch"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.title("📊 Statistiques de l'application")
    
    # 2. Lecture et affichage des statistiques récoltées en base de données
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query("SELECT * FROM recipe_history ORDER BY created_at DESC", conn)
        
        if not df.empty:
            col1, col2 = st.columns(2)
            col1.metric("Total Recettes", len(df))
            col2.metric("Score Moyen", f"{int(df['match_score'].mean())}%")
            
            st.subheader("⏱️ Temps de préparation (Derniers repas)")
            # Graphique des temps de préparation des 5 dernières recettes générées
            st.bar_chart(df.head(5).set_index('title')['temps_preparation'])
            
            st.subheader("📜 Historique Récent")
            st.dataframe(df[['title', 'match_score']].head(5), width='stretch', hide_index=True)
        else:
            st.info("Aucune donnée statistique pour le moment.")
    except Exception:
        st.info("En attente de la première génération de recette...")

    st.markdown("---")
    
    # 3. Visualisation de l'architecture du graphe LangGraph
    with st.expander("👁️ Voir l'architecture de l'agent"):
        try:
            # On instancie un agent temporaire juste pour dessiner le graphe actuel
            temp_agent = ChefAgentGraph(model_name=model_choice, local_search=search_mode, db_path=DB_PATH)
            st.image(temp_agent.get_graph_image(), width="stretch")
        except Exception:
            st.caption("Le rendu visuel du graphe nécessite une connexion internet ou les dépendances Mermaid.")

# ==========================================
# ZONE PRINCIPALE : LE CHAT COMPORTANT TEXTE & IMAGE
# ==========================================
st.title("🍳 Assistant Culinaire Intelligent")
st.write(f"*(ID de session active : `{st.session_state.thread_id}`)*")

# Affichage des anciens messages de la session en cours
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone d'envoi d'image (Frigo / Ingrédients sur table)
uploaded_file = st.file_uploader("📸 Ajouter une photo de votre frigo ou d'ingrédients :", type=["png", "jpg", "jpeg"])
    
# Input de texte principal
if user_text := st.chat_input("Ex: J'ai des tomates, des oeufs et du fromage. Que puis-je faire ?"):

    # Affichage immédiat du message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(user_text)
    st.session_state.messages.append({"role": "user", "content": user_text})
    
    # Traitement de l'image si elle est présente
    temp_image_path = None
    if uploaded_file is not None:
        os.makedirs("temp", exist_ok=True)
        temp_image_path = os.path.join("temp", uploaded_file.name)
        # CORRECTION ICI : on utilise .write() pour enregistrer l'image de Gradio/Streamlit
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_file.getvalue())
            
    # Chargement dynamique de l'agent configuré via la Sidebar
    agent = ChefAgentGraph(model_name=model_choice, local_search=search_mode, db_path=DB_PATH)
    
    # Animation de chargement pendant l'exécution
    with st.chat_message("assistant"):
        with st.spinner("Le Chef réfléchit... (Vision ➔ Recherche ➔ Scoring)"):
            response_markdown = agent.run(
                text_input=user_text,
                image_filepath=temp_image_path,
                thread_id=st.session_state.thread_id
            )
            st.markdown(response_markdown)

    # Chargement dynamique de l'agent configuré via la Sidebar
    agent = ChefAgentGraph(model_name=model_choice, local_search=search_mode, db_path=DB_PATH)
    
    # Animation de chargement pendant l'exécution linéaire de LangGraph
    with st.chat_message("assistant"):
        with st.spinner("Le Chef réfléchit... (Vision ➔ Recherche ➔ Scoring)"):
            response_markdown = agent.run(
                text_input=user_text,
                image_filepath=temp_image_path,
                thread_id=st.session_state.thread_id
            )
            st.markdown(response_markdown)
            
    # Enregistrement de la réponse du bot dans l'historique de session
    st.session_state.messages.append({"role": "assistant", "content": response_markdown})
    
    # Nettoyage du fichier temporaire d'image après exécution
    if temp_image_path and os.path.exists(temp_image_path):
        os.remove(temp_image_path)
        
    # Rerun forcé pour rafraîchir instantanément le tableau de bord des statistiques à gauche
    st.rerun()