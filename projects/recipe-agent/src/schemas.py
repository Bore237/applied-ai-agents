from pydantic import BaseModel, Field
from typing import List, Literal, TypedDict, Optional



class Ingredient(BaseModel):
    name: str = Field(..., description="Name of the ingredient")
    quantity: str | None = Field(
        default=None,
        description="Optional quantity (e.g., '200g', '2 tbsp', '1 unit')"
    )


class RecipeResponse(BaseModel):
    dish_name: str = Field(
        ...,
        description="Name of the final dish"
    )

    justification: str = Field(
        ...,
        description="Why this recipe is the best choice compared to other possible dishes"
    )

    ingredients_used: List[Ingredient] = Field(
        ...,
        description="List of ingredients used in the recipe with quantities when available"
    )

    missing_ingredients: List[Ingredient] = Field(
        ...,
        description="Ingredients required for the recipe that are not available"
    )

    steps: List[str] = Field(
        ...,
        description="Step-by-step cooking instructions in logical order"
    )

    prep_time_minutes: int = Field(
        ...,
        ge=0,
        description="Preparation time in minutes"
    )

    cook_time_minutes: int = Field(
        ...,
        ge=0,
        description="Cooking time in minutes"
    )

    difficulty: Literal["easy", "medium", "hard"] = Field(
        ...,
        description="Difficulty level of the recipe"
    )
