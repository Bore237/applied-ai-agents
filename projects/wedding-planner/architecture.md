# Wedding Planner Multi-Agents
## Objectif

Construire un système multi-agents spécialisé dans l'organisation de mariage.

Chaque agent possède :

* un domaine d'expertise clairement défini ;
* un ensemble d'outils autorisés ;
* des frontières strictes pour éviter les chevauchements de responsabilités.

## Architecture
Le projet repose sur un paradigme de supervision hiérarchique où l'utilisateur ne dialogue qu'avec un coordinateur unique.
```text
wedding_planner/
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Gestion des variables d'environnement (OpenAI, API keys)
│
├── schemas/
│   ├── __init__.py
│   └── state.py             # Modèles Pydantic pour valider les entrées/sorties
│
├── tools/
│   ├── __init__.py
│   ├── mcp_tools.py      # Tranforme les mcp en tools 
|   └── agent_tools.py    # Transforme les sous-agents en tools
│
├── agents/
│   ├── __init__.py
│   ├── supervisor.py        # Logique de routage centrale
│   ├── budget.py            # Chaîne ou Agent Budget            
│   └── didier.py            # ....
|
├── servers
|   ├── mcp_lieux.py 
│   └── mcp_didier.py       #...
├── app.py                  # Interface pour utiliser agents
└── requirements.txt
```

## Spécifications Fonctionnelles des Sous-Agents
Pour garantir un routage sans ambiguïté par l'orchestrateur, chaque agent est défini selon trois critères : Domaine de compétence, Périmètre d'action et Frontières.

### Agent Budget
* Domaine : Calcul comptable, santé financière et risques de dépassement.
* Périmètre d'action :
    * obtenir_etat_budget(mariage_id) : Renvoie budget_max, total_engage_estime, solde_restant et alerte_depassement.
    * verifier_et_ordonner_depense(...) : Lit le solde, évalue le risque budget_hors_controle et insère la dépense en transaction ('Prevu').
    * proposer_modification_depense(...) : Calcule l'écart et suspend la dépense sous le statut 'En_Attente_Validation'.
* Frontières : Ne prend aucune décision finale d'annulation. Ne modifie pas une dépense validée sans basculer dans un état suspendu à l'arbitrage humain.

### Agent Lieu
* Domaine : Recherche de salles disponibles, validation des critères logistiques et réservation ferme.
* Périmètre d'action :
    * rechercher_lieux_disponibles(...) : Filtre les salles selon la capacité, la ville, le style et le tarif maximal, puis sélectionne un lieu disponible de manière aléatoire.
    * reserver_lieux_mariage(...) : Bloque le lieu, le lie au mariage et injecte automatiquement le coût de location dans le budget ('Lieu', statut 'Prevu').
* Frontières : Action de réservation irréversible. Impossible de réserver un lieu déjà indisponible ou inexistant.

### Agent Logistique & Transport
* Domaine : Analyse des besoins de déplacement et enregistrement des coûts de transport.
* Périmètre d'action :
    * recuperer_villes_mariage(mariage_id) : Compare la ville de résidence des mariés et celle du lieu réservé. Lève une erreur si aucun lieu n'est assigné.
    * enregistrer_frais_transport(...) : Injecte le coût total des billets dans le budget sous la catégorie 'Transport' avec le statut 'Prevu'.
* Frontières : Ne cherche pas directement les billets sur les API tierces (rôle dévolu aux outils externes ou sous-agents de vol). N'effectue aucune réservation ferme.

### Agent Traiteur
* Domaine : Conception de menus thématiques via API externe (TheMealDB), ajustements tarifaires et calcul des coûts de revient culinaires.
* Périmètre d'action :
    * modifier_prix_plat(...) : Réajuste le prix unitaire d'un plat spécifique directement dans la table de tarification.
    * obtenir_menus_traiteur(...) : Récupère les plats distants, calcule le coût global selon le nombre d'invités et exécute une transaction atomique pour enregistrer le budget et les plats retenus.
* Frontières : Limité aux styles de menus configurés (viande, gourmet, vegetarien, cocktail). Si l'API externe est indisponible, l'opération d'écriture est totalement

### Agent Didier (Musique)
* Domaine : Recherche de catalogues (iTunes), filtrage de sécurité et structuration de la playlist.
* Périmètre d'action :
    * rechercher_morceaux(...) : Interroge iTunes et filtre en temps réel les titres ou artistes présents dans la blacklist.
    * sauvegarder_morceaux(...) : Injecte un lot JSON via INSERT OR IGNORE (sans doublons) pour les moments 'Cocktail', 'Diner' ou 'Soiree'.
    * resumer_playlist(mariage_id) : Extrait et segmente les morceaux au statut 'Valide' par moments (cocktail, diner, soiree, non_assigne).
* Frontières : Interdiction d'inventer des morceaux hors résultats réels. Ne doit pas appeler l'outil de lecture en boucle pour la même requête.

### Agent Planning
* Domaine : Gestion du calendrier, création de jalons critiques et suivi des responsabilités par agent.
* Périmètre d'action :
    * creer_tache_planning(...) : Enregistre une tâche avec une date limite (YYYY-MM-DD), une priorité et attribue la responsabilité à un agent spécifique.
    * obtenir_planning_mariage(mariage_id) : Extrait et trie l'intégralité des tâches associées par ordre chronologique.
    * mettre_a_jour_statut_tache(...) : Modifie l'état d'une tâche en respectant les contraintes SQL ('A_Faire', 'En_Cours', 'Termine', 'Annule').
* Frontières : Rejette les actions si le mariage_id n'existe pas. Les valeurs de responsable_agent sont strictement limitées aux codes des serveurs MCP autorisés.

### Agent Communication / Invités
* Domaine : Gestion de la liste des invités, intégration de données (JSON/Ast) et suivi des indicateurs RSVP et logistiques.
* Périmètre d'action :
    * importer_et_recenser_invites(...) : Parse et normalise les entrées (dictionnaires ou listes), filtre les doublons par email et insère les invités en BDD.
    * mettre_a_jour_rsvp_invite(...) : Modifie le RSVP ('En_Attente', 'Confirme', 'Decline') et recalcule immédiatement les statistiques globales.
    * extraire_besoins_vols_invites(mariage_id) : Extrait le volume d'invités actifs nécessitant un acheminement aérien, segmenté par ville d'origine.
* Frontières : Ne gère pas l'envoi effectif des invitations ou relances (délégué à l'Agent Communication / e-mail). Exclut automatiquement les invités au statut 'Decline' de tous les calculs de répartition des transports.

## Principes de conception
### Prompt Engineering
Avant tout développement
1. Définir précisément le rôle de chaque agent.
2. Définir son périmètre d'action.
3. Définir ses limites.
Chaque agent doit savoir :
* ce qu'il maîtrise ;
* ce qu'il peut faire ;
* ce qu'il ne doit jamais faire.

## Documentation standard des sous-agents
Chaque agent doit documenter :

* Domaine de compétence: ce que l'agent maîtrise.
* Périmètre d'action: Actions qu'il est autorisé à exécuter.
* Frontières: Actions qu'il ne peut jamais exécuter.
* Objectif :
    * éviter les erreurs de routage ;
    * éviter qu'un agent exécute une tâche relevant d'un autre agent.

## Orchestration
Pattern de délégation
```python
# Utiliser
create_agent(...)
# Ne plus utiliser (ancienne approche)
AgentExecutor
```
## Contrat de sortie des outils
Tous les outils doivent respecter le même format :
```json
{
  "success": true,
  "data": {},
  "error": null
}
```
## Gestion des erreurs
Les erreurs des outils doivent être renvoyées à l'agent pour ne pas faire échouer le workflow.
Objectif :

* permettre à l'agent de corriger son appel ;
* permettre un second essai ;
* améliorer la robustesse.

Exemple :
```python
{
  "success": False,
  "data": {},
  "error": "Date invalide"
}
```
## Limitation des boucles
Pour éviter les dérives :
* limiter le nombre de recherches ;
* limiter les réessais ;
* Formater les sorties des tools externes 
Exemple:
```python
for tool in transport_tools:
    if tool.name == "search-flight":
        print("FUNC =", tool.func)
        print("COROUTINE =", tool.coroutine)

    # On définit la nouvelle logique asynchrone
    async def _wrapped_coroutine(**kwargs):
        raw_result = await tool.ainvoke(kwargs)
        try:
            flights = extract_json(raw_result)
            if not isinstance(flights, list) or len(flights) == 0:
                return {"success": False, "data": None, "error": "Aucun vol trouvé"}
            
            # On extrait uniquement le premier vol (le meilleur)
            best = flights[0]
            return {"success": True, "data": {"prix": best.get("price")},"error": None  }

        except Exception as e:
            return {"success": False, "data": None, "error": str(e)}
    
    # Fonction de repli obligatoire pour la signature synchrone de StructuredTool
    def _sync_fallback(*args, **kwargs):
        raise NotImplementedError("Ce wrapper supporte uniquement l'exécution asynchrone via ainvoke.")

    # 2. On instancie un nouveau StructuredTool en conservant les métadonnées et le schéma d'origine
    return StructuredTool(name=tool.name, description=tool.description, args_schema=tool.args_schema, 
                            coroutine=_wrapped_coroutine,   func=_sync_fallback)
```
## Gestion stricte des identifiants
* Règle absolue: Toujours utiliser l'identifiant fourni par l'utilisateur.
* Interdictions :(Incrémenter; corriger; deviner; remplacer.)
* Cette règle s'applique à :mariage_id, tache_id,...

## Sécurité transactionnelle (SQL)
prompt: `Alors que j'ai essayer de faire a mon niveaux pas de flatterie je veux analyse rigoureuse et dur qui m'aidera vraiment. Je te laisse rendre ce code robuste`

### Règle d'or 
Une vérification suivie d'une écriture basée sur cette vérification doit se faire dans un bloc d'isolation transactionnel strict (idéalement via un verrou ou une seule transaction regroupant lecture et écriture).

### Transactions en base de données ACID
* A (Atomicité) : toutes les requêtes liées doivent être exécutées entièrement ou pas du tout (tout ou rien).
* C (Cohérence) : le système passe d’un état valide à un autre état valide, en respectant les règles d’intégrité.
* I (Isolation) : les modifications d’une transaction ne sont pas visibles par les autres tant qu’elles ne sont pas validées (commit).
* D (Durabilité) : les données validées sont sauvegardées de manière permanente et restent disponibles même en cas de panne (ex : coupure de courant).

### Sécurité en trois couches
la sécurité repose sur plusieurs couches complémentaires. L
* a base de données constitue la couche de confiance la plus forte, en garantissant l’intégrité des données via les contraintes, les transactions et les mécanismes d’isolation, et reste la source de vérité du système. 
* La couche applicative, ou MCP, assure la validation métier et ajoute des garde-fous pour prévenir les erreurs et les incohérences avant toute interaction avec la base. 
* la couche du prompt ou du LLM joue uniquement un rôle de guidage comportemental et d’assistance, sans aucune garantie de sécurité fiable. 

Il est essentiel de considérer que le prompt ne peut en aucun cas être utilisé comme un mécanisme de sécurité, mais seulement comme un support d’orientation, la sécurité réelle devant toujours être assurée par les couches inférieures.


## Production

1. L'Industrialisation et Conteneurisation (Docker)
Pour l'instant, tes serveurs MCP Pour rendre le tout portable et déployable :

* Dockeriser chaque composant : Crée un Dockerfile optimisé (multi-stage build si nécessaire) pour ton orchestrateur et tes scripts serveurs.
* Orchestration avec Docker-Compose : Rédige un fichier docker-compose.yml qui monte :
    * Le conteneur de l'orchestrateur central.
    * Les différents conteneurs pour tes serveurs FastMCP.
    * Un volume partagé ou un conteneur dédié pour ta base de données SQLite (ou PostgreSQL si tu décides de migrer pour gérer de la vraie concurrence).

2. L'Observabilité et le Tracing (La Boîte Noire)
Debugger des systèmes multi-agents dans le terminal devient vite un enfer dès que le nombre de tokens augmente. On as besoin de voir ce qu'il se passe à l'intérieur.

* Intégration d'un outil de tracing : Connecte le projet à LangSmith (la solution native de LangChain) ou à une alternative open-source comme Arize Phoenix ou Langfuse.

* Ce que ça apporte : On pourrais visualiser graphiquement l'arbre d'exécution (quelle consigne exacte l'orchestrateur a envoyé à l'agent Logistique, ce que l'outil a répondu, le nombre de tokens consommés, et la latence de chaque appel LLM).

3. La Gestion des Erreurs et la Résilience (Fallbacks)
Actuellement, si un sous-agent renvoie une erreur (par exemple, une contrainte SQLite violée ou une API Flights indisponible), le graphe risque de planter ou de renvoyer une réponse brute illisible.

* Interception des erreurs d'outils : Configure ton ToolNode ou tes fonctions de secours pour intercepter les exceptions.

* Stratégie de repli : Si le modèle llama-3.1-8b échoue deux fois de suite sur une validation de format, configure un mécanisme de fallback pour passer temporairement sur un modèle plus robuste (comme mixtral-8x22b ou un modèle cloud plus imposant via Groq) pour débloquer la situation.

4. Une Interface Utilisateur (UI)
Quitter le terminal donnera immédiatement une autre dimension à du projet. Tu as deux options rapides et très efficaces en Python :

* Chainlit : Parfait pour les applications de type Chat/Agent. Il gère nativement l'affichage des "pensées" de l'agent (on voit quand il appelle un outil, ce que l'outil répond, etc.) et supporte le streaming de texte.

* Streamlit : Idéal si tu veux diviser ton écran en deux : un panneau de chat avec l'orchestrateur à gauche, et un tableau de bord dynamique (les graphiques du budget, la table des invités, le planning) mis à jour en temps réel à droite.

5. Automatisation de ta Suite de Tests (CI/CD)
Utilise la suite de tests qu'on vient de valider pour créer un script de non-régression (run_tests.py).

* Tu pourras l'intégrer dans un pipeline GitHub Actions pour t'assurer que chaque modification de ton code, modification de prompt ou ajout d'un nouvel outil ne casse pas le routage de ton orchestrateur.

* Pour cette prochaine étape, tu préfères te concentrer sur l'aspect infra et MLOps (Docker, tracking des tokens, base de données) ou sur le livrable visuel (création de l'interface utilisateur avec Chainlit/Streamlit) ?


## Nouvelle fonctionalité

* Une fonction qui extraire parse un fichier exel pour remplir automatiquement la liste des invitées.
* Gerer envoie des mails au marier