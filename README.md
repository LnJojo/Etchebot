# Etchebot

## Description
Etchebot est un bot Discord conçu pour permettre aux utilisateurs de noter et classer des restaurants avec leurs amis sur un serveur Discord. Inspiré de l'émission "Un dîner presque parfait", Etchebot aide les gens à découvrir et partager des restaurants tout en s'amusant.

## Fonctionnalités
- Ajouter un restaurant avec un lien Google Maps.
- Noter un restaurant avec une note et un commentaire.
- Lancer et arrêter des compétitions de notation de restaurants.
- Afficher le classement des restaurants pour une compétition active.

## Technologies
- Python
- Discord.py
- PostgreSQL

## Installation
### Prérequis
- Python 3.x
- Un serveur PostgreSQL
- Un serveur Discord et un bot Discord (obtenez le token de votre bot depuis le portail des développeurs Discord)

### Étapes d'installation
1. Clonez ce dépôt :
    ```bash
    git clone https://github.com/votre-utilisateur/Etchebot.git
    cd Etchebot
    ```

2. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

3. Configurez les variables d'environnement :
    - `DISCORD_TOKEN`: le token de votre bot Discord
    - `DATABASE_URL`: l'URL de connexion à votre base de données PostgreSQL

4. Démarrez le bot :
    ```bash
    python etchebot.py
    ```

## Utilisation
### Commandes
- `!addResto <nom_du_resto> <lien_google_maps>` : Ajouter un restaurant avec un lien Google Maps.
- `!rateResto <nom_du_resto> <note> [commentaire]` : Noter un restaurant avec une note et un commentaire facultatif.
- `!newCompet` : Lancer une nouvelle compétition de notation.
- `!stopCompet` : Arrêter la compétition actuelle.
- `!rankRestos` : Afficher le classement des restaurants pour la compétition active.

### Exemple
1. Ajouter un restaurant :
    ```bash
    !addResto "Chez Paul" "https://maps.google.com/?q=Chez+Paul"
    ```
    Réponse : `Resto 'Chez Paul' ajouté avec succès.`

2. Noter un restaurant :
    ```bash
    !rateResto "Chez Paul" 4.5 "Très bonne cuisine !"
    ```
    Réponse : `Note de 4.5 pour 'Chez Paul' ajoutée avec commentaire : Très bonne cuisine !`

3. Lancer une nouvelle compétition :
    ```bash
    !newCompet
    ```
    Réponse : `Nouvelle compétition lancée.`

4. Afficher le classement des restaurants :
    ```bash
    !rankRestos
    ```
    Réponse :
    ```
    Classement des restos:
    1. Chez Paul - 4.50
    ```
