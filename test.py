import datetime
import locale
import requests
from bs4 import BeautifulSoup
import regex

locale.setlocale(locale.LC_ALL, 'fr_FR')

date_jour = datetime.datetime.now()

nom_du_mois = date_jour.strftime('%B')
base_url = "https://liguesaintamedee.ch/"
fin_url = ".html"
url = f"{base_url}saints-{nom_du_mois}{fin_url}"

reponse = requests.get(url, verify=False)
soup = BeautifulSoup(reponse.content, "html.parser")

look_for = regex.compile(r"St.+")

results = soup.findAll(id=look_for)

for resultat in results:
    date_saint = resultat.contents[0]
    if date_saint.text == str(date_jour.day) + " " + nom_du_mois:
        for element_suivant in date_saint.next_elements:
            element_texte = element_suivant.text.strip()
            if element_texte == "Retour en haut":
                break
            if element_texte != '':
                print(element_texte)
        print("Le saint du jour est : " + resultat.next_element.next_element.next_element.next_element.text)