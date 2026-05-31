import gradio as gr
import base64
from langchain_core.messages import HumanMessage
from src.agent import init_chef_agent

# Initialisation de l'agent au démarrage de l'application
chef_agent = init_chef_agent()
config = {"configurable": {"thread_id": "gradio_session"}}

def predict(text_input, image_input):
    content = []

    # 1. Ajout du texte si présent
    if text_input:
        content.append({"type": "text", "text": text_input})

    # 2. Gestion de l'image (Gradio fournit le chemin du fichier temporaire)
    if image_input is not None:
        with open(image_input, "rb") as image_file:
            img_bytes = image_file.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        content.append({
            "type": "image", 
            "base64": img_b64, 
            "mime_type": "image/png" # Idéalement, détecter dynamiquement le mime_type
        })
        
    if not content:
        return "Veuillez fournir des ingrédients (texte ou image)."

    # 3. Appel de l'agent
    message = HumanMessage(content=content)
    
    # On invoque l'agent (ajuste selon la syntaxe exacte de ton create_agent)
    response = chef_agent.invoke({"messages": [message]}, config=config)
    
    # Extraction de la réponse (dépend de la structure de ton état LangGraph)
    return response["messages"][-1].content

# --- Interface Graphique Gradio ---
with gr.Blocks() as demo:
    gr.Markdown("# 🍳 Chef IA Multimodal - Assistant Recettes")
    
    with gr.Row():
        with gr.Column():
            txt_ingredients = gr.Textbox(label="Ingrédients textuels", placeholder="Ex: Tomates, Oignons, Poulet...")
            img_ingredients = gr.Image(type="filepath", label="Photo de ton frigo / ingrédients")
            btn_submit = gr.Button("Générer la recette", variant="primary")
            
        with gr.Column():
            output_recipe = gr.Markdown(label="Proposition du Chef")
            
    btn_submit.click(
        fn=predict, 
        inputs=[txt_ingredients, img_ingredients], 
        outputs=[output_recipe]
    )

if __name__ == "__main__":
    demo.launch()