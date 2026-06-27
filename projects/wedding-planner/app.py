# app.py
import streamlit as st
import asyncio
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.agent_tools import *
from servers.server import db

load_dotenv(r"D:\marchine_learning\Agent_course\agentic-labs\.env.key")

# Configuration de la page
st.set_page_config(page_title="Wedding AI OS", layout="wide", page_icon="💍")

def extract_reply(msg):
    # Si le message contient un appel d'outil et pas de texte
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        tool_name = msg.tool_calls[0]['name']
        return f"🤖 *L'orchestrateur fait appel à l'agent expert : `{tool_name}`...*"
    
    content = msg.content
    if isinstance(content, list):
        return content[0].get("text", "")
    return content
# ========================================================
# 1. FONCTIONS DE RÉCUPÉRATION DES DONNÉES (TABLEAU DE BORD)
# ========================================================
def charger_mariages():
    """
    Récupère tous les mariages disponibles
    """
    res = db.read_param("""SELECT id, nom_code, date_evenement FROM mariages ORDER BY id""")
    if res["ok"]:
        return res["data"]

    return []

def charger_metriques_mariage(mariage_id=1):
    """Va chercher les vraies infos en BDD pour l'affichage visuel"""
    # Budget
    res_bMax = db.read_param("SELECT budget_max FROM mariages WHERE id = ?", (mariage_id,))
    res_bSum = db.read_param("SELECT SUM(montant_estime) FROM budget_depenses WHERE mariage_id = ?", (mariage_id,))
    b_max = res_bMax["data"][0][0] if res_bMax["ok"] and res_bMax["data"] else 50000.0
    b_spent = res_bSum["data"][0][0] if res_bSum["ok"] and res_bSum["data"][0][0] else 0.0
    
    # Invités
    res_inv = db.read_param("SELECT COUNT(*) FROM invites WHERE mariage_id = ? AND statut_rsvp != 'Decline'", (mariage_id,))
    total_inv = res_inv["data"][0][0] if res_inv["ok"] else 0
    
    # Tâches
    res_taches = db.read_param("SELECT titre, date_limite  FROM taches_planning WHERE mariage_id = ? AND statut = 'A_Faire' LIMIT 3", (mariage_id,))
    taches = res_taches["data"] if res_taches["ok"] else []
    
    return b_max, b_spent, total_inv, taches

# ========================================================
# 2. INITIALISATION DE L'AGENT SUPERVISEUR
# ========================================================
def obtenir_superviseur(use_gemini=True):
    """Instancie le cerveau central du réseau d'agents"""
    boite_outils = [outil_agent_planning, outil_agent_budget, outil_agent_invites,
    outil_agent_flight, outil_agent_didier, outil_agent_lieux, outil_agent_traiteur]
    # On utilise un modèle performant pour l'orchestration (Llama 3.1 70b ou équivalent si nécessaire)
    if use_gemini:
        llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0, streaming=True)
    else:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, streaming=True)
    
    return create_agent(model=llm, tools=boite_outils, system_prompt=SYSTEM_PROMPT_ORCHESTRATEUR, debug=True)

# Initialisation de l'historique du chat dans la session Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Je suis votre Assitant IA de Mariage. Que faisons-nous aujourd'hui ?"}]

if "use_gemini" not in st.session_state:
    st.session_state.use_gemini = True

# ========================================================
# 3. DESSIN DE L'INTERFACE GRAPHIQUE (SPLIT-SCREEN)
# ========================================================
st.title("💍 Wedding AI OS")
st.caption("Centre de Commandement Multi-Agents")
st.divider()

# Création des deux colonnes (Gauche: 28% de largeur, Droite: 78%)
col_dashboard, col_chat = st.columns([28, 78])

# ---- COLONNE GAUCHE : LE TABLEAU DE BORD EN TEMPS RÉEL ----
with col_dashboard:
    st.header(f"📊 Board du Mariage")
    with st.container(border=True):
        mariages = charger_mariages()
        if not mariages:
            st.error("Aucun mariage trouvé.")
            st.stop()

        options = {f"Mariage #{m[0]} - {m[1]} ({m[2]})": m[0] for m in mariages}
        mariage_selectionne = st.selectbox("Choisir un mariage", list(options.keys()))
        mariage_id = options[mariage_selectionne]
    
    ##########---------------------------- Chargement des données --------------
    b_max, b_spent, total_inv, taches = charger_metriques_mariage(mariage_id)
    solde = b_max - b_spent
    
    #########################-----------------  Affichage des KPIs ---------------------------
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        with st.container(border=True):
            st.metric(label="👥 Invités ", value=f"{total_inv} personnes")
        with kpi2:
            with st.container(border=True):
                st.metric( "💰 Restant", f"{solde:,.1f} €" )
    
    ##################----------------------- Taches ----------------------------------------
    with st.container(border=True):
        st.subheader("💰 Suivi du Budget")
        budget_pct = ( b_spent / b_max if b_max > 0 else 0 )
        st.progress( min(float(budget_pct), 1.0) )
        st.caption( f"{b_spent:,.0f} € utilisés sur {b_max:,.0f} €" )
        # col_b1, col_b2 = st.columns(2)
        # col_b1.metric(label="Total Engagé", value=f"{b_spent:,.2f} €")
        # col_b2.metric(label="Reste à Vivre", value=f"{solde:,.2f} €", delta=f"Budget Max: {b_max}€", delta_color="normal" if solde >= 0 else "inverse")
    
    if solde < 0:
        st.error("⚠️ Budget dépassé !")
    
    ##################----------------------- Taches -----------------
    with st.container(border=True):
        with st.expander("📅 Prochaines tâches"):
            if taches:
                for titre, date_limite in taches:
                    st.info(f"📌 **{titre}** \n(Avant le : {date_limite})")
            else:
                st.success("🎉 Aucune tâche urgente! Le planning est à jour.")

# ---- COLONNE DROITE : LE CHAT EN DIRECT AVEC LE SUPERVISEUR ----
with col_chat:
    top_left, top_right = st.columns([8, 2])

    with top_left:
        st.header("💬 Wedding AI Assistant")
    
    with top_right:
        modele_choisi = st.selectbox("Modèle IA", ["Gemini", "Llama"], label_visibility="collapsed")
    st.session_state.use_gemini = (modele_choisi == "Gemini")
    st.divider()

#########--------------------------- Zone de chats --------------------------------------------
    # Zone de défilement des anciens messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Entrée utilisateur
    if prompt := st.chat_input("Ex: Ajoute l'invité Marc (marc@email.com, Lyon, vol: oui) et regarde si on a le budget."):
        # 1. On affiche le message du marié
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 2. On appelle le Superviseur
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*L'Orchestrateur consulte les agents experts...*")
            
            # Appel asynchrone encapsulé du master agent
            superviseur = obtenir_superviseur(use_gemini=st.session_state.use_gemini)
            try:
                response = asyncio.run(superviseur.ainvoke({"messages": [HumanMessage(content=prompt)]}))
                reply = extract_reply(response["messages"][-1])
            except Exception as e:
                reply = f"❌ Une erreur est survenue lors de la coordination des agents : {str(e)}"
                
            # 3. Rendu de la réponse et sauvegarde
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            # Relance un rafraîchissement global de la page pour mettre à jour la colonne de gauche !
            st.rerun()