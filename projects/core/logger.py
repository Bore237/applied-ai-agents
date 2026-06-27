import os
import sys
import logging

# Format du message : Heure - Niveau - Nom du script - Message
logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"

log_dir = "./logs"
log_filepath = os.path.join(log_dir, "running_logs.log")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=logging_str,
    handlers=[
        logging.FileHandler(log_filepath), # Écrit dans le fichier
        logging.StreamHandler(sys.stdout)  # Affiche dans la console
    ],
    force=True 
)

def logger(name: str):
    return logging.getLogger(name)