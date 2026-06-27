import os
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools.google import GmailTool

work_dir = os.path.dirname(__file__)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
server_path = os.path.join(project_root, "server", "mcp_gmail.py")
gmail_tool = GmailTool(os.path.join(work_dir, 'secret.json'))

mcp = FastMCP(
    'Gmail',
    dependencies=[
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib'
    ],
)

mcp.add_tool(gmail_tool.send_email, name='Gmail-Send-Email', description="Envoie un e-mail. Assure-toi de fournir le destinataire ('to'), le sujet et le corps ('body'). Ne l'utilise pas pour répondre, seulement pour de nouveaux e-mails.")
mcp.add_tool(gmail_tool.get_email_message_details, name='Gmail-Get-Email-Message-Details', description="Obtient les métadonnées détaillées d'un e-mail (comme l'expéditeur, la date, l'objet et les dossiers/labels). REQUIERT un 'msg_id' valide obtenu au préalable via 'Gmail-Search-Emails'.")
mcp.add_tool(gmail_tool.get_email_message_body, name='Get-Email-Message-Body', description="Obtient le contenu d'un e-mail. REQUIERT un 'msg_id' valide obtenu au préalable via 'Gmail-Search-Emails'.")
mcp.add_tool(gmail_tool.search_emails, name='Gmail-Search-Emails', description="Recherche des e-mails. Retourne une liste contenant les 'msg_id'")
mcp.add_tool(gmail_tool.delete_email_message, name='Gmail-Delete-Email-Message', description="Supprime un e-mail de façon permanente. REQUIERT un 'msg_id' valide. Ne l'utilise que si l'utilisateur a explicitement demandé une suppression.")

if __name__ == "__main__":
    mcp.run()