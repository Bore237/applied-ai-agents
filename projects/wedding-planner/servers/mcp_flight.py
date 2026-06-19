# mcp_flight.py
import sys
from mcp.server.fastmcp import FastMCP
from server import db

mcp = FastMCP("Wedding_Transport_Server")

@mcp.tool("recuperer_villes_mariage")
def recuperer_villes_mariage(mariage_id: int) -> dict:
    """
    Récupère la ville de résidence des mariés et la ville où se trouve le lieu réservé 
    pour vérifier s'il y a besoin d'un déplacement.
    """
    try:
        # Requête pour lier le mariage au lieu réservé et comparer les villes
        query = """
            SELECT m.ville_residence, l.ville, l.nom 
            FROM mariages m
            LEFT JOIN lieux l ON m.lieu_id = l.id
            WHERE m.id = ?
        """
        rows = db.read_param(query, (mariage_id,))
        
        if not rows["ok"] or len(rows["data"]) == 0:
            return {
                "success": False,
                "data": None,
                "error": f"Mariage {mariage_id} introuvable"
            }
            
        ville_residence, ville_mariage, nom_lieu = rows["data"][0]
        
        if not ville_mariage:
            return {
                "success": False,
                "data": None,
                "error": f"Le mariage ID {mariage_id} Aucun lieu assigné: Impossible de calculer un trajet."
            }
            
        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "ville_residence": ville_residence,
                "ville_mariage": ville_mariage,
                "lieu": nom_lieu
            },
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Erreur lors de la récupération des villes : {str(e)}"
        }


@mcp.tool("enregistrer_frais_transport")
def enregistrer_frais_transport(mariage_id: int, cout_total: float, temps_estime_h: float, details_trajet: str) -> dict:
    """
    Enregistre le coût total des billets d'avion dans le budget et ajoute une note logistique.
    """
    try:
        intitule_depense = f"Transport aérien - {details_trajet} (Est. {temps_estime_h}h)"
        
        # Insertion du coût dans le budget
        db.transaction([
            ("""
                INSERT INTO budget_depenses (mariage_id, categorie, intitule, montant_estime, statut)
                VALUES (?, 'Transport', ?, ?, 'Prevu')
            """, (mariage_id, intitule_depense, cout_total))
        ])
        
        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "cout_total": cout_total,
                "details": details_trajet
            },
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Erreur lors de l'enregistrement du transport : {str(e)}"
        }

if __name__ == "__main__":
    mcp.run()
