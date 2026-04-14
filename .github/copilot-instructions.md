# Instructions Copilot — Community

## Projet
Application web Flask simulant un réseau social fictif pour des ateliers d'animation scientifique sur la gestion de crise (Les Petits Débrouillards). Deux groupes communiquent : la Cellule de crise (mairie) et la Population (citoyens). Déployée sur Raspberry Pi, réseau local uniquement, sans internet.

## Stack technique
- **Langage** : Python 3.11+
- **Framework** : Flask 3.x (factory pattern `create_app`)
- **ORM** : SQLAlchemy (Flask-SQLAlchemy)
- **Base de données** : SQLite (`instance/community.db`)
- **Frontend** : HTML5 / CSS3 / HTMX (fichier local, pas de CDN)
- **Templating** : Jinja2
- **Sécurité** : Flask-WTF (CSRF), Flask-Bcrypt (hash code admin), TLS auto-signé (Waitress)
- **Scheduler** : Thread Python natif (`threading.Thread`, daemon=True)
- **Serveur** : Waitress (production LAN)

## Conventions
- **Langue du code** (identifiants, variables, fonctions) : anglais
- **Langue des commentaires et templates** : français
- **Style** : PEP 8, snake_case pour Python, kebab-case pour les classes CSS
- **Imports** : stdlib → third-party → local, séparés par une ligne vide
- **Blueprints Flask** : un blueprint par rôle (`auth`, `admin`, `officiel`, `population`, `htmx`)

## Architecture
```
community/
├── app/
│   ├── __init__.py        # create_app() + init extensions + register blueprints + start scheduler
│   ├── models.py          # Session, Message, Comment, Photo, Config (SQLAlchemy)
│   ├── routes/
│   │   ├── auth.py        # /login, /logout
│   │   ├── admin.py       # /admin/* (photothèque, codes, session)
│   │   ├── officiel.py    # /officiel (page unique feed + rédaction)
│   │   ├── population.py  # /population (page unique feed + rédaction)
│   │   └── htmx.py        # /htmx/* (fragments HTMX pour polling)
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── admin/dashboard.html, photos.html
│   │   ├── officiel/feed.html
│   │   ├── population/feed.html
│   │   └── partials/message_card.html, feed_officiel.html, feed_population.html
│   ├── static/
│   │   ├── css/styles.css
│   │   ├── js/htmx.min.js
│   │   └── photos/<scenario>/  # photothèque persistante
│   └── utils/scheduler.py      # thread daemon publication messages programmés
├── instance/community.db
├── certs/cert.pem, key.pem
├── config.py
├── run.py
└── requirements.txt
```

## Règles importantes
- **Page unique par participant** : feed et zone de rédaction sur la même page (`/officiel`, `/population`)
- **Horodatage fictif** : JAMAIS l'heure système — toujours l'horloge fictive de session
- **Heure fictive affichée** en permanence en haut de chaque interface
- **HTMX polling** toutes les 2 secondes (`hx-trigger="every 2s"`) sur les conteneurs de feed
- **Pas de modification** de message après publication
- **Réponses croisées** : les deux groupes peuvent répondre aux messages de l'autre
- **Photothèque persistante** : jamais effacée lors de la réinitialisation de session
- **CSRF** obligatoire sur tous les formulaires POST
- Utiliser `werkzeug.utils.secure_filename` + préfixe UUID sur tous les uploads
- Valider le type MIME (image/jpeg, image/png, image/webp) côté serveur
- Le code admin est hashé bcrypt ; les codes officiel/population sont en clair (usage pédagogique)
- `SECRET_KEY` générée aléatoirement, jamais codée en dur
