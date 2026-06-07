import gradio as gr
from src.agent import ChefAgentContext

def predict(text_input, image_input, model_choice):
    # 1. On initialise le contexte de l'agent avec le modèle choisi par l'utilisateur
    chef_pipeline = ChefAgentContext(model_name=model_choice)
    
    # 2. On lance l'agent (il va décider seul d'appeler l'outil image ou web)
    try:
        recipe_data = chef_pipeline.run(
            text_input=text_input,
            image_filepath=image_input,
            thread_id="session_gradio_1"
        )

        return recipe_data[-1].content
        
    except Exception as e:
        return f"Erreur lors de l'exécution de l'agent : {str(e)}"

# --- Layout Gradio ---
with gr.Blocks() as demo:
    gr.Markdown("# 🍳 Chef Agent - Mode Production ReAct")
    
    with gr.Row():
        with gr.Column():
            txt_in = gr.Textbox(label="Tes ingrédients (texte)")
            img_in = gr.Image(type="filepath", label="Photo de ton frigo")
            model_sel = gr.Dropdown(choices=["gemini-2.5-flash", "llama-3.3-70b"], value="llama-3.3-70b", label="Cerveau de l'agent")
            btn = gr.Button("Générer la recette", variant="primary")
            
        with gr.Column():
            txt_out = gr.Markdown(label="Réponse de l'agent")
            
    btn.click(fn=predict, inputs=[txt_in, img_in, model_sel], outputs=[txt_out])

if __name__ == "__main__":
    demo.launch()