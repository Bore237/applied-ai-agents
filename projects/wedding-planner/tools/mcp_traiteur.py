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

def get_or_create_meal_price(meal_id: str, meal_name: str, category: str) -> float:
    row = db.read_param( """SELECT prix_unitaire FROM menus_prix  WHERE meal_id = ?""",
                            (meal_id,)
    )

    if row.get("ok") and row.get("data"):
        return float(row["data"]["prix_unitaire"])

    default_price = PRIX_CATEGORIES.get(category, 20)
    db.write_param("""INSERT INTO menus_prix (meal_id, meal_name, category, prix_unitaire)
                    VALUES (?, ?, ?, ?)
                    """,
                    (meal_id, meal_name, category, default_price)
    )

    return default_price

def fetch_meals(category: str):
    """
    Récupère les plats d'une catégorie TheMealDB.
    """
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    meals = response.json().get("meals") or []
    results = []

    for meal in meals:
        meal_id = meal["idMeal"]
        meal_name = meal["strMeal"]

        #price = get_or_create_meal_price(meal_id, meal_name, category)

        results.append({
            "id": meal["idMeal"],
            "name": meal["strMeal"],
            "thumbnail": meal.get("strMealThumb"),
            "category": category,
            "price": PRIX_CATEGORIES.get(category, 20.0)
        })

    return results


@mcp.tool(name="modifier_prix_plat")
def modifier_prix_plat(meal_id: str, nouveau_prix: float):
    db.write_param("""UPDATE menus_prix SET prix_unitaire = ?, updated_at = CURRENT_TIMESTAMP WHERE meal_id = ? """,
        (nouveau_prix,  meal_id)
    )

    return "Prix mis à jour"

@mcp.tool(name="obtenir_menus_traiteur", 
        description="""
            Génère un menu traiteur réaliste à partir de TheMealDB.
            Styles disponibles : (viande, gourmet, vegetarien, cocktail).
            Le système récupère plusieurs catégories, fusionne les plats, mélange aléatoirement,
            conserve 10 propositions, calcule le coût global et enregistre le budget.
        """)
def obtenir_menus_traiteur(style_menu: str, mariage_id: int, nombre_invites: int) -> str:
    """
    Recherche des propositions de menus adaptées aux contraintes des invités (ex: 'vege', 'viande', 'poisson')
    et calcule automatiquement le devis global pour le budget du mariage.
    """

    style = style_menu.lower().strip()
    if style not in MENU_STYLES:
        return (f"❌ Style '{style_menu}' inconnu.\n\n"
            f"Styles disponibles : {', '.join(MENU_STYLES.keys())}"
        )

    categories = MENU_STYLES[style]
    all_meals = []

    try:
        # 1. Appels API multiples
        for category in categories:
            try:
                meals = fetch_meals(category)
                all_meals.extend(meals)
            except Exception as api_err:
                # Si une API de catégorie flanche, on logge mais on n'arrête pas tout le processus
                print(f"⚠️ Erreur catégorie {category}: {str(api_err)}", file=sys.stderr)
                continue

        if not all_meals:
            return f"❌ Aucun plat n'a pu être récupéré depuis le catalogue culinaire. {all_meals}"

        # 2. Mélange aléatoire
        random.shuffle(all_meals)

        # 3. Sélection des 10 premiers
        selected_meals = all_meals[:10]

        # 4. Calcul du coût moyen du menu
        prix_moyen_menu = sum(meal["price"] for meal in selected_meals) / len(selected_meals)

        # 5. Coût total mariage
        cout_total = prix_moyen_menu * nombre_invites

        # 6. Sauvegarde du budget
        intitule_depense = (f"Traiteur {style.capitalize()} ({nombre_invites} invités)")

        write_out = db.transaction([("""
                INSERT INTO budget_depenses (mariage_id, categorie, intitule, montant_estime, statut)
                VALUES (?, 'Traiteur', ?, ?, 'Prevu')
                """,
                (mariage_id, intitule_depense, cout_total)
            )
        ])

        # Gestion du cas où l'écriture du budget échoue ou renvoie False
        if not write_out or not write_out.get('ok'):
            return "❌ Échec de l'opération : Impossible d'enregistrer l'estimation dans le module Budget."
        
        # 7. Sauvegarde des plats retenus
        transactions = []
        for meal in selected_meals:

            transactions.append(("""
                INSERT INTO menus_traiteur (mariage_id, nom_plat, categorie, cout_unitaire, source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (mariage_id, meal["name"], meal["category"], meal["price"], "TheMealDB")
            ))

        db.transaction(transactions)

        # 8. Réponse utilisateur
        output = [
            f"🍽️ **MENU {style.upper()} — {nombre_invites} invités**",
            f"Voici les 10 propositions sélectionnées pour votre buffet :\n"
        ]

        for i, meal in enumerate(selected_meals, start=1):
            output.append(f"{i}. {meal['name']} *({meal['category']})* — {meal['price']}€/pers")

        output.extend([
            "",
            f"💰 **Prix moyen constaté :** {prix_moyen_menu:.2f}€ / personne",
            f"💰 **Coût total estimé :** {cout_total:.2f}€",
            "✅ *Le devis prévisionnel a été automatiquement injecté et validé dans votre budget.*"
        ])

        return "\n".join(output)

    except Exception as e:
        return f"❌ Erreur critique lors de la génération du menu : {str(e)}"

if __name__ == "__main__":
    mcp.run()