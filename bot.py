import os
import discord
from discord.ext import commands
import psycopg2

# Récupérer les informations de connexion depuis les variables d'environnement
db_url = os.getenv('DATABASE_URL')  # Assurez-vous que cette variable correspond à l'URL de votre base de données PostgreSQL sur Railway
# Récupérer le token du bot à partir de la variable d'environnement
bot_token = os.getenv('DISCORD_TOKEN')

# Initialisation du bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Connexion à la base de données PostgreSQL
conn = psycopg2.connect(db_url)
c = conn.cursor()

# Création des tables si elles n'existent pas déjà
c.execute('''CREATE TABLE IF NOT EXISTS restos (
             id SERIAL PRIMARY KEY,
             name TEXT,
             google_maps_link TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS ratings (
             id SERIAL PRIMARY KEY,
             resto_id INTEGER,
             user_id BIGINT,
             rating FLOAT,
             comment TEXT,
             competition_id INTEGER,
             FOREIGN KEY(resto_id) REFERENCES restos(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS competitions (
             id SERIAL PRIMARY KEY,
             active INTEGER)''')

conn.commit()

# Commande pour ajouter un resto avec lien Google Maps
@bot.command(name='addResto')
async def add_resto(ctx, resto_name, google_maps_link):
    # Insérer le resto dans la base de données
    c.execute("INSERT INTO restos (name, google_maps_link) VALUES (%s, %s)", (resto_name, google_maps_link))
    conn.commit()
    await ctx.send(f"Resto '{resto_name}' ajouté avec succès.")

# Commande pour noter un resto
@bot.command(name='rateResto')
async def rate_resto(ctx, resto_name, rating: float, *, comment=""):
    c.execute("SELECT id FROM restos WHERE name = %s", (resto_name,))
    resto_id = c.fetchone()
    if resto_id:
        c.execute("SELECT id FROM competitions WHERE active = 1")
        competition_id = c.fetchone()
        if competition_id:
            c.execute("INSERT INTO ratings (resto_id, user_id, rating, comment, competition_id) VALUES (%s, %s, %s, %s, %s)",
                      (resto_id[0], ctx.author.id, rating, comment, competition_id[0]))
            conn.commit()
            await ctx.send(f"Note de {rating} pour '{resto_name}' ajoutée avec commentaire : {comment}")
        else:
            await ctx.send("Aucune compétition active. Lance une nouvelle compétition avec !newCompetition.")
    else:
        await ctx.send(f"Resto '{resto_name}' non trouvé.")

# Commande pour lancer une nouvelle compétition
@bot.command(name='newCompet')
async def new_competition(ctx):
    c.execute("UPDATE competitions SET active = 0 WHERE active = 1")
    c.execute("INSERT INTO competitions (active) VALUES (1)")
    conn.commit()
    await ctx.send("Nouvelle compétition lancée.")

# Commande pour arrêter une compétition
@bot.command(name='stopCompet')
async def stop_competition(ctx):
    c.execute("UPDATE competitions SET active = 0 WHERE active = 1")
    conn.commit()
    await ctx.send("Compétition arrêtée.")

# Commande pour afficher le classement des restos
@bot.command(name='rankRestos')
async def rank_restos(ctx):
    c.execute("SELECT id FROM competitions WHERE active = 1")
    competition_id = c.fetchone()
    if competition_id:
        c.execute('''SELECT r.name, AVG(rt.rating) as avg_rating
                     FROM ratings rt
                     JOIN restos r ON rt.resto_id = r.id
                     WHERE rt.competition_id = %s
                     GROUP BY rt.resto_id
                     ORDER BY avg_rating DESC''', (competition_id[0],))
        rankings = c.fetchall()
        if rankings:
            ranking_message = "Classement des restos:\n"
            for i, (name, avg_rating) in enumerate(rankings, start=1):
                ranking_message += f"{i}. {name} - {avg_rating:.2f}\n"
            await ctx.send(ranking_message)
        else:
            await ctx.send("Aucune note pour la compétition actuelle.")
    else:
        await ctx.send("Aucune compétition active. Lance une nouvelle compétition avec !newCompetition.")

# Démarrer le bot Discord
bot.run(bot_token)

# Fermer la connexion à la base de données PostgreSQL
conn.close()
