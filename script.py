from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
import os
import requests
import logging
from textwrap import wrap

BASE_URL = "https://liguesaintamedee.ch/"

# Definition d'un Saint
class Saint:

  def __init__(self, nom, description, url_image = None):
    self.nom = nom
    self.description = description
    self.url_image = url_image

# Chargement des variables d'environnement contenues dans le fichier .env
load_dotenv()

API_URL = os.getenv("API_URL")

# Récupération de l'URL du webhook discord
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Récupération du token du bot Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Récupération de l'identifiant du chat Telegram
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configuration du logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="saint_du_jour.log"
)

def recuperer_saints_du_jour() -> list[Saint]:

    logger.info('Lancement de la récupération des Saints du jour')

    r = requests.get(API_URL)
    return r.json()

def envoyer_saint_du_jour_discord(saints_du_jour):

    if len(saints_du_jour) == 0:
        DiscordWebhook(url=DISCORD_WEBHOOK_URL, content="Oups ! 0 Saint trouvé aujourd'hui ! Mais que fais le X solide et crémeux à la fois ?").execute()

    # Récupération des Saints du jour
    for saint in saints_du_jour:
        # Découpage du texte en bloc de 2000 caractères (limite d'envoi de Discord)
        paragraphes = wrap(saint['description'], 2000)

        # Pour chacun des blocs de 2000 caractères, les envoyer
        for paragraphe in paragraphes:
            # Création et execution d'un webhook contenant le paragraphe 
            DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=paragraphe).execute()

        # Si le Saint du jour possède une image
        if saint['image'] is not None:
            
            # Téléchargement de l'image du Saint
            reponse = requests.get(saint['image'])

            # Si le téléchargement est OK
            if reponse.ok:

                # Création et execution d'un webhook contenant l'image
                webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
                webhook.add_file(reponse.content, saint['nom'] + ".jpg")
                webhook.execute()

def envoyer_saint_du_jour_telegram(saints_du_jour: list[Saint]):

    base_url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
    url_message = base_url_telegram + "sendMessage"
    url_photo = base_url_telegram + "sendPhoto"

    for saint in saints_du_jour:

        if saint.url_image is not None:
            payload_photo = {"chat_id": TELEGRAM_CHAT_ID, "photo": saint.url_image}
            requests.post(url_photo, json=payload_photo)
        
        payload_text = {"chat_id": TELEGRAM_CHAT_ID, "text": saint.description}
        requests.post(url_message, json=payload_text)

saints_du_jour = recuperer_saints_du_jour()

envoyer_saint_du_jour_discord(saints_du_jour)
#envoyer_saint_du_jour_telegram(saints_du_jour)