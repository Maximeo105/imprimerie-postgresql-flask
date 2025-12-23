# imprimerie-postgresql-flask

Ce projet consiste à créer une application de gestion des commandes pour une petite entreprise (imprimerie).

## Démo
<img src="PresentationDuProgramme.gif" width="900" />

## Étapes du projet

1. Normalisation et identification des besoins du client  
   À partir d'un bon de travail, j'ai identifié les attributs, les dépendances, et j'ai clarifié certaines questions avec le client.  
   Ensuite, une normalisation jusqu'en 3NF a été réalisée (voir `Normalisation.md`).

2. Création de la base de données avec PostgreSQL  
   Script complet dans `BaseDeDonneePostgre.sql` (tables, vues, contraintes, trigger, procédure d’archivage, index).

3. Création du site web avec Python/Flask  
   Application dans `ApplicationFlask/imprimerie/` (routes + templates).

## Fonctionnalités (v1)

- Tableau de bord avec statistiques (commandes en retard / en cours) + recherche
- Gestion des clients (liste, détail, création, suppression si aucune commande)
- Gestion des commandes (création, modification, suppression, annulation, complétion)
- Gestion des livraisons (ajout + suppression)
- Page paramètres (types de travail et sous-traitants)

## Lancer le projet (local)

### 1) Créer la DB et exécuter le script SQL
- Créer une base `imprimerie`
- Exécuter `BaseDeDonneePostgre.sql` dans cette base

### 2) Configurer l’environnement
Copier `.env.example` en `.env` dans `ApplicationFlask/imprimerie/` et ajuster :

- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

### 3) Installer et démarrer Flask
```bash
cd ApplicationFlask/imprimerie
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
