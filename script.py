import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
import time
import logging
from bs4 import BeautifulSoup
import datetime
import locale
import requests
from bs4 import BeautifulSoup
import regex
import io
import aiohttp



# Chargement des variables d'environnement contenues dans le fichier .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ID_CANAL = int(os.getenv("ID_CANAL"))

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

locale.setlocale(locale.LC_ALL, 'fr_FR')

# Definition d'un Saint
class Saint:
  def __init__(self, nom, description, url_image):
    self.nom = nom
    self.description = description
    self.url_image = url_image

# Configuration du bot Discord
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration du scheduler
scheduler = AsyncIOScheduler(timezone='Europe/Paris')

@bot.event
async def on_ready():
    logging.info(f"Connecté en tant que {bot.user}")
    
    # Démarrer le scheduler une fois que le bot est prêt
    # scheduler.start()

    await envoi_message_quotidien()

    # Ajouter la tâche planifiée si elle n'existe pas encore
    #scheduler.add_job(envoi_message_quotidien, 'cron', hour=9, minute=0)

async def envoi_message_quotidien():

    # Récupération du canal
    canal = bot.get_channel(ID_CANAL)
    if canal:

        # Récupération du Saint du jour
        saints_du_jour = recuperer_saints_du_jour()

        # Si le Saint du jour existe bien
        for saint_du_jour in saints_du_jour:
            async with aiohttp.ClientSession() as session:
                async with session.get(saint_du_jour.url_image, ssl=False) as resp:
                    if resp.status != 200:
                        return await canal.send('Could not download file...')
                    data = io.BytesIO(await resp.read())
                    await canal.send(file=discord.File(data, f"{saint_du_jour.nom}.png"), content=f"{saint_du_jour.description}" )

def recuperer_saints_du_jour():

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

    # Recherche par Regex de toutes les balises commmencant par St
    regex_balises_saints = regex.compile(r"St.+")
    resultats_recherche_balises_saint = html_parse.find_all(id=regex_balises_saints)
    
    nom_saint = None

    # Je parcours l'ensembe des balises
    for balise_saint in resultats_recherche_balises_saint:

        # Récupération de la date de ce Saint
        date_saint = balise_saint.contents[0]

        # Si la date du Saint correspond à la date du jour
        if date_saint.text == str(7) + " " + nom_du_mois:
            
            description_saint = ""

            for element_suivant in date_saint.next_elements:
                element_texte = element_suivant.text
                if element_texte.strip() == "Retour en haut":
                    break
                if element_texte.strip() != '':
                    if element_suivant.name == "u":
                        nom_saint = element_suivant.text
                    elif element_suivant.name != "i":
                        description_saint += element_texte
            
            print("Le saint du jour est : " + nom_saint)

        # Si le Saint du jour n'a pas été trouvé
        if nom_saint is None:
            next

        # Recherche par Regex de l'image commencant par le mois et le jour
        regex_image_saint = regex.compile(r"img/" + date_jour.strftime('%m') + " " + date_jour.strftime('%d') + ".+")
        balise_image = html_parse.find(src=regex_image_saint)

        url_image = base_url + balise_image.attrs['src']

        saints_du_jour.append(Saint(nom_saint, description_saint, url_image))
    
    return saints_du_jour

bot.run(BOT_TOKEN)