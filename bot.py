import os
import discord
from discord.ext import commands
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# Récupération des informations de connexion
db_url = os.getenv('DATABASE_URL')
bot_token = os.getenv('DISCORD_TOKEN')

# Initialisation du bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Fonction pour obtenir une connexion à la base de données
def get_db_connection():
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)

# Fonction pour exécuter une requête avec gestion d'erreurs
def execute_query(query, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return cur.fetchall()
    except Exception as e:
        print(f"Erreur de base de données : {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

# Création des tables
def create_tables():
    queries = [
        '''CREATE TABLE IF NOT EXISTS restos (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            google_maps_link TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS ratings (
            id SERIAL PRIMARY KEY,
            resto_id INTEGER,
            user_id BIGINT,
            rating FLOAT CHECK (rating >= 0 AND rating <= 5),
            comment TEXT,
            competition_id INTEGER,
            UNIQUE(resto_id, user_id, competition_id),
            FOREIGN KEY(resto_id) REFERENCES restos(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS competitions (
            id SERIAL PRIMARY KEY,
            active BOOLEAN
        )'''
    ]
    for query in queries:
        execute_query(query)

create_tables()

@bot.command(name='addResto')
async def add_resto(ctx, resto_name, google_maps_link):
    try:
        execute_query("INSERT INTO restos (name, google_maps_link) VALUES (%s, %s)", (resto_name, google_maps_link))
        await ctx.send(f"Resto '{resto_name}' ajouté avec succès.")
    except psycopg2.errors.UniqueViolation:
        await ctx.send(f"Le resto '{resto_name}' existe déjà.")
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {str(e)}")

@bot.command(name='rateResto')
async def rate_resto(ctx, resto_name, rating: float, *, comment=""):
    if not 0 <= rating <= 5:
        await ctx.send("La note doit être entre 0 et 5.")
        return

    try:
        resto = execute_query("SELECT id FROM restos WHERE name = %s", (resto_name,))
        if not resto:
            await ctx.send(f"Resto '{resto_name}' non trouvé.")
            return

        resto_id = resto[0]['id']
        competition = execute_query("SELECT id FROM competitions WHERE active = TRUE")
        if not competition:
            await ctx.send("Aucune compétition active. Lance une nouvelle compétition avec !newCompet.")
            return

        competition_id = competition[0]['id']
        
        # Vérifier si l'utilisateur a déjà noté ce restaurant dans cette compétition
        existing_rating = execute_query(
            "SELECT id FROM ratings WHERE resto_id = %s AND user_id = %s AND competition_id = %s",
            (resto_id, ctx.author.id, competition_id)
        )
        if existing_rating:
            await ctx.send("Vous avez déjà noté ce restaurant dans cette compétition.")
            return

        execute_query(
            "INSERT INTO ratings (resto_id, user_id, rating, comment, competition_id) VALUES (%s, %s, %s, %s, %s)",
            (resto_id, ctx.author.id, rating, comment, competition_id)
        )
        await ctx.send(f"Note de {rating} pour '{resto_name}' ajoutée avec commentaire : {comment}")
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {str(e)}")

@bot.command(name='newCompet')
async def new_competition(ctx):
    try:
        execute_query("UPDATE competitions SET active = FALSE WHERE active = TRUE")
        execute_query("INSERT INTO competitions (active) VALUES (TRUE)")
        await ctx.send("Nouvelle compétition lancée.")
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {str(e)}")

@bot.command(name='stopCompet')
async def stop_competition(ctx):
    try:
        execute_query("UPDATE competitions SET active = FALSE WHERE active = TRUE")
        await ctx.send("Compétition arrêtée.")
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {str(e)}")

@bot.command(name='rankRestos')
async def rank_restos(ctx):
    try:
        competition = execute_query("SELECT id FROM competitions WHERE active = TRUE")
        if not competition:
            await ctx.send("Aucune compétition active. Lance une nouvelle compétition avec !newCompet.")
            return

        competition_id = competition[0]['id']
        rankings = execute_query('''
            SELECT r.name, AVG(rt.rating) as avg_rating, COUNT(rt.id) as vote_count
            FROM ratings rt
            JOIN restos r ON rt.resto_id = r.id
            WHERE rt.competition_id = %s
            GROUP BY rt.resto_id, r.name
            ORDER BY avg_rating DESC
        ''', (competition_id,))

        if not rankings:
            await ctx.send("Aucune note pour la compétition actuelle.")
            return

        ranking_message = "Classement des restos:\n"
        for i, resto in enumerate(rankings, start=1):
            ranking_message += f"{i}. {resto['name']} - {resto['avg_rating']:.2f} (Votes: {resto['vote_count']})\n"
        await ctx.send(ranking_message)
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {str(e)}")

@bot.command(name='podium')
async def show_podium(ctx):
    try:
        competition = execute_query("SELECT id FROM competitions WHERE active = FALSE ORDER BY id DESC LIMIT 1")
        if not competition:
            await ctx.send("Aucune compétition terminée.")
            return

        competition_id = competition[0]['id']
        podium = execute_query('''
            SELECT r.name, AVG(rt.rating) as avg_rating
            FROM ratings rt
            JOIN restos r ON rt.resto_id = r.id
            WHERE rt.competition_id = %s
            GROUP BY rt.resto_id, r.name
            ORDER BY avg_rating DESC
            LIMIT 3
        ''', (competition_id,))

        if not podium:
            await ctx.send("Pas de résultats pour la dernière compétition.")
            return

        podium_message = "Podium de la dernière compétition:\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, resto in enumerate(podium):
            podium_message += f"{medals[i]} {resto['name']} - {resto['avg_rating']:.2f}\n"
        await ctx.send(podium_message)
    except Exception as e:
        await ctx.send(f"Une erreur est survenue : {str(e)}")

# Démarrer le bot Discord
bot.run(bot_token)