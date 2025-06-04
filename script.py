import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement contenues dans le fichier .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ID_CANAL = int(os.getenv("ID_CANAL"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler(timezone='Europe/Paris')

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    
    # Démarrer le scheduler une fois que le bot est prêt
    scheduler.start()

    await envoi_message_quotidien()

    # Ajouter la tâche planifiée si elle n'existe pas encore
    #scheduler.add_job(envoi_message_quotidien, 'cron', hour=9, minute=0)

async def envoi_message_quotidien():
    canal = bot.get_channel(ID_CANAL)
    if canal:
        await canal.send("C'est l'heure du message quotidien ☀️")



bot.run(BOT_TOKEN)