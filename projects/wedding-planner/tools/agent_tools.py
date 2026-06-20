from agents.sous_agents import *
from langchain_core.tools import tool

# Exemple 1 : L'Agent Invités
@tool
async def outil_agent_invites(consigne: str) -> str:
    """
    Rôle : Expert en logistique, hébergement et gestion de la liste des invités.
    
    Quand l'utiliser : 
    - Pour importer, ajouter ou modifier des invités en base de données (besoin d'un mariage_id).
    - Pour analyser les RSVP (Confirmé, En attente, Décliné).
    - Pour extraire la liste des villes d'origine (Hubs de départ) des invités.
    
    Ce qu'il NE FAIT PAS : 
    - Ne cherche PAS de billets d'avion (passer le relais à outil_agent_flight).
    - Ne gère pas les dépenses financières (passer le relais à outil_agent_budget).
    
    Format de consigne attendu : Transmettre la demande brute de l'utilisateur avec le contexte et les données d'invités si présentes.
    """
    return await executer_agent_invites(consigne)

# Exemple 2 : L'Agent Vols / Flight
@tool
async def outil_agent_flight(consigne: str) -> str:
    """
    Rôle : Expert en recherche de vols, tarification aérienne et offres de groupe.
    
    Quand l'utiliser :
    - Dès qu'il faut chercher des estimations de prix de billets d'avion pour une ou plusieurs villes d'origine.
    - Pour planifier les trajets aériens des invités.
    
    Ce qu'il NE FAIT PAS :
    - Ne sait pas qui est invité et ne modifie pas les fiches invités (passer le relais à outil_agent_invites pour le recensement).
    
    Format de consigne attendu : Fournir les villes de départ et le nombre de passagers requis.
    """
    return await executer_agent_flight(consigne)

@tool
async def outil_agent_planning(consigne: str) -> str:
    """
    Rôle : Expert en gestion de projet, calendrier et suivi des jalons chronologiques.
    
    Quand l'utiliser :
    - Pour créer, modifier ou afficher les tâches de préparation (ex: choix du lieu, envoi des faire-part).
    - Pour ordonner les préparatifs dans le temps et vérifier les dates butoirs.
    
    Ce qu'il NE FAIT PAS :
    - Ne gère aucun aspect financier ou devis (passer le relais à outil_agent_budget).
    - Ne liste pas les invités (passer le relais à outil_agent_invites).
    
    Format de consigne : Transmettre la demande de planification avec le mariage_id et les dates clés.
    """
    return await executer_agent_planning(consigne)

@tool
async def outil_agent_budget(consigne: str) -> str:
    """
    Rôle : Contrôleur de gestion financière, suivi des dépenses, acomptes et enveloppe globale.
    
    Quand l'utiliser :
    - Pour enregistrer une dépense, calculer un reste à payer, ou analyser la répartition du budget.
    - Pour valider si une prestation (traiteur, lieu) entre dans les clous financiers des mariés.
    
    Ce qu'il NE FAIT PAS :
    - Ne crée pas de tâches de rappel dans le calendrier (passer le relais à outil_agent_planning).
    
    Format de consigne : Inclure impérativement les montants numériques, la catégorie de dépense et le mariage_id.
    """
    return await executer_agent_budget(consigne)

@tool
async def outil_agent_lieux(consigne: str) -> str:
    """
    Rôle : Expert en recherche, sélection et contractualisation des domaines et salles de réception.
    
    Quand l'utiliser :
    - Pour chercher des lieux disponibles selon une capacité d'invités ou une zone géographique.
    - Pour gérer le statut de réservation du domaine principal.
    
    Ce qu'il NE FAIT PAS :
    - Ne gère pas les menus ou la nourriture (passer le relais à outil_agent_traiteur).
    
    Format de consigne : Spécifier la région cible, la capacité d'accueil minimale et le mariage_id.
    """
    return await executer_agent_lieux(consigne)

@tool
async def outil_agent_traiteur(consigne: str) -> str:
    """
    Rôle : Expert gastronomique, gestion des menus, des pièces de cocktail et des restrictions alimentaires.
    
    Quand l'utiliser :
    - Pour concevoir le menu, estimer le coût par pièce/invité, ou ajuster les formules (buffet, service à l'assiette).
    - Pour recenser les allergies globales signalées.
    
    Ce qu'il NE FAIT PAS :
    - Ne réserve pas la salle physique (passer le relais à outil_agent_lieux).
    
    Format de consigne : Préciser le type de repas, le nombre de convives estimé et le mariage_id.
    """
    return await executer_agent_traiteur(consigne)

@tool
async def outil_agent_didier(consigne: str) -> str:
    """
    Rôle : Expert Ambiance, Animation, Coordination technique (Son, Lumière, DJ, Artistes).
    
    Quand l'utiliser :
    - Pour planifier la playlist/gérer les demandes musicales des mariés (Ouverture de bal, soirée).
    - Pour caler les interventions des proches durant le dîner ou coordonner le matériel avec le lieu.
    
    Ce qu'il NE FAIT PAS :
    - Ne gère pas l'envoi des invitations physiques (passer le relais à outil_agent_invites).
    
    Format de consigne : Transmettre les styles musicaux, contraintes logistiques d'ambiance et le mariage_id.
    """
    return await executer_agent_didier(consigne)