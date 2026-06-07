#mcp_lieux.py
from typing import Optional
from mcp.server.fastmcp import FastMCP
from server import db

mcp = FastMCP("Wedding_Place_Server")

# =====================================================================
# MODULE LIEUX (Arguments aplatis pour une parfaite compatibilité MCP)
# =====================================================================
@mcp.tool("rechercher_lieux_disponibles", description="Utile pour chercher des salles de réception disponibles dans le catalogue selon des critères de style ou de prix")
def rechercher_lieux_disponibles(style: Optional[str] = None, budget_max_location: Optional[float] = None) -> str:
    """
    Utile pour chercher des salles de réception disponibles dans le catalogue selon des critères de style ou de prix.
    :param style: Le style du lieu (ex: 'Château', 'Plage', 'Grange'). Optionnel.
    :param budget_max_location: Le budget maximum pour la location. Optionnel.
    """
    try:
        query = "SELECT id, nom, ville, capacite_max, tarif_location, style FROM lieux WHERE disponible = 1"
        params = []
        
        if style is not None:
            query += " AND LOWER(style) = LOWER(?)"
            params.append(style.strip())

        if budget_max_location is not None:
            query += " AND tarif_location <= ?"
            params.append(budget_max_location)
            
        rows = db.read_param(query, tuple(params))
        
        if not rows["ok"]: 
            return f"Erreur BDD : {rows.get('error', 'Erreur inconnue')}"
        
        if len(rows["data"]) == 0:
            return "Aucune salle ne correspond aux critères demandés."

        resultat = "Salles disponibles trouvées :\n"
        for r in rows["data"]:
            resultat += f"- [ID {r[0]}] {r[1]} à {r[2]} | Capacité: {r[3]} pers. | Tarif: {r[4]}€ | Style: {r[5]}\n"
        return resultat

    except Exception as e:
        return f"Échec de la recherche en Base de Données : {str(e)}."


@mcp.tool("verifier_capacite_et_reserver", description="Vérifie la capacité d’un lieu et effectue la réservation si possible")
def verifier_capacite_et_reserver(lieu_id: int, nombre_invites: int, mariage_id: int) -> str:
    """
    Vérifie la capacité maximale d'un lieu spécifique par son ID et effectue la réservation 
    en mettant automatiquement à jour le budget du mariage associé.

    :param lieu_id: L'ID unique du lieu à réserver.
    :param mariage_id: L'ID du mariage concerné.
    :param nombre_invites: Le nombre d'invités prévus.
    """
    try:
        # 1. Récupération du lieu
        query = """
            SELECT nom, capacite_max, tarif_location, disponible
            FROM lieux
            WHERE id = ?
        """
        lieu = db.read_param(query, (lieu_id,))
        
        if not lieu["ok"] or len(lieu["data"]) == 0:
            return f"Erreur : Le lieu avec l'ID {lieu_id} n'existe pas."

        nom_lieu, capacite_max, tarif_location, disponible = lieu["data"][0]

        # 2. Règles métiers
        if not disponible:
            return f"Le lieu '{nom_lieu}' (ID {lieu_id}) est déjà réservé pour un autre événement."

        if nombre_invites > int(capacite_max):
            return (
                f"Opération impossible : '{nom_lieu}' possède une capacité maximale de "
                f"{capacite_max} personnes, mais votre planification en demande {nombre_invites}."
            )

        # 3. Transaction unifiée
        write_out = db.transaction([
            ("UPDATE lieux SET disponible = 0 WHERE id = ?", (lieu_id,)),
            ("""
                INSERT INTO budget_depenses (mariage_id, categorie, intitule, montant_estime, statut)
                VALUES (?, 'Lieu', ?, ?, 'Prevu')
            """, (mariage_id, f"Location {nom_lieu}", tarif_location))
        ])

        if write_out["ok"]:
            return (
                f"Succès ! Le lieu '{nom_lieu}' (ID {lieu_id}) a été réservé avec succès pour le mariage {mariage_id}. "
                f"Un coût de {tarif_location}€ a été ajouté au module Budget."
            )
        else:
            return f"Échec de la mise à jour transactionnelle du budget."

    except Exception as e:
        return f"Erreur critique lors de la tentative de réservation : {str(e)}. Transaction annulée."

if __name__ == "__main__":
    mcp.run()

