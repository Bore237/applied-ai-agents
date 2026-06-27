"""
Suite de Tests Complets - Prompts et scénarios pour tester la robustesse du système.
"""

# ==========================================
# TESTS UNITAIRES - DOMAINE PAR DOMAINE
# ==========================================

UNIT_TESTS = [
    # --- TESTS INVITÉS ---
    {
        "name": "Invités - Import simple",
        "domain": "invites",
        "request": """Pour le mariage ID 1, ajoute ces invités:
        - Jean Dupont (jean.dupont@email.com) de Paris, besoin vol: Oui
        - Marie Martin (marie.martin@email.com) de Lyon, besoin vol: Non
        Dis-moi le résumé d'importation."""
    },
    {
        "name": "Invités - Mise à jour RSVP",
        "domain": "invites",
        "request": """Pour le mariage ID 1, marque l'invité ID 1 comme 'Confirme'.
        Puis affiche l'impact sur les statistiques d'invités."""
    },
    {
        "name": "Invités - Extraction des besoins de vols",
        "domain": "invites",
        "request": """Pour le mariage ID 1, extrais la liste des villes d'origine
        et le nombre de personnes nécessitant un vol pour chaque ville."""
    },
    
    # --- TESTS VOLS ---
    {
        "name": "Vols - Récupération des villes",
        "domain": "flight",
        "request": """Pour le mariage ID 1, récupère les informations de déplacement:
        ville de résidence des mariés et ville du lieu de mariage."""
    },
    {
        "name": "Vols - Enregistrement de transport",
        "domain": "flight",
        "request": """Pour le mariage ID 1, enregistre un coût de transport:
        - Prix total: 850€ (pour 2 billets Paris → Nantes)
        - Durée: 2.5 heures
        - Détails: Vol Air France AF1234"""
    },
    
    # --- TESTS PLANNING ---
    {
        "name": "Planning - Création de tâche",
        "domain": "planning",
        "request": """Pour le mariage ID 1, crée une tâche:
        - Titre: "Valider le menu avec le traiteur"
        - Date limite: 2027-01-15
        - Responsable: Traiteur
        - Priorité: Haute
        - Description: Approuver les plats finaux et ajustements diététiques"""
    },
    {
        "name": "Planning - Obtenir le planning",
        "domain": "planning",
        "request": """Pour le mariage ID 1, affiche le planning complet
        avec toutes les tâches triées par date limite."""
    },
    {
        "name": "Planning - Mise à jour statut tâche",
        "domain": "planning",
        "request": """Pour le mariage ID 1, marque la tâche ID 1 comme 'En_Cours'."""
    },
    
    # --- TESTS BUDGET ---
    {
        "name": "Budget - État du budget",
        "domain": "budget",
        "request": """Pour le mariage ID 1, affiche l'état financier complet:
        - Enveloppe maximale
        - Total engagé
        - Solde disponible
        - Alerte si dépassement"""
    },
    {
        "name": "Budget - Enregistrement de dépense",
        "domain": "budget",
        "request": """Pour le mariage ID 1, enregistre une nouvelle dépense:
        - Catégorie: Décoration
        - Intitulé: Fleurs fraîches (roses + pivoines)
        - Montant: 350€
        Valide l'impact budgétaire après enregistrement."""
    },
    {
        "name": "Budget - Modification de dépense",
        "domain": "budget",
        "request": """Pour le mariage ID 1, propose une modification:
        - Dépense ID: 1
        - Nouveau montant: 450€
        - Raison: Supplément pour 50 invités supplémentaires prévus"""
    },
    
    # --- TESTS LIEUX ---
    {
        "name": "Lieux - Recherche simple",
        "domain": "lieux",
        "request": """Pour le mariage ID 1, recherche un lieu avec:
        - Capacité: 150 invités minimum
        - Style: Château
        - Budget max: 5000€"""
    },
    {
        "name": "Lieux - Recherche par ville",
        "domain": "lieux",
        "request": """Pour le mariage ID 1, cherche un lieu à Nantes
        pouvant accueillir 120 personnes."""
    },
    {
        "name": "Lieux - Réservation (après recherche)",
        "domain": "lieux",
        "request": """Pour le mariage ID 1, réserve le lieu ID 5.
        Cela doit aussi enregistrer le coût dans le budget."""
    },
    
    # --- TESTS TRAITEUR ---
    {
        "name": "Traiteur - Génération menu gourmet",
        "domain": "traiteur",
        "request": """Pour le mariage ID 1 avec 100 invités,
        génère une proposition de menu style 'gourmet'.
        Limite à 10 plats.
        Cela doit aussi enregistrer le coût total en budget."""
    },
    {
        "name": "Traiteur - Génération menu végétarien",
        "domain": "traiteur",
        "request": """Pour le mariage ID 1 avec 80 invités,
        génère un menu style 'vegetarien'."""
    },
    {
        "name": "Traiteur - Modification de prix",
        "domain": "traiteur",
        "request": """Modifie le prix du plat 'Beef Wellington'
        à 35€ (au lieu de 28€)."""
    },
    
    # --- TESTS MUSIQUE ---
    {
        "name": "Musique - Recherche morceaux",
        "domain": "didier",
        "request": """Pour le mariage ID 1, cherche des morceaux romantiques
        'Ed Sheeran Perfect' et 'Adele Rolling in the Deep'.
        Limite à 5 résultats par recherche."""
    },
    {
        "name": "Musique - Sauvegarde playlist",
        "domain": "didier",
        "request": """Pour le mariage ID 1, ajoute ces morceaux au moment 'Diner':
        - Titre: 'La Vie en Rose', Artiste: 'Édith Piaf', Genre: 'Classique'
        - Titre: 'Clair de Lune', Artiste: 'Claude Debussy', Genre: 'Classique'"""
    },
    {
        "name": "Musique - Affichage playlist",
        "domain": "didier",
        "request": """Pour le mariage ID 1, affiche l'état complet de la playlist
        (Cocktail, Dîner, Soirée)."""
    },
]

# ==========================================
# TESTS MULTI-AGENTS - SCÉNARIOS COMPLEXES
# ==========================================

MULTI_AGENT_TESTS = [
    {
        "name": "Flux 1: Import invités + Récup vols",
        "request": """Pour le mariage ID 1, je viens de recevoir la confirmation 
        de 3 nouveaux invités:
        - Paul Durand (paul.durand@email.com) de Marseille, besoin vol
        - Sophie Lefebvre (sophie.lefebvre@email.com) de Lille, besoin vol
        - Thomas Richard (thomas.richard@email.com) de Paris, pas besoin vol
        
        Après l'import, extrait les villes et le nombre de voyageurs pour 
        l'agent Vols.""",
        "expects_agents": ["invites", "flight"]
    },
    {
        "name": "Flux 2: Recherche lieu + Enregistrement budget",
        "request": """Pour le mariage ID 1 (100 invités), je veux:
        1. Chercher un château en Île-de-France avec budget max 4000€
        2. Une fois trouvé, réserver le lieu
        3. Vérifier que le coût s'est bien enregistré en budget""",
        "expects_agents": ["lieux", "budget"]
    },
    {
        "name": "Flux 3: Menu traiteur + Mise à jour budget",
        "request": """Pour le mariage ID 1 (120 invités):
        1. Génère un menu style 'gourmet'
        2. Affiche l'état du budget après l'enregistrement automatique""",
        "expects_agents": ["traiteur", "budget"]
    },
    {
        "name": "Flux 4: Planning complet",
        "request": """Pour le mariage ID 1, je veux organiser le planning:
        1. Crée une tâche 'Confirmer RSVP des invités' (Priority: Haute, Agent: Invite) - limite 2027-01-10
        2. Crée une tâche 'Finaliser le menu' (Priority: Haute, Agent: Traiteur) - limite 2027-01-05
        3. Crée une tâche 'Réserver DJ/Animation' (Priority: Moyenne, Agent: Didier) - limite 2027-01-20
        4. Affiche le planning complet""",
        "expects_agents": ["planning"]
    },
    {
        "name": "Flux 5: Préparation complète d'un mariage",
        "request": """Pour le mariage ID 2 (150 invités, budget 20000€):
        
        ÉTAPE 1 - INVITÉS:
        Importe les invités suivants:
        - Olivier Gasquet (olivier@email.com) de Madrid, besoin vol
        - Carmen Santez (carmen@email.com) de Bordeaux, besoin vol
        - Nina Besson (nina@email.com) de Lyon, pas de vol
        
        ÉTAPE 2 - LOGISTIQUE:
        Récupère les informations de vol (villes de départ/arrivée)
        
        ÉTAPE 3 - LIEUX:
        Cherche un lieu avec capacité 150+ en Auvergne, budget max 5000€
        
        ÉTAPE 4 - MENU:
        Propose un menu gourmet pour 150 personnes
        
        ÉTAPE 5 - MUSIQUE:
        Ajoute à la playlist 'Soiree': 'Levitating' by Dua Lipa
        
        ÉTAPE 6 - PLANNING:
        Crée 3 tâches critiques (toutes Haute priorité, dates à discrétion)
        
        Résume l'état global du mariage après toutes ces opérations.""",
        "expects_agents": ["invites", "flight", "lieux", "traiteur", "didier", "planning", "budget"]
    }
]

# ==========================================
# TESTS DE ROBUSTESSE - CAS LIMITES
# ==========================================

EDGE_CASE_TESTS = [
    {
        "name": "Erreur: Mariage ID manquant",
        "request": """Ajoute un invité: Jean Dupont (jean@email.com) de Paris avec besoin de vol.
        (Note: Je n'ai pas précisé le mariage ID - le système doit me le demander)""",
        "should_ask_for": "mariage_id"
    },
    {
        "name": "Erreur: Montant négatif au budget",
        "request": """Pour le mariage ID 1, enregistre une dépense:
        - Catégorie: Décoration
        - Montant: -500€ (négatif!)
        (Doit être rejeté)""",
        "should_fail": True
    },
    {
        "name": "Erreur: Statut RSVP invalide",
        "request": """Pour le mariage ID 1, marque l'invité 1 avec le statut 'En_Vacances'.
        (Statut invalide - accepte uniquement En_Attente/Confirme/Decline)""",
        "should_fail": True
    },
    {
        "name": "Erreur: Style de menu invalide",
        "request": """Pour le mariage ID 1 (80 invités), 
        génère un menu style 'mexicain'.
        (Style invalide - accepte uniquement viande/gourmet/vegetarien/cocktail)""",
        "should_fail": True
    },
    {
        "name": "Erreur: Date limite invalide",
        "request": """Pour le mariage ID 1, crée une tâche:
        - Titre: Test
        - Date: 2020-01-01 (date passée!)
        - Agent: Planning""",
        "should_fail": True
    },
    {
        "name": "Cas limite: Nombreux appels séquentiels",
        "request": """Pour le mariage ID 1:
        1. Affiche le planning
        2. Affiche l'état du budget
        3. Affiche la playlist
        4. Récupère les infos de vol
        5. Affiche les besoins de vols des invités
        (Chaîne longue d'opérations sans état partagé)""",
        "expects_max_calls": 5
    },
    {
        "name": "Cas limite: Caractères spéciaux dans les noms",
        "request": """Pour le mariage ID 1, ajoute un invité:
        - Nom: "O'Reilly-Johnson"
        - Prénom: "François-Xavier"
        - Email: test+special@example.com
        - Ville: "Saint-Dié-des-Vosges" """,
        "should_handle_special_chars": True
    },
    {
        "name": "Cas limite: Zéro invités à traiter",
        "request": """Pour le mariage ID 1, affiche les statistiques d'invités.
        (Le mariage peut avoir 0 invité)""",
        "should_handle_empty_data": True
    },
    {
        "name": "Cas limite: Budget dépassé",
        "request": """Pour le mariage ID 1 (budget total 5000€):
        - Enregistre une dépense de 4000€
        - Enregistre une dépense de 1500€ (cela dépasse!)
        - Affiche l'alerte de dépassement
        (Doit afficher clairement le dépassement)""",
        "should_show_alert": True
    },
]

# ==========================================
# SCÉNARIOS RÉALISTES DE MARIAGE
# ==========================================

REALISTIC_SCENARIOS = [
    {
        "name": "Scénario 1: Mariage champêtre en Provence",
        "scenario": {
            "mariage_id": 1,
            "nombre_invites": 80,
            "budget": 18000,
            "ville_residence": "Paris",
            "lieu_cible": "Provence",
            "style_menu": "gourmet",
            "date_mariage": "2026-10-25"
        },
        "steps": [
            "Importe une liste de 80 invités (mix: 40 de Île-de-France, 30 de Lyon, 10 locaux)",
            "Récupère les besoins de vols (estimation pour vols Paris → Nice)",
            "Cherche un domaine en Provence (capacité 80+, ambiance champêtre)",
            "Réserve le lieu et vérifie l'impact budgétaire",
            "Propose un menu gourmet (80 personnes)",
            "Ajoute une sélection de musique romantique pour le dîner",
            "Crée le planning avec tâches critiques"
        ]
    },
    {
        "name": "Scénario 2: Mariage urbain à Paris",
        "scenario": {
            "mariage_id": 2,
            "nombre_invites": 200,
            "budget": 50000,
            "ville_residence": "Paris",
            "lieu_cible": "Paris 5e",
            "style_menu": "gourmet",
            "date_mariage": "2026-10-20"
        },
        "steps": [
            "Importe une liste de 200 invités (résidents Paris et régions)",
            "Cherche une salle de réception prestigieuse à Paris",
            "Propose un menu gastronomique pour 200 couverts",
            "Sélectionne une playlist variée (cocktail + dîner + soirée dansante)",
            "Crée 10+ tâches de planning (maitre d'hôtel, photographe, transports, etc.)",
            "Vérifie que le budget global est respecté"
        ]
    },
    {
        "name": "Scénario 3: Mariage international",
        "scenario": {
            "mariage_id": 3,
            "nombre_invites": 120,
            "budget": 35000,
            "ville_residence": "Londres",
            "ville_mariage": "Côte d'Azur",
            "style_menu": "vegetarien",
            "date_mariage": "2027-08-10"
        },
        "steps": [
            "Importe invités de multiple pays (France, UK, Allemagne, Espagne)",
            "Analyse les besoins de vols multiples (Londres → Nice)",
            "Cherche un lieu côtier avec ambiance méditerranéenne",
            "Propose un menu végétarien (accommode les régimes variés)",
            "Sélectionne une musique internationalement appréciée",
            "Gère les complexités de planning multi-pays (fuseaux horaires)"
        ]
    }
]

# ==========================================
# FONCTION DE GÉNÉRATION DE RAPPORT DE TEST
# ==========================================

def generate_test_report(test_name: str, result: dict, status: str) -> str:
    """Génère un rapport formaté pour un test."""
    
    emoji_status = {
        "PASS": "✅",
        "FAIL": "❌",
        "WARN": "⚠️",
        "SKIP": "⏭️"
    }
    
    report = f"""
{emoji_status.get(status, '❓')} {test_name}
{'='*70}
Status: {status}
"""
    
    if result.get("error"):
        report += f"Error: {result['error']}\n"
    
    if result.get("duration"):
        report += f"Duration: {result['duration']:.2f}s\n"
    
    if result.get("details"):
        report += f"Details: {result['details']}\n"
    
    report += "\n"
    
    return report

# ==========================================
# SOMMAIRE DES TESTS
# ==========================================

TEST_SUMMARY = f"""
📊 SUITE DE TESTS COMPLÈTE - RÉSUMÉ
{'='*70}

TESTS UNITAIRES (Domaine par domaine):
  - Invités: 3 tests
  - Vols: 2 tests
  - Planning: 3 tests
  - Budget: 3 tests
  - Lieux: 3 tests
  - Traiteur: 3 tests
  - Musique: 3 tests
  TOTAL: 20 tests

TESTS MULTI-AGENTS (Flux complexes):
  - 5 flux complexes testant l'orchestration

TESTS DE ROBUSTESSE (Cas limites):
  - 10 cas limites et erreurs à gérer

SCÉNARIOS RÉALISTES:
  - 3 scénarios réalistes complets de mariage

TOTAL: 38+ tests pour valider la robustesse du système
"""
"""
Tu es un orchestrateur d'agents de gestion de mariage.

Exécute les demandes suivantes dans l'ordre indiqué. Pour chaque étape :

* appelle l'agent correspondant au domaine ;
* attends le résultat avant de passer à l'étape suivante ;
* si une étape échoue, indique clairement laquelle et la raison ;
* à la fin, fournis un récapitulatif global.

Étape 1 — Domaine: planning

Mariage ID: 3

Créer une tâche :

* Titre : Valider le menu avec le traiteur
* Date limite : 2027-01-15
* Responsable : Traiteur
* Priorité : Haute
* Description : Approuver les plats finaux et ajustements diététiques

Étape 2 — Domaine: invites

Mariage ID: 3

Ajouter les invités suivants :

1. Jean Dupont

   * Email : [jean.dupont@email.com](mailto:jean.dupont@email.com)
   * Ville : Paris
   * Besoin de vol : Oui

2. Marie Martin

   * Email : [marie.martin@email.com](mailto:marie.martin@email.com)
   * Ville : Lyon
   * Besoin de vol : Non

Retourner un résumé d'importation contenant :

* nombre d'invités créés ;
* nombre d'échecs ;
* éventuels doublons ;
* besoins de transport détectés.

Étape 3 — Domaine: lieux

Mariage ID: 3

Rechercher des lieux correspondant aux critères :

* capacité minimale : 100 invités ;
* style : Château ;
* budget maximum : 18 000 €.

Retourner les 5 meilleures options avec :

* nom ;
* localisation ;
* capacité ;
* budget estimé ;
* score de pertinence.

Format de sortie attendu :

{
"planning": { ... },
"invites": { ... },
"lieux": { ... },
"success": true
}

"""

print(TEST_SUMMARY)