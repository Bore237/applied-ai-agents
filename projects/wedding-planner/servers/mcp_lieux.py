#mcp_lieux.py
from typing import Optional
from mcp.server.fastmcp import FastMCP
from server import db
import random

mcp = FastMCP("Wedding_Place_Server")

@mcp.tool("rechercher_lieux_disponibles")
def rechercher_lieux_disponibles(
    nombre_invites: int = 500, 
    style: Optional[str] = None, 
    budget_max_location: Optional[float] = None,
    ville: Optional[str] = None
) -> dict:
    """
    Recherche les lieux de mariage actuellement disponibles.

    UTILISATION :
    Ce tool doit être appelé AVANT toute réservation de lieu.
    Le champ 'lieux_id' retourné par ce tool est obligatoire pour utiliser le tool 'reserver_lieux_mariage'.

    Paramètres :
    - nombre_invites : nombre d'invités prévus
    - style : filtre optionnel (Château, Plage, Grange, Salle...)
    - budget_max_location : budget maximal pour la location
    - ville : ville recherchée (ex: Paris, Nantes...)
    """
    try:
        query = "SELECT id, nom, ville, capacite_max, tarif_location, style FROM lieux WHERE disponible = 1"
        params = []
        
        # Ajout du filtre de ville pour que l'agent puisse cibler "Paris"
        if ville is not None and ville.strip() != "":
            query += " AND LOWER(ville) = LOWER(?)"
            params.append(ville.strip())
        
        if style is not None and style.strip() != "":
            query += " AND LOWER(style) = LOWER(?)"
            params.append(style.strip())

        if budget_max_location is not None:
            query += " AND tarif_location <= ?"
            params.append(budget_max_location)
            
        rows = db.read_param(query, tuple(params))
        
        if not rows["ok"]: 
            return {
                "success": False, 
                "data": None, 
                "error": f"Erreur BDD : {rows.get('error', 'Inconnue')}"
            }
        
        if len(rows["data"]) == 0:
            return {
                "success": False, 
                "data": None, 
                "error": "Aucune salle ne correspond aux critères demandés."
            }

        lieux_trouves = []
        for r in rows["data"]:
            if nombre_invites <= int(r[3]):
                lieux_trouves.append({
                    "lieux_id": r[0],
                    "nom": r[1],
                    "ville": r[2],
                    "capacite_max": r[3],
                    "tarif_location": r[4],
                    "style": r[5]
                })
        
        if not lieux_trouves:
            return {
                "success": False, 
                "data": None, 
                "error": f"Capacité insuffisante (places max insuffisantes pour {nombre_invites} demandées)."
            }
        
        # FIX : random.choice est safe et n'induit pas d'erreur d'index hors limites
        return {
            "success": True,
            "data": random.choice(lieux_trouves),
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}
@mcp.tool("reserver_lieux_mariage")
def reserver_lieux_mariage(lieux_id: int, mariage_id: int) -> dict:
    """
    Valide et enregistre la réservation ferme d'un lieu pour un mariage spécifique.
    Cette action est irréversible : elle bloque le lieu en BDD, lie le lieu au mariage et crée la ligne de dépense financière.

    Paramètres :
    - lieux_id : id du lieu retouner pas le tools rechercher_lieux_disponibles
    - mariage_id : id du mariage fournir pas utilisateur
    """
    try:
        # 1. Récupération du lieu
        query = "SELECT nom, tarif_location, disponible, ville FROM lieux WHERE id = ?"
        lieu = db.read_param(query, (lieux_id,))
        
        if not lieu["ok"] or len(lieu["data"]) == 0:
            return {"success": False, "data": None, "error": f"Le lieu ID {lieux_id} n'existe pas."}

        nom_lieux, tarif_location, disponible, ville = lieu["data"][0]

        # 2. Validation des règles métiers
        if not disponible:
            return {"success": False, "data": None, "error": f"Le lieu '{nom_lieux}' (ID {lieux_id}) est indisponible."}

        # 3. Transaction unifiée
        write_out = db.transaction([
            ("UPDATE lieux SET disponible = 0 WHERE id = ?", (lieux_id,)),
            ("UPDATE mariages SET lieu_id = ? WHERE id = ?", (lieux_id, mariage_id)),
            ("""
                INSERT INTO budget_depenses (mariage_id, categorie, intitule, montant_estime, statut)
                VALUES (?, 'Lieu', ?, ?, 'Prevu')
            """, (mariage_id, f"Location {nom_lieux} ({ville})", tarif_location))
        ])

        if not write_out["ok"]:
            return {"success": False, "data": None, "error": "Échec de l'écriture transactionnelle en base."}

        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "lieux_id": lieux_id,
                "nom_lieux": nom_lieux,
                "ville": ville,
                "montant_ajoute": tarif_location,
                "statut": "Reserve"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "data": None, "error": f"Erreur critique de réservation : {str(e)}"}

if __name__ == "__main__":
    mcp.run()