import sys
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from server import db

mcp = FastMCP("Wedding_Budget_Server")

def _recuperer_metriques_budget(mariage_id: int) -> dict:
    """
    Source unique de vérité pour l'extraction et le calcul des indicateurs budgétaires.
    Évite la duplication SQL et sécurise le parsing des types de données.
    """
    # 1. Extraction sécurisée du plafond budgétaire
    query_mariage = "SELECT budget_max FROM mariages WHERE id = ?"
    res_m = db.read_param(query_mariage, (mariage_id,))
    
    if not res_m.get("ok") or not res_m.get("data") or len(res_m["data"]) == 0:
        return {"success": False, "error": f"Le mariage ID {mariage_id} est introuvable."}
        
    try:
        budget_max = float(res_m["data"][0][0])
    except (TypeError, ValueError):
        return {"success": False, "error": f"Le budget_max pour l'ID {mariage_id} est corrompu ou invalide."}

    # 2. Sommation des engagements financiers actuels
    query_depenses = "SELECT SUM(montant_estime) FROM budget_depenses WHERE mariage_id = ?"
    res_d = db.read_param(query_depenses, (mariage_id,))
    
    total_engage = 0.0
    if res_d.get("ok") and res_d.get("data") and res_d["data"][0][0] is not None:
        try:
            total_engage = float(res_d["data"][0][0])
        except (TypeError, ValueError):
            total_engage = 0.0

    solde_restant = budget_max - total_engage

    return {
        "success": True,
        "metrics": {
            "mariage_id": mariage_id,
            "budget_max": budget_max,
            "total_engage_estime": total_engage,
            "solde_restant": solde_restant,
            "alerte_depassement": solde_restant < 0
        }
    }


@mcp.tool("obtenir_etat_budget")
def obtenir_etat_budget(mariage_id: int) -> Dict[str, Any]:
    """
    Calcule la santé financière globale d'un mariage : total engagé, 
    plafond alloué et solde disponible.
    """
    bilan = _recuperer_metriques_budget(mariage_id)
    if not bilan["success"]:
        return {"success": False, "data": {}, "error": bilan["error"]}
        
    return {"success": True, "data": bilan["metrics"], "error": None}


@mcp.tool("verifier_et_ordonner_depense")
def verifier_et_ordonner_depense(mariage_id: int, categorie: str, intitule: str, montant: float) -> Dict[str, Any]:
    """
    Valide l'impact financier d'une dépense proposée et l'inscrit de manière transactionnelle.
    """
    if montant <= 0:
        return {"success": False, "data": {}, "error": "Le montant de la dépense doit être strictement positif."}

    # Récupération de l'état actuel (Lecture juste avant écriture)
    bilan = _recuperer_metriques_budget(mariage_id)
    if not bilan["success"]:
        return {"success": False, "data": {}, "error": bilan["error"]}

    metrics = bilan["metrics"]
    solde_actuel = metrics["solde_restant"]
    depassement_prevu = (solde_actuel - montant) < 0

    # Inscription de la ligne de dépense dans la base de données
    try:
        write_out = db.transaction([
            ("""
                INSERT INTO budget_depenses (mariage_id, categorie, intitule, montant_estime, statut)
                VALUES (?, ?, ?, ?, 'Prevu')
            """, (mariage_id, categorie, intitule, montant))
        ])

        if not write_out or not write_out.get("ok"):
            return {"success": False, "data": {}, "error": "Échec de l'écriture de la dépense en base de données."}

        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "statut_enregistrement": "Confirme",
                "montant_alloue": montant,
                "nouveau_solde_calculer": round(solde_actuel - montant, 2),
                "budget_hors_controle": depassement_prevu
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": {}, "error": f"Erreur critique lors de la transaction : {str(e)}"}

@mcp.tool("proposer_modification_depense")
def proposer_modification_depense(depense_id: int, nouveau_montant: float, raison: str) -> dict:
    """
    Soumet une demande de modification de montant pour une dépense existante.
    La modification reste suspendue à la validation des mariés.
    """
    if nouveau_montant < 0:
        return {"success": False, "data": {}, "error": "Le montant ne peut pas être négatif."}

    try:
        # 1. On récupère la dépense actuelle pour l'historique
        query_check = "SELECT intitule, montant_estime, mariage_id FROM budget_depenses WHERE id = ?"
        res = db.read_param(query_check, (depense_id,))
        
        if not res.get("ok") or not res.get("data"):
            return {"success": False, "data": {}, "error": "Dépense introuvable."}
            
        intitule, ancien_montant, mariage_id = res["data"][0]

        # 2. Au lieu d'écraser la table 'budget_depenses', on inscrit la demande 
        # dans une table de révision ou on change son statut en 'En_Attente_Modification'
        # Note : Tu peux stocker le 'nouveau_montant' temporaire dans une colonne dédiée 'montant_propose'
        write_out = db.transaction([
            ("UPDATE budget_depenses SET montant_propose = ?, statut = 'En_Attente_Validation' WHERE id = ?", 
            (nouveau_montant, depense_id))
        ])

        if not write_out.get("ok"):
            return {"success": False, "data": {}, "error": "Impossible de suspendre la dépense pour modification."}

        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "depense_id": depense_id,
                "intitule": intitule,
                "ancien_montant": ancien_montant,
                "nouveau_montant_propose": nouveau_montant,
                "ecart": round(nouveau_montant - ancien_montant, 2),
                "statut_action": "Soumis_A_Validation_Humaine"
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": {}, "error": str(e)}
    
if __name__ == "__main__":
    mcp.run()