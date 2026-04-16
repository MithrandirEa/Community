# Poneglyphe — Synthèse du projet Community

> **Projet** : Community  
> **Auteur** : Les Petits Débrouillards / Mithrandir  
> **Date de synthèse** : 15 avril 2026  
> **Branche analysée** : `development`  
> **Statut** : En développement actif

---

## Table des matières

1. [Rôle et objectif](#1-rôle-et-objectif)
2. [Architecture et modules](#2-architecture-et-modules)
3. [Modèle de données](#3-modèle-de-données)
4. [Flux principal](#4-flux-principal)
5. [Sécurité](#5-sécurité)
6. [Points d'attention](#6-points-dattention)
7. [Glossaire](#7-glossaire)

---

## 1. Rôle et objectif

**Community** est une application web Flask simulant un réseau social fictif, conçue pour des ateliers d'animation scientifique sur la **gestion de crise** chez les Petits Débrouillards.

Elle met en scène deux groupes d'acteurs :

| Groupe | Rôle | Interface |
|---|---|---|
| **Cellule de crise** (Mairie) | Diffuse des alertes et communiqués officiels | `/officiel` |
| **Population** (Citoyens) | Réagit, commente, poste des messages libres | `/population` |
| **Animateur** | Orchestre la session depuis le back-office | `/admin` |

L'application tourne sur **Raspberry Pi en réseau local**, sans accès internet. Les tablettes des participants s'y connectent via HTTPS auto-signé.

**Particularité centrale** : toute l'activité se déroule sous une **horloge fictive** — l'heure affichée n'est jamais l'heure système, mais une heure de simulation qui avance en temps réel à partir d'un instant de départ configuré par l'animateur.

---

## 2. Architecture et modules

```
community/
├── run.py                      # Point d'entrée — HTTPS (certs) ou HTTP (Waitress)
├── config.py                   # Config Flask : SECRET_KEY persistante, SGBD, uploads
├── requirements.txt            # 6 dépendances Python
├── app/
│   ├── __init__.py             # Factory create_app() + init extensions + scheduler
│   ├── models.py               # Modèles SQLAlchemy (Session, Message, Comment, Photo, Config)
│   ├── routes/
│   │   ├── auth.py             # Blueprint auth : /login, /logout, /
│   │   ├── admin.py            # Blueprint admin : /admin/* (session, photothèque, codes)
│   │   ├── officiel.py         # Blueprint officiel : /officiel (feed + rédaction)
│   │   ├── population.py       # Blueprint population : /population (feed + rédaction)
│   │   └── htmx.py             # Blueprint htmx : /htmx/* (fragments pour polling)
│   ├── utils/
│   │   ├── helpers.py          # Décorateur require_role()
│   │   └── scheduler.py        # Thread daemon — publication des messages programmés
│   ├── templates/              # Jinja2 : base.html, login, admin/, officiel/, population/, partials/
│   └── static/                 # CSS, htmx.min.js (local), photos/
├── instance/                   # community.db + secret.key (générés à l'exécution)
├── certs/                      # cert.pem + key.pem (TLS auto-signé, non versionné)
└── DOCS/                       # Cahier des charges, specs fonctionnelles/techniques, user-stories
```

### Blueprints Flask

| Blueprint | Préfixe | Responsabilité |
|---|---|---|
| `auth` | `/` | Connexion par code, déconnexion |
| `admin` | `/admin` | Gestion de session (démarrage/arrêt/reset), photothèque, codes d'accès |
| `officiel` | `/officiel` | Feed et rédaction de messages officiels (dont programmés) |
| `population` | `/population` | Feed et rédaction de messages citoyens |
| `htmx` | `/htmx` | Fragments HTML pour polling HTMX (feed, commentaires) |

---

## 3. Modèle de données

```
Session ─────────────────────┐
  id (PK)                     │  1 session active à la fois
  fictive_start_minutes       │  Heure fictive de début (ex. 540 = 09:00)
  real_started_at             │  Datetime réelle de démarrage
  is_active                   │
                              │
                        ┌─────┘
Message ────────────────┤ session_id (FK)
  id (PK)               │
  role                  │  'officiel' | 'population'
  content               │
  photo_filename        │  UUID_nom.ext ou NULL
  real_published_at     │  NULL = non encore publié
  is_scheduled          │
  scheduled_for_minutes │  Heure cible fictive (NULL si immédiat)
  is_published          │
                        │
Comment ────────────────┤ message_id (FK)
  id (PK)               │
  role                  │  'officiel' | 'population'
  content               │
  real_created_at       │

Photo ───────────────────────── (indépendant de la session)
  id (PK)
  scenario_folder              Nom du dossier de scénario
  filename                     UUID_nom.ext
  uploaded_at

Config ──────────────────────── (clé/valeur globale)
  key (PK)                     'code_officiel', 'code_population', 'code_admin', 'scenario_actif'
  value
```

**Calcul de l'heure fictive** : `fictive_minutes = fictive_start_minutes + (now - real_started_at).seconds / 60`  
Le calcul est effectué dynamiquement dans `Session.get_fictive_minutes()` — aucune heure fictive n'est persistée.

---

## 4. Flux principal

### 4.1 Démarrage d'une session

```
Animateur → POST /admin/session/start
  ↳ Désactive toute session en cours
  ↳ Crée Session(fictive_start_minutes, real_started_at=now, is_active=True)
  ↳ Démarre le thread scheduler (daemon, 1 fois au démarrage de l'app)
```

### 4.2 Publication d'un message officiel

```
Cellule de crise → POST /officiel
  ↳ OfficielMessageForm validé (CSRF + WTForms)
  ↳ Vérification photo : existe en base → prévient path traversal
  ↳ Si immédiat  : is_published=True,  real_published_at=now
  ↳ Si programmé : is_published=False, scheduled_for_minutes=cible
      → Le scheduler vérifie toutes les 5s et publie quand fictive_time ≥ cible
```

### 4.3 Mise à jour du feed (polling HTMX)

```
Tablette → GET /htmx/feed  (toutes les 2 secondes, hx-trigger="every 2s")
  ↳ Charge les messages is_published=True de la session active
  ↳ Retourne le fragment partials/feed.html
  ↳ HTMX remplace le conteneur dans la page sans rechargement complet
```

### 4.4 Réponse croisée (commentaires)

```
Participant → POST /htmx/comment/<message_id>
  ↳ require_role('officiel', 'population')
  ↳ Crée Comment(role=session['role'], content, real_created_at=now)
  ↳ Retourne le fragment partials/comments.html mis à jour
```

### 4.5 Réinitialisation de session

```
Animateur → POST /admin/session/reset
  ↳ Supprime tous les Message + Comment (cascade)
  ↳ Conserve intégralement la photothèque (table Photo + fichiers static/photos/)
  ↳ Recrée une session vierge avec la même heure fictive de début
```

---

## 5. Sécurité

| Mesure | Implémentation |
|---|---|
| **CSRF** | Flask-WTF sur tous les formulaires POST |
| **Hachage** | Code admin hashé bcrypt (jamais en clair en base) |
| **Contrôle d'accès** | Décorateur `require_role()` sur toutes les routes protégées |
| **Upload sécurisé** | `secure_filename` + préfixe UUID + vérification magic bytes (JPEG/PNG/WebP) |
| **Path traversal** | Photo validée par lookup en base avant association à un message |
| **SECRET_KEY** | Générée avec `secrets.token_hex(32)`, persistée dans `instance/secret.key` |
| **TLS** | Certificat auto-signé en production (Raspberry Pi LAN) |
| **Taille upload** | Limitée à 2 Mo (`MAX_CONTENT_LENGTH`) |
| **MIME** | Validation déclarative (`ALLOWED_MIME_TYPES`) + vérification magic bytes côté serveur |

---

## 6. Points d'attention

### Concurrence du thread scheduler
Le scheduler tourne dans un **thread daemon Python**. SQLAlchemy crée son propre contexte applicatif dans la boucle via `app.app_context()`. En cas d'exception, le thread ne plante pas (try/except silencieux) mais les erreurs sont donc **silencieuses** — aucun logging n'est implémenté.

### Session Flask unique par rôle
L'application utilise `session['role']` de Flask (cookie signé côté client). Il n'y a **pas de gestion de déconnexion automatique** ni d'expiration de session côté serveur.

### Horloge fictive non persistée
L'heure fictive est recalculée à la volée. Si le serveur redémarre pendant une session active, `real_started_at` est conservé en base et le calcul repart correctement — mais le thread scheduler redémarre avec un délai de 0 s, ce qui est correct.

### Pas de WebSocket
Le temps réel est simulé par **polling HTMX toutes les 2 secondes** sur `/htmx/feed`. Avec ~30 clients simultanés, cela génère environ 15 requêtes/seconde, acceptable pour un Raspberry Pi sur LAN.

### Codes officiel/population en clair
Par choix pédagogique explicite, ces codes sont stockés **en clair** dans la table `Config`. Seul le code admin est hashé.

### Pas de tests d'intégration HTMX
Les tests (`tests/`) couvrent les routes Flask mais pas les interactions HTMX de bout en bout (pas de navigateur headless).

---

## 7. Glossaire

| Terme | Définition |
|---|---|
| **Session** | Durée d'un atelier de simulation. Une seule peut être active à la fois. |
| **Heure fictive** | Heure affichée dans l'interface, déconnectée de l'heure système, qui avance en temps réel à partir d'un instant configuré. |
| **Message officiel** | Publication de la Cellule de crise (Mairie), peut être immédiate ou programmée. |
| **Message programmé** | Message créé à l'avance, publié automatiquement quand l'horloge fictive atteint l'heure cible. |
| **Scheduler** | Thread Python daemon qui vérifie toutes les 5 s si des messages programmés doivent être publiés. |
| **Fragment HTMX** | Portion de HTML retournée par `/htmx/*`, injectée dans la page sans rechargement. |
| **Photothèque** | Bibliothèque d'images persistante, organisée par dossier de scénario, jamais effacée lors d'un reset de session. |
| **Scénario actif** | Dossier de la photothèque sélectionné par l'animateur, dont les photos sont accessibles lors de la session. |
| **Réponse croisée** | Commentaire posté par un groupe sur le message de l'autre groupe. |
| **require_role** | Décorateur Flask (`helpers.py`) qui redirige vers `/login` si le rôle de session ne correspond pas. |
| **magic bytes** | Premiers octets d'un fichier permettant d'identifier son type réel, indépendamment de l'extension déclarée. |
