# Plan de résolution — Usopp 🎯

> Dernière mise à jour : 2026-04-16
> Statut global : 🔵 En cours

---

## Problèmes actifs

### 🔴 Critiques

- [ ] **[#10] FIX : duplication des noms dans un pack**
  - Sévérité : 🔴 Critique (bug fonctionnel — données corrompues silencieusement)
  - Effort : 🟢 Rapide (< 30 min)
  - Fichiers : `app/routes/admin.py` (fonction `namepack_add_entry`)
  - Piste recommandée : vérifier l'unicité `(pack_id, role, label)` avant l'insert avec une requête `NameEntry.query.filter_by(...).first()` — un flash d'erreur si doublon détecté
  - Dépend de : rien
  - Risques : aucun

### 🟠 Importants

- [ ] **[#15] ENHANCE : déplacer le badge + renommer onglet "Noms"**
  - Sévérité : 🟠 Important (UX / lisibilité interface)
  - Effort : 🟢 Rapide (< 30 min)
  - Fichiers : tous les templates qui ont un header (`base.html`, `admin/dashboard.html`, `admin/namepacks.html`, `admin/config.html`, `admin/photos.html`, `officiel/feed.html`, `population/feed.html`)
  - Piste recommandée : déplacer le `<span class="badge ...">` juste après le `<span class="brand">` dans chaque header ; renommer le bouton "Noms" en "Pack de noms" dans `admin/dashboard.html`
  - Dépend de : rien
  - Risques : changement purement HTML/CSS, aucun impact Python

- [ ] **[#11] ENHANCE : détail des packs en modale**
  - Sévérité : 🟠 Important (UX admin : la liste des noms encombre la page)
  - Effort : 🟡 Moyen (1-2h)
  - Fichiers : `app/templates/admin/namepacks.html`
  - Piste recommandée : la liste des noms est actuellement affichée directement dans chaque card. La remplacer par un bouton "Voir le pack" qui ouvre une `<dialog>` HTML5 (native, sans JS externe). La modale affiche les noms groupés par rôle + un bouton "Modifier" par nom (ou édition inline via un input caché). Fermeture par bouton Fermer ou clic en dehors.
  - Dépend de : rien
  - Risques : HTMX non nécessaire si on utilise `<dialog>` + JS vanilla minimal ; pas d'impact backend

- [ ] **[#12] ENHANCE : dimensions max des photos (format 4:3)**
  - Sévérité : 🟠 Important (design du feed)
  - Effort : 🟢 Rapide (< 20 min)
  - Fichiers : `app/static/css/styles.css` (classe `.message-photo`)
  - Piste recommandée : `.message-photo` a déjà `object-fit: cover` mais `max-height: 360px`. Ajouter un `aspect-ratio: 4/3` (ou `3/4` pour les photos verticales) avec un `max-width: 100%` et `width: 100%`. Utiliser `object-fit: cover` pour que l'image remplit le cadre sans distorsion. Optionnellement, ajouter `object-position: center` pour centrer le sujet.
  - Dépend de : rien
  - Risques : aucun — CSS pur, les images existantes s'adaptent

### 🟡 Modérés

- [ ] **[#14] ENHANCE : responsive de l'app**
  - Sévérité : 🟡 Modéré (important pour usage terrain sur Pi LAN)
  - Effort : 🔴 Long (3-5h)
  - Fichiers : `app/static/css/styles.css` (breakpoints `@media`)
  - Piste recommandée : définir deux breakpoints — `@media (max-width: 768px)` pour les espaces officiel/population (tablette), `@media (max-width: 480px)` pour l'espace admin (smartphone). Adapter : header, compose-form, message-card, photo-picker, feed-main, admin-card, session-start-form, namepacks grid.
  - Dépend de : #15 (évite de dupliquer des corrections de layout)
  - Risques : peut casser des elements déjà OK sur desktop — tester sur plusieurs résolutions

- [ ] **[#13] FEAT : avatar pour les noms des pack**
  - Sévérité : 🟡 Modéré (amélioration visuelle, non bloquant)
  - Effort : 🔴 Long (3-5h)
  - Fichiers : `app/models.py` (`NameEntry`), `app/routes/admin.py` (upload avatar), `app/templates/admin/namepacks.html` (formulaire + affichage), `app/templates/partials/message_card.html` (affichage dans le feed)
  - Piste recommandée : ajouter `avatar_filename` (nullable) sur `NameEntry`. Upload via un `FileField` dans la modale d'édition (issue #11 prérequise pour la modale). Validation magic bytes comme pour les photos de la photothèque. Affichage en `<img class="sender-avatar">` dans `message_card.html` si présent.
  - Dépend de : #11 (modale d'édition)
  - Risques : migration BDD (`ALTER TABLE name_entry ADD COLUMN avatar_filename VARCHAR(255)`), gestion des fichiers uploadés (dossier dédié `static/avatars/`)

### 🟢 Mineurs

- [ ] **[#17] CI/CD : GitHub Actions pour les tests**
  - Sévérité : 🟢 Mineur (qualité de code, non bloquant pour la prod)
  - Effort : 🟢 Rapide (< 1h)
  - Fichiers : `.github/workflows/tests.yml` (à créer)
  - Piste recommandée : workflow `on: [push, pull_request]` ciblant `development` et `main`. Job : `python -m pytest tests/ -x -q` sur Python 3.11+ avec installation des dépendances depuis `requirements.txt`.
  - Dépend de : rien
  - Risques : aucun — read-only sur le code

---

## Ordre de résolution recommandé

1. **[#10]** — Quick win critique, bug silencieux à corriger immédiatement
2. **[#15]** — Quick win UX, 30 min, aucune dépendance
3. **[#12]** — Quick win CSS, 20 min, aucune dépendance
4. **[#17]** — Quick win CI/CD, 1h, aucune dépendance
5. **[#11]** — Prérequis de #13, améliore l'ergonomie admin
6. **[#14]** — Responsive, faire après #15 pour éviter les doublons de layout
7. **[#13]** — Feature lourde, nécessite #11

---

## Historique des résolutions

- [x] **[#2] ENHANCE : visibilité des messages programmés** — Résolu le 2026-04-15 — Messages grisés en tête du feed officiel via `pending_messages`. CSS `.message-pending` + `.pending-banner`. PR #6.
- [x] **[#5] ENHANCE : sélecteur heure/minute** — Résolu le 2026-04-15 — `<input type="time">`. PR #7.
- [x] **[#4] FEAT : packs de noms fictifs** — Résolu le 2026-04-15 — Modèles `NamePack`, `NameEntry`, routes CRUD admin, template `/admin/namepacks`. PR #8.
- [x] **[#3] FEAT : sélecteur de personnage** — Résolu le 2026-04-15 — `sender_name` sur `Message`, `<select>` dans les formulaires officiel/population. PR #9.
