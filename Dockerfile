FROM searxng/searxng:latest

# On copie le fichier de configuration directement dans l'image
COPY settings.yml /etc/searxng/settings.yml