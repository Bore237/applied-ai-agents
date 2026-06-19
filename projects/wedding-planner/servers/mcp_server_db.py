
#pip install "fastmcp[cli]"
# mcp_server_db.py
# mcp_server.py

from server import db
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Wedding_Planner_DB_Server")


# =====================================================================
# AJOUT DES DOCSTRINGS RICHES POUR LE GUIDAGE DU LLM
# =====================================================================
@mcp.tool()
def executer_requete_lecture(sql: str) -> dict:
    """
    Exécute une requête SQL SELECT pour lire les données du mariage.
    
    Utilise cet outil pour inspecter les tables suivantes :
    - mariages (id, nom_code, date_evenement, budget_max, ville_depart_invites)
    - lieux (id, nom, ville, capacite_max, tarif_location, style, disponible)
    - budget_depenses (id, mariage_id, categorie, intitule, montant_estime, montant_paye, statut)
    - invites (id, mariage_id, nom, prenom, email, statut_rsvp, regime_alimentaire, besoin_vol, ville_origine)
    - playlist_didier (id, mariage_id, titre, artiste, genre, moment_diffusion, statut_validation)
    - taches_planning (id, mariage_id, titre, description, date_limite, statut, responsable_agent)

    Exemple d'argument : "SELECT * FROM lieux WHERE disponible = 1 AND style = 'Château';"
    """
    return db.read_param(sql)

@mcp.tool()
def executer_requete_ecriture(sql: str) -> dict:
    """
    Exécute une requête SQL INSERT ou UPDATE pour modifier les données du mariage.
    
    Utilise cet outil pour :
    - Réserver un lieu (Ex: UPDATE lieux SET disponible = 0 WHERE id = 1)
    - Ajouter une dépense (Ex: INSERT INTO budget_depenses ...)
    - Mettre à jour un RSVP ou ajouter une tâche au planning.
    
    Attention : Les commandes DELETE et DROP sont strictement interdites.
    """
    return db.write_param(sql)

if __name__ == "__main__":
    # Lancement du serveur MCP en mode stdio (communication standard d'entrée/sortie)
    mcp.run()