from discord_webhook import DiscordWebhook
import datetime
from dotenv import load_dotenv
import os
import requests
import logging
from bs4 import BeautifulSoup
import locale
from textwrap import wrap
from unidecode import unidecode

BASE_URL = "https://liguesaintamedee.ch/"

# Definition d'un Saint
class Saint:

  def __init__(self, nom, description, url_image = None):
    self.nom = nom
    self.description = description
    self.url_image = url_image

# Chargement des variables d'environnement contenues dans le fichier .env
load_dotenv()

# Récupération du token du bot
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Configuration du logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="saint_du_jour.log"
)

# Configuration de la langue
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

def recuperer_page_saints_du_mois(nom_du_mois) -> BeautifulSoup:
    # Construction de l'URL permettant de récuperer les Saints du mois
    url = f"{BASE_URL}saints-{unidecode(nom_du_mois)}.html"

    # Récupération de la page des Saints du mois
    reponse = requests.get(url, verify=False)

    if not reponse.ok:
        raise RuntimeError(f"Erreur HTTP {reponse.status_code} en récupérant {url}")

    return BeautifulSoup(reponse.content, "html.parser")

def recuperer_url_image_saint_du_jour(page_web, nom_saint) -> str:
    return page_web.find(alt=nom_saint, name="img")

def recuperer_saints_du_jour() -> list[Saint]:

    logger.info('Lancement de la récupération des Saints du jour')

    saints_du_jour = []

    date_jour = datetime.datetime.now()
    nom_du_mois = date_jour.strftime('%B')
    
    try:
        html_parse = recuperer_page_saints_du_mois(nom_du_mois)
    except Exception as e:
        logger.error(f"Impossible de récupérer la page des saints : {e}")
        return []  # le script continue, mais vide

    numero_jour = '{dt.day}'.format(dt = date_jour)
    if numero_jour == "1":
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

        saint_du_jour = Saint(nom_saint, description_saint)

        # Recherche de l'image du Saint
        image = recuperer_url_image_saint_du_jour(html_parse, nom_saint)

        # Si elle existe ...
        if image:

            # L'ajouter au sein du jour
            saint_du_jour.url_image = BASE_URL + image.attrs['src']

        saints_du_jour.append(saint_du_jour)

    logger.info(f"Récupération des Saints du jour terminé : {len(saints_du_jour)} récupéré(s)")
    return saints_du_jour

saints_du_jour = recuperer_saints_du_jour()

if len(saints_du_jour) == 0:
    DiscordWebhook(url=WEBHOOK_URL, content="Oups ! 0 Saint trouvé aujourd'hui ! Mais que fais le X solide et crémeux à la fois ?").execute()

# Récupération des Saints du jour
for saint in saints_du_jour:
     # Découpage du texte en bloc de 2000 caractères (limite d'envoi de Discord)
    paragraphes = wrap(saint.description, 2000)

    # Pour chacun des blocs de 2000 caractères, les envoyer
    for paragraphe in paragraphes:
        # Création et execution d'un webhook contenant le paragraphe 
        DiscordWebhook(url=WEBHOOK_URL, content=paragraphe).execute()

    # Si le Saint du jour possède une image
    if saint.url_image is not None:
        
        # Téléchargement de l'image du Saint
        reponse = requests.get(saint.url_image)

        # Si le téléchargement est OK
        if reponse.ok:

            # Création et execution d'un webhook contenant l'image
            webhook = DiscordWebhook(url=WEBHOOK_URL)
            webhook.add_file(reponse.content, saint.nom + ".jpg")
            webhook.execute()