# Community — Réseau social fictif pour ateliers de crise

![Python](https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-embarqué-003B57?logo=sqlite&logoColor=white)
![Plateforme](https://img.shields.io/badge/plateforme-Raspberry%20Pi-C51A4A?logo=raspberrypi&logoColor=white)
![Réseau](https://img.shields.io/badge/réseau-LAN%20Wi--Fi%20uniquement-orange)
![Licence](https://img.shields.io/badge/licence-MIT-green)

> Application web pédagogique — simule un réseau social de gestion de crise en réseau local, sans internet.

---

## Table des matières

1. [Présentation du projet](#1-présentation-du-projet)
2. [Prérequis](#2-prérequis)
3. [Installation](#3-installation)
4. [Démarrage de l'application](#4-démarrage-de-lapplication)
5. [Guide de l'animateur](#5-guide-de-lanimateur)
6. [Codes d'accès](#6-codes-daccès)
7. [Connexion des tablettes](#7-connexion-des-tablettes)
8. [Architecture technique](#8-architecture-technique)
9. [Structure des fichiers](#9-structure-des-fichiers)

---

## 1. Présentation du projet

**Community** est une application web déployée sur Raspberry Pi et accessible depuis les tablettes des participants via le Wi-Fi local. Elle simule un réseau social fictif dans le cadre d'ateliers d'animation scientifique sur la **gestion de crise**.

### Contexte pédagogique

Deux groupes de participants jouent des rôles complémentaires durant l'atelier :

| Groupe | Rôle | Interface |
|--------|------|-----------|
| **Cellule de crise** | Élus, services municipaux | `/officiel` |
| **Population** | Citoyens, riverains | `/population` |

- La **Cellule de crise** publie des communiqués officiels, peut joindre des photos et programmer des messages à diffuser à une heure fictive précise.
- La **Population** réagit librement à ces annonces via des commentaires ou ses propres messages.
- Les deux groupes voient les publications de l'autre en temps réel (actualisation automatique toutes les 2 secondes).
- L'**animateur** pilote entièrement la session depuis l'interface d'administration.

### Particularités

- **Horloge fictive** : l'heure affichée dans l'application est indépendante de l'heure réelle — l'animateur configure l'heure de début du scénario.
- **Photothèque persistante** : les photos chargées dans l'application survivent aux réinitialisations de session et sont organisées par scénario.
- **Aucun internet requis** : tout fonctionne en réseau local Wi-Fi.

---

## 2. Prérequis

### Matériel

- Raspberry Pi (modèle 3B+ ou supérieur recommendé) sous **Raspberry Pi OS** (Debian Bookworm)
- Tablettes ou ordinateurs connectés au **même réseau Wi-Fi** que le Raspberry Pi

### Logiciels (Raspberry Pi)

| Logiciel | Version minimale |
|----------|-----------------|
| Python   | 3.11+           |
| pip      | Inclus avec Python |
| openssl  | Pré-installé sur Raspberry Pi OS |
| curl     | Pré-installé sur Raspberry Pi OS |

Vérifier la version de Python :
```bash
python3 --version
```

---

## 3. Installation

L'installation complète se fait en une seule commande grâce au script `setup.sh`.

### Cloner ou transférer le projet

```bash
# Depuis un poste de travail — transfert par clé USB ou SSH
scp -r community/ pi@<ip-du-pi>:~/community
```

### Lancer le script d'installation

```bash
cd community
bash setup.sh
```

Le script effectue automatiquement les 5 étapes suivantes :

| Étape | Action |
|-------|--------|
| 1/5 | Création de l'environnement virtuel Python (`.venv/`) |
| 2/5 | Installation des dépendances Python (`requirements.txt`) |
| 3/5 | Génération du certificat TLS auto-signé (10 ans, RSA 4096) dans `certs/` |
| 4/5 | Création des dossiers nécessaires (`instance/`, `app/static/photos/`, etc.) |
| 5/5 | Initialisation de la base de données SQLite et des codes par défaut |

> **Note :** Si le Raspberry Pi n'a pas d'accès internet lors de l'installation, HTMX ne pourra pas être téléchargé automatiquement (étape 4). Placez manuellement le fichier `htmx.min.js` dans `app/static/js/` avant de lancer le setup, ou téléchargez-le depuis un autre poste : [https://htmx.org/](https://htmx.org/).

---

## 4. Démarrage de l'application

```bash
cd community
source .venv/bin/activate
python run.py
```

L'application détecte automatiquement le mode de démarrage :

| Condition | Mode | Adresse |
|-----------|------|---------|
| `certs/cert.pem` présent | **HTTPS** (production) | `https://0.0.0.0:5443` |
| Certificat absent | HTTP (développement) | `http://0.0.0.0:5000` |

En production (Raspberry Pi après `setup.sh`), l'affichage console sera :

```
Démarrage HTTPS sur https://0.0.0.0:5443
Accès tablettes : https://<ip-du-pi>:5443
```

### Trouver l'adresse IP du Raspberry Pi

```bash
hostname -I
# Exemple de résultat : 192.168.1.42
```

L'accès depuis les tablettes se fera alors sur : `https://192.168.1.42:5443`

---

## 5. Guide de l'animateur

### Avant l'atelier

**1. Récupérer l'adresse IP du Raspberry Pi** et la noter (elle sera communiquée aux participants).

**2. Se connecter à l'interface d'administration** :
```
https://<ip-du-pi>:5443
```
→ Choisir le rôle **Animateur** et saisir le code admin.

**3. Configurer la session** (`/admin`) :
- Choisir ou créer un **dossier de scénario** pour la photothèque.
- Définir l'**heure fictive de début** (ex. `08:30` si le scénario commence à 8h30 du matin fictif).
- Charger les **photos du scénario** dans la photothèque.
- Modifier les **codes d'accès** si nécessaire.

**4. Démarrer la session** en cliquant sur "Configurer et démarrer" dans le tableau de bord.

**5. Distribuer les codes** aux participants :
- Groupe Cellule de crise → code officiel
- Groupe Population → code population

---

### Pendant l'atelier

**Interface Cellule de crise** (`/officiel`) :
- Rédiger et publier des communiqués (texte libre).
- Joindre une photo de la photothèque.
- **Programmer** un message à diffuser à une heure fictive précise (ex. un message qui apparaîtra "dans 10 minutes" d'après l'horloge fictive).
- Répondre aux messages de la population.

**Interface Population** (`/population`) :
- Lire les communiqués officiels.
- Publier des réactions et témoignages.
- Commenter les messages de la cellule de crise.

**Réinitialiser la session** (entre deux ateliers) :
- Depuis `/admin` → bouton "Réinitialiser la session".
- Tous les messages et commentaires sont effacés.
- **La photothèque est conservée** intacte.

---

## 6. Codes d'accès

### Codes par défaut

| Rôle | Code par défaut | Interface |
|------|----------------|-----------|
| Cellule de crise | `MAIRIE2026` | `/officiel` |
| Population | `CITOYEN2026` | `/population` |
| Animateur | `ADMIN2026` | `/admin` |

> **Sécurité :** Le code animateur est stocké hashé en bcrypt. Les codes officiel et population sont en clair dans la base de données (usage pédagogique en réseau local isolé).

### Modifier les codes

Depuis l'interface d'administration (`/admin`) → section **"Codes d'accès"** :
- Modifier le code de la Cellule de crise.
- Modifier le code de la Population.
- Modifier le code animateur.

Les modifications sont immédiatement actives ; les participants déjà connectés restent connectés jusqu'à la fin de leur session navigateur.

---

## 7. Connexion des tablettes

### Procédure pour les participants

1. S'assurer que la tablette est connectée au **même réseau Wi-Fi** que le Raspberry Pi.
2. Ouvrir le navigateur et accéder à :
   ```
   https://<ip-du-pi>:5443
   ```
3. Le navigateur affiche un **avertissement de sécurité** (certificat auto-signé non reconnu par une autorité officielle).
4. Procéder selon le navigateur :
   - **Chrome / Chromium** : cliquer sur "Avancé" → "Continuer vers le site (non sécurisé)"
   - **Firefox** : cliquer sur "Avancé" → "Accepter le risque et continuer"
   - **Safari** : cliquer sur "Afficher les détails" → "Visiter ce site web"

> **Pourquoi cet avertissement ?** Le certificat TLS est auto-signé (généré localement par le script `setup.sh`) et non émis par une autorité de certification reconnue. La connexion est néanmoins chiffrée. Cet avertissement est normal et attendu dans ce contexte.

### Page de connexion

Une fois l'avertissement accepté, les participants arrivent sur la page de connexion. Ils choisissent leur rôle et saisissent le code correspondant.

---

## 8. Architecture technique

### Stack

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Serveur web | Flask 3.x + Waitress | Serveur WSGI, factory pattern `create_app` |
| Base de données | SQLite + Flask-SQLAlchemy | Persistance des messages, sessions, photos |
| Sécurité | Flask-WTF (CSRF) + Flask-Bcrypt | Protection formulaires, hash mot de passe admin |
| Frontend | HTMX + HTML5/CSS3 + Jinja2 | Polling temps réel, rendu serveur |
| TLS | OpenSSL (certificat auto-signé) | Chiffrement HTTPS sur réseau local |
| Scheduler | Thread Python natif (daemon) | Publication automatique des messages programmés |

### Flux de données

```
Tablette participant
       │
       │ HTTPS (port 5443)
       ▼
  Raspberry Pi
  ┌─────────────────────────────────────┐
  │  Flask (run.py)                     │
  │  ┌─────────────────────────────┐    │
  │  │ Blueprints                  │    │
  │  │  auth    → /login, /logout  │    │
  │  │  admin   → /admin/*         │    │
  │  │  officiel→ /officiel        │    │
  │  │  population→ /population    │    │
  │  │  htmx    → /htmx/*          │    │
  │  └──────────┬──────────────────┘    │
  │             │                       │
  │  ┌──────────▼──────────────────┐    │
  │  │ SQLAlchemy ORM              │    │
  │  │  Session / Message /        │    │
  │  │  Comment / Photo / Config   │    │
  │  └──────────┬──────────────────┘    │
  │             │                       │
  │  ┌──────────▼──────────────────┐    │
  │  │ SQLite (community.db)       │    │
  │  └─────────────────────────────┘    │
  │                                     │
  │  Scheduler (thread daemon)          │
  │  Vérification toutes les 5 sec.     │
  │  → publie les messages programmés   │
  └─────────────────────────────────────┘
```

### Horloge fictive

L'horloge fictive est calculée côté serveur à partir de :
- L'**heure fictive de début** configurée par l'animateur (en minutes depuis minuit).
- Le **temps réel écoulé** depuis le démarrage de la session.

```
heure_fictive_actuelle = heure_fictive_début + (maintenant - heure_réelle_démarrage)
```

Aucune heure réelle n'est jamais affichée aux participants.

### Uploads de photos

- Taille maximale : **2 Mo** par fichier.
- Formats acceptés : **JPEG, PNG, WebP** (validés par signature magique côté serveur).
- Nommage sécurisé : préfixe UUID + `secure_filename()`.
- Stockage : `app/static/photos/<nom-du-scénario>/`.

---

## 9. Structure des fichiers

```
community/
├── app/
│   ├── __init__.py            # create_app() : extensions, blueprints, scheduler
│   ├── models.py              # Modèles SQLAlchemy : Session, Message, Comment, Photo, Config
│   ├── routes/
│   │   ├── auth.py            # /login, /logout
│   │   ├── admin.py           # /admin/* (session, photothèque, codes d'accès)
│   │   ├── officiel.py        # /officiel (feed + rédaction + programmation)
│   │   ├── population.py      # /population (feed + rédaction)
│   │   └── htmx.py            # /htmx/* (fragments polling HTMX + commentaires)
│   ├── templates/
│   │   ├── base.html          # Layout commun (horloge fictive, nav)
│   │   ├── login.html         # Page de connexion
│   │   ├── admin/
│   │   │   ├── dashboard.html # Tableau de bord animateur
│   │   │   ├── photos.html    # Gestion de la photothèque
│   │   │   └── config.html    # Configuration session et codes
│   │   ├── officiel/
│   │   │   └── feed.html      # Interface Cellule de crise
│   │   ├── population/
│   │   │   └── feed.html      # Interface Population
│   │   └── partials/
│   │       ├── feed.html      # Fragment HTMX : liste des messages
│   │       ├── message_card.html  # Fragment HTMX : carte d'un message
│   │       └── comments.html  # Fragment HTMX : section commentaires
│   ├── static/
│   │   ├── css/styles.css     # Styles globaux
│   │   ├── js/htmx.min.js     # Bibliothèque HTMX (fichier local, pas de CDN)
│   │   └── photos/            # Photothèque (organisée par dossier de scénario)
│   └── utils/
│       ├── helpers.py         # Décorateur @require_role, utilitaires
│       └── scheduler.py       # Thread daemon : publication messages programmés
├── DOCS/
│   ├── cahier-des-charges.md
│   ├── specifications-fonctionnelles.md
│   ├── specifications-techniques.md
│   └── user-stories.md
├── instance/
│   ├── community.db           # Base de données SQLite (générée au démarrage)
│   └── secret.key             # SECRET_KEY Flask persistée (générée au démarrage)
├── certs/
│   ├── cert.pem               # Certificat TLS auto-signé (généré par setup.sh)
│   └── key.pem                # Clé privée TLS (générée par setup.sh)
├── config.py                  # Configuration Flask (Config class)
├── run.py                     # Point d'entrée : détecte HTTPS/HTTP, démarre le serveur
├── setup.sh                   # Script d'installation Raspberry Pi
└── requirements.txt           # Dépendances Python
```

---

## Licence

MIT
