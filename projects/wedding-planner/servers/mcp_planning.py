import sys
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from server import db

mcp = FastMCP("Wedding_Planning_Server")

def _mariage_existe(mariage_id: int) -> bool | None:
    """Vérifie l'existence réelle d'un mariage dans la base de données."""
    try:
        res = db.read_param("SELECT id FROM mariages WHERE id = ?", (mariage_id,))
        return res.get("ok") and len(res.get("data", [])) > 0
    except Exception:
        return False


@mcp.tool("creer_tache_planning")
def creer_tache_planning(mariage_id: int, titre: str, date_limite: str, 
    responsable_agent: str,  description: Optional[str] = None, priorite: Optional[str] = "Moyenne"
) -> Dict[str, Any]:
    """
    Ajoute une nouvelle tâche ou un jalon critique dans le planning du mariage.
    date_limite doit être au format YYYY-MM-DD. Priorités acceptées : Haute, Moyenne, Basse.
    
    ATTENTION : 'responsable_agent' doit obligatoirement être l'une de ces valeurs :
    'Lieux', 'Budget', 'Planning', 'Traiteur', 'Humain', 'Invite', 'Didier', 'Flight'.
    """
    # 1. Sécurité Clé Étrangère applicative
    if not _mariage_existe(mariage_id):
        return {"success": False, "data": {}, "error": f"Opération rejetée : Le mariage avec l'ID {mariage_id} n'existe pas."}

    # 2. Nettoyage des entrées optionnelles
    desc_propre = description if description is not None else ""
    prio_propre = priorite if priorite in ["Haute", "Moyenne", "Basse"] else "Moyenne"

    try:
        write_out = db.transaction([
            ("""
                INSERT INTO taches_planning (mariage_id, titre, description, date_limite, priorite, responsable_agent, statut)
                VALUES (?, ?, ?, ?, ?, ?, 'A_Faire')
            """, (mariage_id, titre, desc_propre, date_limite, prio_propre, responsable_agent))
        ])

        if not write_out or not write_out.get("ok"):
            return {"success": False, "data": {}, "error": "Échec de l'insertion de la tâche en base de données."}

        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "titre": titre,
                "date_limite": date_limite,
                "priorite": prio_propre,
                "responsable_agent": responsable_agent,
                "statut_initial": "A_Faire"
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": {}, "error": f"Erreur critique lors de la création de la tâche : {str(e)}"}


@mcp.tool("obtenir_planning_mariage")
def obtenir_planning_mariage(mariage_id: int) -> Dict[str, Any]:
    """
    Récupère l'intégralité des tâches et jalons planifiés pour un mariage donné, triés par ordre chronologique.
    """
    if not _mariage_existe(mariage_id):
        return {"success": False, "data": {}, "error": f"Le mariage ID {mariage_id} n'existe pas."}

    try:
        query = """
            SELECT id, titre, description, date_limite, priorite, responsable_agent, statut 
            FROM taches_planning 
            WHERE mariage_id = ? 
            ORDER BY date_limite ASC
        """
        res = db.read_param(query, (mariage_id,))

        if not res.get("ok"):
            return {"success": False, "data": {}, "error": "Erreur lors de la lecture du planning."}

        liste_taches = []
        for row in res.get("data", []):
            liste_taches.append({
                "tache_id": row[0],
                "titre": row[1],
                "description": row[2],
                "date_limite": row[3],
                "priorite": row[4],
                "responsable_agent": row[5],
                "statut": row[6]
            })

        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "total_taches": len(liste_taches),
                "taches": liste_taches
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": {}, "error": f"Erreur critique de récupération : {str(e)}"}


@mcp.tool("mettre_a_jour_statut_tache")
def mettre_a_jour_statut_tache(tache_id: int, nouveau_statut: str) -> Dict[str, Any]:
    """
    Modifie le statut d'une tâche. 
    Statuts autorisés en conformité avec le schéma SQL : 'A_Faire', 'En_Cours', 'Termine', 'Annule'.
    """
    # Alignement strict avec la contrainte CHECK de la base de données
    statuts_valides = ['A_Faire', 'En_Cours', 'Termine', 'Annule']
    if nouveau_statut not in statuts_valides:
        return {
            "success": False,
            "data": {},
            "error": f"Statut invalide. Contrainte SQL respectée : {statuts_valides}"
        }

    try:
        res_check = db.read_param("SELECT titre, mariage_id FROM taches_planning WHERE id = ?", (tache_id,))
        if not res_check.get("ok") or not res_check.get("data"):
            return {"success": False, "data": {}, "error": f"Tâche ID {tache_id} introuvable."}

        titre, mariage_id = res_check["data"][0]

        write_out = db.transaction([
            ("UPDATE taches_planning SET statut = ? WHERE id = ?", (nouveau_statut, tache_id))
        ])

        if not write_out or not write_out.get("ok"):
            return {"success": False, "data": {}, "error": "Échec de la mise à jour du statut en base."}

        return {
            "success": True,
            "data": {
                "tache_id": tache_id,
                "titre": titre,
                "mariage_id": mariage_id,
                "nouveau_statut": nouveau_statut
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": {}, "error": f"Erreur lors de la mise à jour de la tâche : {str(e)}"}

if __name__ == "__main__":
    mcp.run()