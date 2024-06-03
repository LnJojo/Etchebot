# Utiliser l'image officielle Python comme image de base
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers requirements.txt et installer les dépendances
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu de votre projet dans le répertoire de travail du conteneur
COPY . .

# Définir les variables d'environnement pour PostgreSQL
ENV DATABASE_URL=${DATABASE_URL}
ENV DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}

# Commande pour démarrer le bot
CMD ["python", "bot.py"]
