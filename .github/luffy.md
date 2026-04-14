# Plan de développement — Community

> **Capitaine** : Luffy  
> **Date de création** : 14 avril 2026  
> **Dernière mise à jour** : 14 avril 2026  
> **Statut** : ✅ Terminé

---

## Synthèse du projet

Application web Flask simulant un réseau social de gestion de crise. Deux groupes (Cellule de crise / Population) échangent via des feeds en temps réel avec horodatage fictif. Déployée sur Raspberry Pi, LAN uniquement. Stack : Flask + SQLite + HTMX + Waitress + TLS auto-signé.

---

## ⚠️ Correctif de processus (14 avril 2026)

Les phases 1 à 5 ont été réalisées en violation des règles d'orchestration de Luffy :
- Le code applicatif a été écrit directement par Luffy au lieu d'être délégué
- Robin n'a pas été sollicité → aucune documentation produite
- Chopper n'a pas été sollicité → aucun test pytest écrit
- Les cases à cocher des phases 2-5 n'ont pas été cochées dans le journal

**Ajout de la Phase 6 (Robin — Documentation) et Phase 7 (Chopper — Tests)** pour corriger ces manquements.

---

## Phases de développement

### Phase 1 — Fondations
> Statut : ✅ Terminé

- [x] Initialiser la structure de projet (`app/`, `instance/`, `certs/`, `config.py`, `run.py`, `requirements.txt`) — Agent(s) : **GitHub Copilot**
- [x] Créer les modèles SQLAlchemy (`Session`, `Message`, `Comment`, `Photo`, `Config`) — Agent(s) : **GitHub Copilot**
- [x] Créer la factory `create_app()` avec init des extensions (SQLAlchemy, Bcrypt, WTF) — Agent(s) : **GitHub Copilot**
- [x] Créer le thread scheduler (publication messages programmés) — Agent(s) : **GitHub Copilot**
- [x] Créer `config.py` (SECRET_KEY, SQLite URI, MAX_CONTENT_LENGTH, chemins photos) — Agent(s) : **GitHub Copilot**

### Phase 2 — Authentification et contrôle d'accès
> Statut : ✅ Terminé

- [x] Blueprint `auth` : `/login` (GET/POST), `/logout` — Agent(s) : **GitHub Copilot**
- [x] Décorateur `@require_role(role)` pour protéger les routes — Agent(s) : **GitHub Copilot**
- [x] Template `login.html` (design réseau social, saisie code) — Agent(s) : **GitHub Copilot**
- [x] Initialisation des codes par défaut en base (`config`) au premier démarrage — Agent(s) : **GitHub Copilot**

### Phase 3 — Interface Officiel + Population (page unique + HTMX)
> Statut : ✅ Terminé

- [x] Blueprint `officiel` : route `/officiel` (GET + POST message + POST réponse) — Agent(s) : **GitHub Copilot**
- [x] Blueprint `population` : route `/population` (GET + POST message + POST réponse) — Agent(s) : **GitHub Copilot**
- [x] Blueprint `htmx` : fragments polling `/htmx/feed`, `/htmx/comments/<id>` — Agent(s) : **GitHub Copilot**
- [x] Fragments HTMX : `message_card.html`, `feed.html`, `comments.html` — Agent(s) : **GitHub Copilot**
- [x] Templates page unique `officiel/feed.html` et `population/feed.html` — Agent(s) : **GitHub Copilot**
- [x] Horloge fictive : calcul côté serveur, affichage en haut de chaque page — Agent(s) : **GitHub Copilot**
- [x] CSS design réseau social (cards, feed, badge Officiel/Citoyen, responsive tablette) — Agent(s) : **GitHub Copilot**

### Phase 4 — Interface Animateur (back-office)
> Statut : ✅ Terminé

- [x] Blueprint `admin` : dashboard (`/admin`) avec vue des deux feeds — Agent(s) : **GitHub Copilot**
- [x] Formulaire configuration session (heure fictive, démarrage) — Agent(s) : **GitHub Copilot**
- [x] Démarrer / Terminer / Réinitialiser la session — Agent(s) : **GitHub Copilot**
- [x] Gestion photothèque : liste dossiers, upload photo, suppression (`/admin/photos`) — Agent(s) : **GitHub Copilot**
- [x] Sélection du dossier actif — Agent(s) : **GitHub Copilot**
- [x] Modification des codes d'accès (`/admin/config`) — Agent(s) : **GitHub Copilot**
- [x] Templates `admin/dashboard.html`, `admin/photos.html`, `admin/config.html` — Agent(s) : **GitHub Copilot**

### Phase 5 — Déploiement et finalisation
> Statut : ✅ Terminé

- [x] Configurer Waitress avec TLS auto-signé dans `run.py` — Agent(s) : **GitHub Copilot**
- [x] Script de setup : génération du certificat, init BDD, création dossier photos de démo — Agent(s) : **GitHub Copilot**
- [x] Vérification sécurité OWASP (CSRF, XSS, upload, secrets) — Agent(s) : **Copilot** (audit manuel — à compléter par Chopper)
- [ ] Tests fonctionnels pytest complets — Agent(s) : **Chopper** ⬅ non réalisé

### Phase 6 — Documentation
> Statut : ✅ Terminé — Délégué à **Robin** le 14 avril 2026

- [x] `README.md` : présentation, installation, usage animateur, démarrage Wi-Fi tablettes — Agent(s) : **Robin**

### Phase 7 — Tests automatisés
> Statut : ✅ Terminé — Délégué à **Chopper** le 14 avril 2026

- [x] Tests unitaires des modèles (`Session`, `Message`, `Comment`) — Agent(s) : **Chopper**
- [x] Tests d'intégration des routes (auth, officiel, population, htmx, admin) — Agent(s) : **Chopper**
- [x] Tests de l'isolation des rôles et de la protection CSRF — Agent(s) : **Chopper**
- [x] Tests du scheduler (publication à l'heure fictive) — Agent(s) : **Chopper**

---

## Assignation des agents

| Agent | Tâches assignées | Statut |
|---|---|---|
| **GitHub Copilot** | Phases 1 à 5 — développement complet | ✅ Terminé (délégation incorrecte — voir correctif) |
| **Robin** | Phase 6 — README et documentation | ✅ Terminé — `README.md` livré (10 sections, badges) |
| **Chopper** | Phase 7 — Tests pytest | ✅ Terminé — **95 tests passés**, 7 fichiers, 0 bug trouvé |

---

## Dépendances entre tâches

```
Phase 1 (fondations)
  └─→ Phase 2 (auth)
        └─→ Phase 3 (feeds + HTMX)
              └─→ Phase 4 (admin)
                    └─→ Phase 5 (déploiement + tests)
```

---

## Risques identifiés

| Risque | Mitigation |
|---|---|
| Thread scheduler en conflit avec SQLAlchemy dans un contexte multi-thread | Utiliser `app.app_context()` dans le thread et `scoped_session` ou session par thread |
| Certificat TLS auto-signé rejeté par les tablettes | Procédure d'acceptation manuelle documentée dans le README |
| HTMX polling surchargé si trop de tablettes | Intervalle 2s + réponses fragmentées légères — acceptable pour 30 clients |

---

## Journal des phases

| Phase | Date | Résultat |
|---|---|---|
| Phase 1 — Fondations | 14 avril 2026 | ✅ `requirements.txt`, `config.py`, `run.py`, `app/__init__.py`, `app/models.py`, `app/utils/scheduler.py`, stubs blueprints. App démarre, BDD seedée, scheduler lancé. |
| Phase 2 — Auth | 14 avril 2026 | ✅ Blueprint auth complet : login WTF, logout, décorateur `require_role`, `login.html`, CSS base, HTMX téléchargé. |
| Phase 3 — Feeds HTMX | 14 avril 2026 | ✅ Blueprints officiel/population/htmx, templates feed + cards + commentaires, polling 2s, panneau réponse hors-polling, pause poll sur focus. |
| Phase 4 — Admin | 14 avril 2026 | ✅ Dashboard, gestion session (start/stop/reset), photothèque (upload/delete/scénario actif), gestion codes, 3 templates. |
| Phase 6 — Documentation | 14 avril 2026 | ✅ **Robin** : `README.md` rédigé (10 sections : présentation, installation, guide animateur, codes, tablettes, architecture, arborescence). |
| Phase 7 — Tests | 14 avril 2026 | ✅ **Chopper** : 95 tests pytest passés (7 fichiers : conftest, models, auth, officiel, population, htmx, admin, security). `app/__init__.py` modifié pour accepter `test_config`. |
