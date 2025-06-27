import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
import logging
from bs4 import BeautifulSoup
import datetime
import locale
import requests
from bs4 import BeautifulSoup
import regex
import io
import aiohttp
from freezegun import freeze_time
from textwrap import wrap

# Definition d'un Saint
class Saint:

  def __init__(self, nom, description, url_image = None):
    self.nom = nom
    self.description = description
    self.url_image = url_image

# Chargement des variables d'environnement contenues dans le fichier .env
load_dotenv()

# Récupération du token du bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Récupération de l'ID du canal dans lequel posté
ID_CANAL = int(os.getenv("ID_CANAL"))

# Configuration du bot Discord
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

logger = logging.getLogger(__name__)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="saint_du_jour.log"
)

# Configuration de la langue
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

# Configuration du scheduler
scheduler = AsyncIOScheduler(timezone='Europe/Paris')

@bot.event
async def on_ready():
    logger.info(f"Connecté en tant que {bot.user}")
    
    # Démarrer le scheduler une fois que le bot est prêt
    scheduler.start()

    # Ajouter la tâche planifiée si elle n'existe pas encore
    scheduler.add_job(envoi_message_quotidien, 'cron', hour=9, minute=0)

async def envoi_message_quotidien():

    # Récupération du canal
    canal = bot.get_channel(ID_CANAL)
    if canal:

        # Récupération du Saint du jour
        saints_du_jour = recuperer_saints_du_jour()

        # Pour chaque Saint du jour ...
        for saint_du_jour in saints_du_jour:
                                
            # Découpage du texte en bloc de 2000 caractères (limite d'envoi de Discord)
            paragraphes = wrap(saint_du_jour.description, 2000)

            # Pour chacun des blocs de 2000 caractères, les envoyer
            for i in range(0, len(paragraphes)):
                await canal.send(paragraphes[i])

            # Envoi de l'image
            if saint_du_jour.url_image is not None:
                # Récupération de l'image du Saint
                async with aiohttp.ClientSession() as session:
                    async with session.get(saint_du_jour.url_image, ssl=False) as resp:
                        if resp.status != 200:
                            return await canal.send('Could not download file...')
                        data = io.BytesIO(await resp.read())
                        await canal.send(file=discord.File(data, f"{saint_du_jour.nom}.png"))

def recuperer_saints_du_jour() -> list[Saint]:

    logger.info('Lancement de la récupération des Saints du jour')

    saints_du_jour = []

    date_jour = datetime.datetime.now()
    nom_du_mois = date_jour.strftime('%B')
    base_url = "https://liguesaintamedee.ch/"
    fin_url = ".html"

    # Construction de l'URL permettant de récuperer les Saints du mois
    url = f"{base_url}saints-{nom_du_mois}{fin_url}"

    # Récupération de la page des Saints du mois
    reponse = requests.get(url, verify=False)

    # Parsage du contenu de la page sous format HTML
    html_parse = BeautifulSoup(reponse.content, "html.parser")

    numero_jour = date_jour.strftime('%d')
    if numero_jour == "01":
        numero_jour = "1er"

    resultats_recherche_balises_saint = html_parse.find_all(string = f"{numero_jour} {nom_du_mois}", name="b")
    
    # Je parcours l'ensembe des balises
    for balise_saint in resultats_recherche_balises_saint:

        # Récupération de la date de ce Saint
        date_saint = balise_saint.contents[0]

        nom_saint = None
        description_saint = ""

        for element_html in date_saint.next_elements:
            element_texte = element_html.text

            # Si on arrive sur le texte " Retour en haut ", c'est qu'on a finit de lire la description de ce saint, on peut passer au suivant
            if element_texte.strip() == "Retour en haut":
                break
            if element_texte.strip() != '':
                if element_html.name == "u":
                    nom_saint = element_html.text
                    logger.info(f"Saint récupéré : {nom_saint}")
                elif element_html.name != "i":
                    description_saint += element_texte
        
        image = html_parse.find(alt=nom_saint, name="img")
        if image:
            url_image = base_url + image.attrs['src']
            saints_du_jour.append(Saint(nom_saint, description_saint, url_image))
        else:
            saints_du_jour.append(Saint(nom_saint, description_saint))

    logger.info(f"Récupération des Saints du jour terminé : {len(saints_du_jour)} récupéré(s)")
    return saints_du_jour

bot.run(BOT_TOKEN)