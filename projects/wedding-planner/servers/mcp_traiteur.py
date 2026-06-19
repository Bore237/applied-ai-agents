# mcp_traiteur.py
import sys
import requests
from mcp.server.fastmcp import FastMCP
import random
from server import db

mcp = FastMCP("Wedding_Catering_Server")

PRIX_CATEGORIES = {
    "Beef": 28,
    "Chicken": 22,
    "Seafood": 35,
    "Vegetarian": 20,
    "Vegan": 19,
    "Lamb": 30,
    "Pork": 24,
    "Pasta": 18,
    "Starter": 12,
}

MENU_STYLES = {
    "viande": ["Beef", "Chicken", "Pork"],
    "gourmet": ["Beef", "Seafood", "Lamb"],
    "vegetarien": ["Vegetarian", "Vegan", "Pasta"],
    "cocktail": ["Starter", "Seafood", "Chicken"]
}

def fetch_meals(category: str) -> list[dict]:
    """Récupère les plats d'une catégorie depuis l'API externe TheMealDB."""
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    meals = response.json().get("meals") or []
    
    results = []
    for meal in meals:
        if not meal.get("idMeal") or not meal.get("strMeal"):
            continue

        results.append({
            "id": meal["idMeal"],
            "name": meal["strMeal"],
            "category": category,
            "price": PRIX_CATEGORIES.get(category, 20.0),
            "thumbnail": meal.get("strMealThumb")
        })
    return results

@mcp.tool(name="modifier_prix_plat")
def modifier_prix_plat(meal_id: str, nouveau_prix: float) -> dict:
    """Met à jour le prix unitaire d'un plat spécifique en base de données."""
    
    try:
        write_out = db.write_param(
            "UPDATE menus_prix SET prix_unitaire = ?, updated_at = CURRENT_TIMESTAMP WHERE meal_id = ?",
            (nouveau_prix, meal_id)
        )
        if not write_out.get("ok"):
            return {"success": False, "data": None, "error": "Échec de la mise à jour du prix en base."}
            
        return {"success": True, "data": {"meal_id": meal_id, "nouveau_prix": nouveau_prix}, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


@mcp.tool(name="obtenir_menus_traiteur")
def obtenir_menus_traiteur(style_menu: str, mariage_id: int, nombre_invites: int, limit_nombre_plat: int = 15) -> dict:
    """
    Génère une proposition de `limit_nombre_plat` de plats, calcule les coûts de revient, 
    et inscrit de façon atomique la dépense globale et les plats associés en BDD.
    """

    style = style_menu.lower().strip()
    if style not in MENU_STYLES:
        return {
            "success": False, 
            "data": None, 
            "error": f"Style '{style_menu}' invalide. Styles autorisés: {list(MENU_STYLES.keys())}"
        }

    categories = MENU_STYLES[style]
    all_meals = []

    # 1. Collecte des données de l'API externe
    for category in categories:
        try:
            all_meals.extend(fetch_meals(category))
        except Exception as api_err:
            print(f"Erreur récupération catégorie {category}: {str(api_err)}", file=sys.stderr)
        continue

    if not all_meals:
        return {"success": False, "data": None, "error": "Le catalogue culinaire distant est inaccessible."}
    
    # 2. Échantillonnage déterministe (10 plats maximum)
    random.shuffle(all_meals)
    selected_meals = all_meals[:limit_nombre_plat]

    # 3. Traitement mathématique des coûts
    prix_moyen_menu = sum(meal["price"] for meal in selected_meals) / len(selected_meals)
    cout_total = prix_moyen_menu * nombre_invites

    # 4. Construction de la TRANSACTION UNIQUE (Garantit l'intégrité de la BDD (ACID))
    intitule_depense = f"Traiteur {style.capitalize()} ({nombre_invites} invités)"

    # Requête A : Le Budget global
    requetes_sql = [
    ("""INSERT INTO budget_depenses (mariage_id, categorie, intitule, montant_estime, statut)
        VALUES (?, 'Traiteur', ?, ?, 'Prevu')
    """, (mariage_id, intitule_depense, cout_total))
    ]

    # Requêtes B : L'ensemble des plats retenus
    # 7. Sauvegarde des plats retenus
    for meal in selected_meals:
        requetes_sql.append((
            """
                INSERT INTO menus_traiteur (mariage_id, nom_plat, categorie, cout_unitaire)
                VALUES (?, ?, ?, ?)
            """, (mariage_id, meal["name"], meal["category"], meal["price"])
        ))

    try:
        # Exécution de la transaction unifiée
        execution = db.transaction(requetes_sql)
        if not execution or not execution.get('ok'):
            return {"success": False, "data": None, "error": "Échec de l'écriture atomique en base de données."}
        
        # 5. Retour de la donnée brute standardisée
        return {
            "success": True,
            "data": {
                "mariage_id": mariage_id,
                "style_applique": style,
                "nombre_invites": nombre_invites,
                "prix_moyen_par_personne": round(prix_moyen_menu, 2),
                "cout_total_estime": round(cout_total, 2),
                "plats": [{"nom": m["name"], "categorie": m["category"], "prix": m["price"]} for m in selected_meals]
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "data": None, "error": f"Erreur critique BDD : {str(e)}"}

if __name__ == "__main__":
    mcp.run()