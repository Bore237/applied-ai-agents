from pydantic import BaseModel, Field
from typing import List, Literal, TypedDict, Optional

class Ingredient(BaseModel):
    name: str = Field(description="Nom de l'ingrédient manquant")
    quantity: Optional[str] = Field(None, description="Quantité ou proportion manquante si spécifiée (ex: '200g', '1 cuillère à soupe')")

class Recipe(BaseModel):
    title: str = Field(description="Nom de la recette de cuisine")
    match_score: int = Field(description="Score de correspondance de 0 à 100 basé sur les ingrédients possédés")
    justification: str = Field(description="Explication concise du score (ex: 'Il ne vous manque que du lait')")
    ingredients_required: List[str] = Field(description="Liste complète des ingrédients requis pour cette recette")
    instructions: List[str] = Field(description="Étapes de préparation claires et séquentielles")
    ingredients_manquant: List[Ingredient] = Field(description="Ingrédients requis pour la recette qui ne sont pas disponibles dans le frigo ou le texte de l'utilisateur")
    temps_preparation: int = Field(ge=0, description="Temps de préparation estimé en minutes")

class RecipeResponse(BaseModel):
    recipes: List[Recipe] = Field(description="Liste contenant exactement les 3 meilleures recettes sélectionnées")

# Definir etat du graph
class ChefState(TypedDict):
    text_input: str
    image_filepath: Optional[str]
    extracted_ingredients: List[str]
    all_ingredients: List[str]
    raw_search_results: str
    final_recipes: Optional[RecipeResponse]