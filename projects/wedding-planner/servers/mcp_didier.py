import json
import re
import requests
from mcp.server.fastmcp import FastMCP
from server import db

mcp = FastMCP("Wedding_Music_Server")

# ==========================================
# TOOL 1 : RECHERCHE SANS ÉCRITURE
# ==========================================
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

@mcp.tool("rechercher_morceaux")
def rechercher_morceaux(terme_recherche: str, mariage_id: int, limite: int = 5) -> dict:
    """
    Recherche des morceaux de musique sur iTunes pour un mariage.

    Utiliser cet outil lorsqu'un utilisateur :
    - recherche une chanson ;
    - recherche un artiste ;
    - demande des suggestions musicales ;
    - souhaite ajouter un morceau à la playlist du mariage.

    L'outil filtre automatiquement les morceaux présents dans la blacklist
    du mariage afin de ne proposer que des résultats autorisés.

    Paramètres :
    - terme_recherche : titre, artiste, album ou mots-clés.
    - mariage_id : identifiant du mariage.
    - limite : nombre maximum de résultats à retourner.

    Retour :
    {
        "success": bool,
        "data" : {"message": str,
            "tracks": [
                {
                    "titre": str,
                    "artiste": str,
                    "genre": str
                }
            ]
        } or None
        "error": str or None
    }

    Instructions pour l'agent :
    - Toujours utiliser cet outil avant toute sauvegarde.
    - Ne jamais inventer de morceaux.
    - Retourner plusieurs résultats si possible.
    - Ne pas bloquer le processus de sauvegarde.
    - Si plusieurs résultats sont trouvés, demander à l'utilisateur
    lequel il souhaite ajouter.
    - Si aucun résultat n'est trouvé, demander une nouvelle recherche.
    """
    try:
        # On vérifie uniquement la blacklist pour ne pas bloquer la recherche
        blacklist = db.read_param(
            "SELECT titre, artiste FROM playlist_didier WHERE mariage_id = ? AND statut_validation = 'Blackliste'", 
            (mariage_id,)
        )

        titres_blacklistes = {(normalize(row[0]), normalize(row[1])) for row in blacklist['data']}

    except Exception as e:
        return {"success": False, "data": None, "error": f"Erreur BDD Blacklist : {str(e)}"}

    try:
        url = "https://itunes.apple.com/search"
        params = {
            "term": terme_recherche.strip(),
            "media": "music",
            "limit": limite + 2, # Marge pour compenser les éventuels fitres
            "lang": "fr_fr"
        }
    
        response = requests.get(url, params=params, timeout=(5, 15))
        response.raise_for_status()
        results = response.json().get("results", [])
        
        morceaux_proposes = []
        for track in results:
            if len(morceaux_proposes) >= limite:
                break
                
            titre = track.get("trackName", "").strip()
            artiste = track.get("artistName", "").strip()
            genre = track.get("primaryGenreName", "Inconnu")
            
            if not titre or not artiste:
                continue
                
            if (normalize(titre), normalize(artiste)) in titres_blacklistes:
                continue

            morceaux_proposes.append({
                "titre": titre,
                "artiste": artiste,
                "genre": genre
            })

        return {
            "success": True,
            "data": {
                "message": f"{len(morceaux_proposes)} morceaux trouvés",
                "tracks": morceaux_proposes
                },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

# ==========================================
# TOOL 2 : SAUVEGARDE SÉCURISÉE (INSERT OR IGNORE)
# ==========================================
@mcp.tool("sauvegarder_morceaux")
def sauvegarder_morceaux(mariage_id: int, morceaux_json: str, moment_diffusion: str = "Soiree") -> dict:
    """
    Ajoute une liste de morceaux à la playlist du mariage pour un moment précis.

    Paramètres:
    - morceaux: Une liste de dictionnaires au format [{"titre": "...", "artiste": "...", "genre": "..."}]
    - moment_diffusion: 'Cocktail', 'Diner' ou 'Soiree'

    UTILISATION :
    - Utiliser après sélection utilisateur OU après résultats de rechercher_morceaux.
    - Il est autorisé et recommandé d'ajouter plusieurs morceaux en un seul appel.

    RÈGLES :
    - Ne jamais inventer de morceaux hors résultats de rechercher_morceaux.
    - Toujours privilégier les appels groupés lorsque possible.
    - Demander confirmation uniquement si plusieurs options existent.

    Comportement :
    - Les morceaux sont enregistrés avec le statut 'Valide'.
    - Les doublons exacts sont ignorés.
    - Les morceaux invalides sont ignorés.
    """
    if moment_diffusion and moment_diffusion not in ['Cocktail', 'Diner', 'Soiree']:
        return {
            "success": False,
            "data": None,
            "error": "Le moment_diffusion doit être soit 'Cocktail', 'Diner' ou 'Soiree'."
        }

    try:
        morceaux = json.loads(morceaux_json)
    except Exception:
        return {
            "success": False,
            "data": None,
            "error": " Le JSON doit être une liste."
        }

    requetes = []
    for m in morceaux:
        if not isinstance(m, dict):
            continue

        titre = m.get("titre")
        artiste = m.get("artiste")
        genre = m.get("genre", "Inconnu")

        if not titre or not artiste:
            continue
        
        if titre and artiste:
            requetes.append((
                """INSERT OR IGNORE INTO playlist_didier 
                    (mariage_id, titre, artiste, genre, moment_diffusion, statut_validation) 
                    VALUES (?, ?, ?, ?, ?, 'Valide')""",
                (mariage_id, titre, artiste, genre, moment_diffusion)
            ))

    if not requetes:
        return {"success": False, "data": None, "error": "Aucun morceau valide trouvé dans la liste."}

    try:
        db.transaction(requetes)
        return {
            "success": True,
            "data": f"Succès : {len(requetes)} morceau(x) injecté(s) ou mis à jour pour le moment '{moment_diffusion}'.",
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "data": None, "error": f"Erreur écriture BDD : {str(e)}"}

# ==========================================
# TOOL 3 : VUE D'ENSEMBLE
# ==========================================
@mcp.tool("resumer_playlist")
def resumer_playlist(mariage_id: int) -> dict:

    """Retourne l'état complet de la playlist d'un mariage segmenté par moment.

    UTILISATION :
    Cet outil doit être utilisé lorsque l'utilisateur demande :
    - de voir la playlist actuelle
    - de connaître les morceaux déjà ajoutés
    - un résumé de la musique du mariage

    SORTIE :
    Retourne un objet structuré :

    {
        "success": bool,
        "data" : {
            "mariage_id": int,
            "playlist": {
                "cocktail": [...],
                "diner": [...],
                "soiree": [...],
                "non_assigne": [...]
            }
        } or None
        "error": str or None
    }

    COMPORTEMENT IMPORTANT POUR L'AGENT :
    - Ceci est une réponse finale de lecture.
    - Ne pas rappeler cet outil plusieurs fois pour la même demande.
    - Ne jamais inventer ou compléter les données retournées.
    - Utiliser directement les données pour répondre à l'utilisateur.
    """
    try:
        lignes = db.read_param(
            "SELECT titre, artiste, genre, moment_diffusion "
            "FROM playlist_didier "
            "WHERE mariage_id = ? AND statut_validation = 'Valide'",
            (mariage_id,)
        )
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

    moments = {
        "cocktail": [],
        "diner": [],
        "soiree": [],
        "non_assigne": []
    }

    if not lignes["ok"] or not lignes["data"]:
        return {"success": True, "data": {"mariage_id": mariage_id, "playlist": moments}, "error": None}

    for titre, artiste, genre, moment in lignes["data"]:
        # Harmonisation des clés en minuscules pour correspondre à l'output attendu
        key = str(moment).lower() if str(moment).lower() in moments else "non_assigne"
        moments[key].append({
            "titre": titre,
            "artiste": artiste,
            "genre": genre
        })

    return {
        "success": True,
        "data": {
            "mariage_id": mariage_id,
            "playlist": moments
        },
        "error": None
    }

if __name__ == "__main__":
    mcp.run()
