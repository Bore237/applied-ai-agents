# tests/test_agent.py
import unittest
from unittest.mock import MagicMock, patch
from src.agent import ChefAgentGraph
from src.schemas import RecipeResponse, Recipe, Ingredient

class TestChefAgentGraph(unittest.TestCase):

    @patch('src.agent.ChatGoogleGenerativeAI')
    @patch('src.agent.get_tools')
    def test_pipeline_linear_with_new_fields(self, mock_get_tools, mock_gemini):
        mock_search = MagicMock()
        mock_search.invoke.return_value = "Mock Web Results"
        mock_get_tools.return_value = mock_search

        bot = ChefAgentGraph(model_name="llama-3.3-70b", db_path=":memory:")

        # Simulation du nouveau format avec ingrédients manquants et temps de préparation
        fake_recipe = Recipe(
            title="Omelette Express",
            match_score=80,
            justification="Il vous manque juste de la ciboulette.",
            ingredients_required=["2 Oeufs", "Sel", "Ciboulette"],
            instructions=["Battre les oeufs.", "Parsemer de ciboulette."],
            ingredients_manquant=[Ingredient(name="Ciboulette", quantity="3 brins")],
            temps_preparation=10
        )
        fake_response = RecipeResponse(recipes=[fake_recipe])
        
        markdown_result = bot.format_to_markdown(fake_response)

        # Vérification de la présence des nouveaux éléments de l'UI
        self.assertIn("**Temps de préparation :** 10 min", markdown_result)
        self.assertIn("À acheter / Ingrédients manquants :", markdown_result)
        self.assertIn("Ciboulette", markdown_result)
        self.assertIn("3 brins", markdown_result)

if __name__ == '__main__':
    unittest.main()