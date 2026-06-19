# mcp_invites.py

import json
import ast
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP
from server import db


mcp = FastMCP("Wedding_Guests_Server")

def calculer_stats_globales(mariage_id: int) -> Dict[str, Any]:
    """
    Fonction interne pour centraliser le calcul des statistiques des invités actifs 
    (tous ceux qui n'ont pas décliné).
    """
    # 1. Nombre total d'invités (Non Décliné)
    q_total = "SELECT COUNT(*) FROM invites WHERE mariage_id = ? AND statut_rsvp != 'Decline'"
    res_total = db.read_param(q_total, (mariage_id,))
    total_actifs = res_total["data"][0][0] if res_total["ok"] else 0

    # 2. Recensement des besoins de vols par ville d'origine (Non Décliné)
    q_vols = """
        SELECT ville_origine, COUNT(*) 
        FROM invites 
        WHERE mariage_id = ? AND besoin_vol = 1 AND statut_rsvp != 'Decline'
        GROUP BY ville_origine
    """
    res_vols = db.read_param(q_vols, (mariage_id,))
    
    repartition_vols = {}
    if res_vols["ok"]:
        for row in res_vols["data"]:
            ville, count = row
            if ville:  # Évite les valeurs vides
                repartition_vols[ville] = count

    return {
        "total_invites_actifs": total_actifs,
        "total_besoins_vol": sum(repartition_vols.values()),
        "repartition_vols_par_ville": repartition_vols
    }

@mcp.tool("importer_et_recenser_invites")
def importer_et_recenser_invites(mariage_id: int, liste_invites_raw: str) -> Dict[str, Any]:
    """
    Prend une chaîne représentant un ou plusieurs invités (JSON ou dictionnaire),
    les extrait proprement, les insère sans doublons et retourne les statistiques.
    """
    try:
        raw_clean = liste_invites_raw.strip()
        donnees = None

        # Étape 1 : Tentative de lecture en JSON standard
        try:
            donnees = json.loads(raw_clean)
        except json.JSONDecodeError:
            # Étape 2 : Secours via ast (gère les guillemets simples {'nom': 'Meunier'} du LLM)
            try:
                donnees = ast.literal_eval(raw_clean)
            except Exception as parse_err:
                return {
                    "success": False,
                    "data": {},
                    "error": f"Impossible de décoder les invités. Reçu: {liste_invites_raw}. Erreur: {str(parse_err)}"
                }

        # Étape 3 : Normalisation de la structure en liste
        if isinstance(donnees, dict):
            liste_invites = [donnees]
        elif isinstance(donnees, list):
            liste_invites = donnees
        else:
            return {
                "success": False,
                "data": {},
                "error": f"Format invalide. Attendu: Liste ou Dictionnaire, Reçu: {type(donnees)}"
            }

        invites_ajoutes = 0
        invites_doublons = 0

        # Étape 4 : Traitement d'insertion classique
        for invite in liste_invites:
            if not isinstance(invite, dict):
                continue
            nom = invite.get("nom", "").strip()
            prenom = invite.get("prenom", "").strip()
            email = invite.get("email", "").strip().lower()
            besoin_vol = 1 if invite.get("besoin_vol") in [True, 1, "Oui", "oui"] else 0
            ville_origine = invite.get("ville_origine", "").strip()

            if not email:
                continue

            query_check = "SELECT id FROM invites WHERE email = ? AND mariage_id = ?"
            res_check = db.read_param(query_check, (email, mariage_id))

            if res_check.get("ok") and len(res_check.get("data", [])) > 0:
                invites_doublons += 1
                continue 

            query_insert = """
                INSERT INTO invites (mariage_id, nom, prenom, email, besoin_vol, ville_origine)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            write_out = db.transaction([(query_insert, (mariage_id, nom, prenom, email, besoin_vol, ville_origine))])
            if write_out.get("ok"):
                invites_ajoutes += 1

        stats = calculer_stats_globales(mariage_id)

        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "synthese_import": {
                    "nouveaux_ajoutes": invites_ajoutes,
                    "doublons_ignores": invites_doublons
                },
                "statistiques_actuelles": stats 
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": {}, "error": f"Erreur critique lors de l'import : {str(e)}"}
    

@mcp.tool("mettre_a_jour_rsvp_invite")
def mettre_a_jour_rsvp_invite(invite_id: int, nouveau_statut: str) -> Dict[str, Any]:
    """
    Actualise le statut RSVP d'un invité ('En_Attente', 'Confirme', 'Decline') 
    et recalcule instantanément l'impact sur le nombre d'invités et les vols.
    """
    statuts_valides = ['En_Attente', 'Confirme', 'Decline']
    if nouveau_statut not in statuts_valides:
        return {"success": False, "data": {}, "error": f"Statut invalide. Choisissez parmi : {statuts_valides}"}

    try:
        # 1. Trouver le mariage_id lié à cet invité
        res_check = db.read_param("SELECT mariage_id, nom, prenom FROM invites WHERE id = ?", (invite_id,))
        if not res_check.get("ok") or not res_check.get("data"):
            return {"success": False, "data": {}, "error": "Invité introuvable."}
        
        mariage_id, nom, prenom = res_check["data"][0]

        # 2. Mise à jour du statut
        write_out = db.transaction([
            ("UPDATE invites SET statut_rsvp = ? WHERE id = ?", (nouveau_statut, invite_id))
        ])

        if not write_out.get("ok"):
            return {"success": False, "data": {}, "error": "Impossible de mettre à jour le RSVP."}

        # 3. Recalcul des compteurs globaux mis à jour
        stats_mises_a_jour = calculer_stats_globales(mariage_id)

        return {
            "success": True,
            "data": {
                "invite_id": invite_id,
                "nom_complet": f"{prenom} {nom}",
                "nouveau_statut_rsvp": nouveau_statut,
                "statistiques_mises_a_jour": stats_mises_a_jour
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": {}, "error": f"Erreur lors de la mise à jour RSVP : {str(e)}"}
    

@mcp.tool("extraire_besoins_vols_invites")
def extraire_besoins_vols_invites(mariage_id: int) -> Dict[str, Any]:
    """
    Retourne la liste des villes d'origine et le nombre d'invités ayant besoin d'un vol.
    Utile pour l'agent pour savoir quelles routes aériennes chercher.
    """
    try:
        stats = calculer_stats_globales(mariage_id)
        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "repartition_vols": stats["repartition_vols_par_ville"]
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "data": {}, "error": str(e)}
    
if __name__ == "__main__":
    mcp.run()