# 🤖 Advanced AI Agents & Orchestration Ecosystem
![Python](https://img.shields.io/badge/python-3.11-blue)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph--LangChain-orange)
![MCP](https://img.shields.io/badge/Protocol-Model__Context__Protocol-green)
![Streamlit](https://img.shields.io/badge/UI-Streamlit__Wide-red)
![QA](https://img.shields.io/badge/Tests-Pytest__Asyncio-lightgrey)
![Status](https://img.shields.io/badge/status-production__ready-success)

Bienvenue dans ce dépôt portfolio regroupant une suite d'applications de production centrées sur l'ingénierie des agents IA autonomes, l'orchestration de workflows complexes et la mise en œuvre du Model Context Protocol (MCP) d'Anthropic.

L'objectif de ce dépôt est de démontrer la mise en œuvre de patterns d'architecture IA robustes, déterministes, sécurisés et testés, s'éloignant des simples chatbots pour proposer de véritables systèmes agents prêts pour la production.

## Vue d'Ensemble de l'Écosystème
Ce dépôt est structuré en sous-projets indépendants, chacun explorant un paradigme d'architecture agentic spécifique :
| Projet | Paradigme d'Agent | Innovation Clé | Stack Technique |
|--------|--------------------|----------------|-----------------|
| ✉️ MCP Email Assistant | Agent Solo + Middlewares | Sécurisation HITL & Résumé de contexte dynamique | LangGraph, MCP, Streamlit, Pytest-Asyncio |
| 🥗 Chef AI Dashboard | Pipeline Déterministe (DAG) | Vision multi-modale & Sortie structurée Pydantic | LangGraph, Gemini 2.5, SQLite, Pandas |
| 💍 Wedding Planner | Supervision Hiérarchique | Architecture Multi-Agents & Transport MCP/SSE | LangChain, FastMCP, Groq, SQLite3 |

## Focus sur les Piliers Techniques du Répertoire
Parcourir ce dépôt vous permettra de voir des implémentations concrètes de concepts avancés en ingénierie de LLM :

* Model Context Protocol (MCP) : Découplage strict entre la logique décisionnelle de l'agent et l'exécution des outils (Serveurs Gmail et bases de données locaux/distants).
* Fiabilité et Déterminisme (Graphs vs ReAct) : Utilisation de graphes orientés acycliques (DAG) avec LangGraph et LangChain pour encadrer le comportement des LLM et éliminer les boucles infinies d'appels d'API.
* Gouvernance et Sécurité (Human-In-The-Loop) : Mécanismes d'interception d'état permettant de figer l'exécution de l'agent avant toute action critique (écriture, suppression, transaction financière) pour validation humaine.
* Middlewares d'Optimisation : Gestion fine de la fenêtre de contexte par compression et résumé automatique de l'historique en arrière-plan.
* Qualité Logicielle : Suites de tests asynchrones et unitaires automatisés utilisant des doublures de test (unittest.mock) et des bases de données éphémères (:memory:).

## Structure et Navigation dans le Dépôt
Chaque dossier contient son propre sous-README détaillé avec les instructions spécifiques d'installation, de configuration des variables d'environnement (.env) et de lancement :

### 1. ✉️ MCP Email Assistant AI
* Description : Assistant de messagerie sécurisé capable de trier et d'interagir avec Gmail.
* Points forts : Interception orange HITL sur interface Streamlit Wide, tests unitaires asynchrones avec pytest-asyncio.

### 2. 🥗 Chef AI Dashboard
* Description : Assistant culinaire intelligent analysant le contenu d'un frigo par reconnaissance d'image pour générer des recettes typées.
* Points forts : Pipeline 100% prévisible, extraction de métriques métier persistées dans SQLite, parsing Pydantic strict.

### 3. 💍 Wedding Planner Multi-Agents
* Description : Système multi-agents collaboratif sous la direction d'un Superviseur Central pour l'organisation logistique et financière d'événements.
* Points forts : Modèle de réponse MCP unifié, intégration d'API tierces (Kiwi.com via SSE), isolation stricte des compétences par agent.

🛠️ Stack Globale du Projet
* Orchestration : LangGraph, LangChain (Core & Agents)
* Modèles & Inférence : Groq Cloud (Llama 3.1), Google Gemini 2.5 Flash, OpenAI
* Protocoles & Données : Anthropic MCP (FastMCP), SQLite3, Pydantic (v2)
* Interfaces Utilisateur : Streamlit (Wide layout, graphiques Pandas analytiques)
* QA & MLOps : Pytest, Pytest-asyncio, Unittest Mocking

✍️ Informations Projet
- **Auteur** : Goudjou Borel (Bore237)
- **Date de réalisation** : Juin 2026
- **Licence** : MIT
