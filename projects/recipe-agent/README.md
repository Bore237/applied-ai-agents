# 🥗 Chef AI Dashboard – Assistant Culinaire Intelligent & Agentic Workflow

Bienvenue dans **Chef AI Dashboard**, une application de production combinant la puissance des architectures d'agents décisionnels (**LangGraph**) et une interface analytique moderne (**Streamlit**). 

L'objectif de ce projet est de transformer un frigo ou une liste d'ingrédients en suggestions de recettes optimales, notées et structurées, tout en offrant un suivi analytique en temps réel.

---

## Fonctionnalités Clés & Richesse Technique

Ce projet dépasse le simple cadre d'un chatbot classique en intégrant des concepts avancés d'ingénierie IA :

* **Pipeline Déterministe (LangGraph DAG) :** Remplacement des agents ReAct imprévisibles par un graphe orienté acyclique strict. Le processus est linéaire, prévisible et garantit l'appel unique des outils (pas de boucle infinie de consommation d'API).
* **Analyse Multi-Modale (Vision) :** Intégration de *Gemini 2.5 Flash* pour extraire textuellement les ingrédients à partir d'une simple photo du frigo.
* **Dual-Persistence SQLite :** Une seule base de données pour deux usages distincts :
    1.  La persistance des sessions (historique de chat de LangGraph via `SqliteSaver`).
    2.  L'extraction de métriques métier (table `recipe_history` dédiée aux statistiques).
* **Génération Structurée Réellement Typée :** Utilisation de `.with_structured_output()` adossé à un schéma **Pydantic** complexe (gestion imbriquée des ingrédients manquants et validation des types).
* **Dashboard Analytique :** Sidebar Streamlit calculant dynamiquement les scores moyens de correspondance et affichant des graphiques de temps de préparation (Pandas + Streamlit Charts).

---

## 📊 Aperçu de l'Interface

Voici à quoi ressemble l'application en cours d'utilisation (Chat intelligent à droite, statistiques persistantes et architecture de l'agent à gauche) :

![Aperçu de l'interface Streamlit](assets\interface.png)

---

## Architecture du Graphe

L'agent est orchestré selon le flux de travail rigoureux suivant :

```text
              START 
                │
                ▼
        📸 [extract_image]        <-- Analyse de la photo si fournie
                │
                ▼
        🥗 [prepare_ingredients]  <-- Consolidation (Texte + Image)
                │
                ▼
        🔍 [search_online]        <-- Recherche Web unique (ou Catalogue Local)
                │
                ▼
        🍳 [rank_and_format]      <-- Scoring, Pydantic & Markdown Conversion
                │
                ▼
                END
```

---

## 💻 Installation et Lancement

### 1. Prérequis
Créez un fichier `.env` à la racine du projet avec vos clés API :
```env
GOOGLE_API_KEY="votre_cle_gemini"
GROQ_API_KEY="votre_cle_groq"
```

### 2. Installation des dépendances
```Bash
# Créer l'environnement virtuel
python -m venv .venv

# L'activer (Linux/macOS)
source .venv/bin/activate
# L'activer (Windows)
.venv\Scripts\activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```
> (Assurez-vous d'avoir streamlit, langchain-google-genai, langgraph, pandas et pydantic ...)

3. Lancement de l'application
```Bash
streamlit run app.
```

## Robustesse & Tests Unitaires

Le projet intègre une suite de tests unitaires utilisant des doublures de test (unittest.mock) pour valider la logique de formatage Markdown et l'intégrité de la structure Pydantic sans consommer de jetons d'API (création d'une base SQLite temporaire :memory:).

Pour exécuter les tests :
```Bash
python -m unittest tests/test_agent.py
```