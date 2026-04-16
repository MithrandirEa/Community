# Plan de résolution — Usopp 🎯

> Dernière mise à jour : 2026-04-15
> Statut global : 🔵 En cours

---

## Problèmes actifs

### 🟠 Importants

- [ ] **[#4] FEAT : packs de noms fictifs pour l'admin**
  - Sévérité : 🟠 Important
  - Effort : 🔴 Long (3-6h)
  - Fichiers : `app/models.py`, `app/routes/admin.py`, `app/templates/admin/namepacks.html` (nouveau), `app/templates/admin/dashboard.html`
  - Piste recommandée : voir section détaillée ci-dessous
  - Dépend de : rien
  - Bloque : #3

- [ ] **[#3] FEAT : sélecteur de personnage lors de la rédaction**
  - Sévérité : 🟠 Important
  - Effort : 🟡 Moyen (2-3h)
  - Fichiers : `app/models.py`, `app/routes/officiel.py`, `app/routes/population.py`, `app/templates/officiel/feed.html`, `app/templates/population/feed.html`, `app/templates/partials/message_card.html`
  - Piste recommandée : voir section détaillée ci-dessous
  - Dépend de : #4

### 🟡 Modérés

- [ ] **[#5] ENHANCE : sélecteur heure/minute pour la programmation**
  - Sévérité : 🟡 Modéré
  - Effort : 🟢 Rapide (< 30 min)
  - Fichiers : `app/templates/officiel/feed.html`
  - Piste recommandée : voir section détaillée ci-dessous
  - Dépend de : rien

---

## Ordre de résolution recommandé

1. **[#5]** — Quick win indépendant, améliore l'UX existante sans toucher à la logique
2. **[#4]** — Prérequis de #3, chunk principal (nouveau modèle + admin UI)
3. **[#3]** — Finalisation fonctionnelle, dépend de #4

---

## Détail des pistes par issue

---

### [#5] Sélecteur heure/minute — ENHANCE

**Problème** : Le champ de saisie de l'heure de programmation est un `<input type="text" placeholder="HH:MM">` peu ergonomique.

**Piste recommandée** : ⭐ `<input type="time">`

- **Principe** : Remplacer l'input texte par `<input type="time">` (natif HTML5). Les navigateurs le rendent en sélecteur heure/minute sur mobile et desktop. La valeur soumise est déjà au format `HH:MM`, compatible avec le validateur WTForms `Regexp(r'^\d{2}:\d{2}$')` existant dans `OfficielMessageForm`.
- **Impact** :
  - `app/templates/officiel/feed.html` — 1 ligne à modifier (type + attributs)
  - 0 changement Python
- **Complexité** : 🟢 Faible
- **Risques** : aucun côté backend ; les navigateurs anciens (non ciblés : app sur Pi LAN) retombent sur un input texte classique.

**Changement exact à faire** dans `officiel/feed.html` (ligne ~97) :
```diff
- <input type="text" name="scheduled_time" id="scheduled-time"
-        class="form-input schedule-time-input"
-        placeholder="HH:MM"
-        maxlength="5"
-        value="{{ form.scheduled_time.data or '' }}">
+ <input type="time" name="scheduled_time" id="scheduled-time"
+        class="form-input schedule-time-input"
+        value="{{ form.scheduled_time.data or '' }}">
```

---

### [#4] Packs de noms fictifs — FEAT

**Problème** : Il n'existe aucun moyen pour l'admin de définir des identités fictives pour les participants. Les modèles actuels ne contiennent aucune notion de "personnage" ou de "pack de noms".

**Piste recommandée** : ⭐ Nouveaux modèles `NamePack` + `NameEntry`, liés à `Session`

#### 4.1 — Nouveaux modèles (`app/models.py`)

```python
class NamePack(db.Model):
    """Pack de noms fictifs défini par l'animateur."""
    __tablename__ = 'name_pack'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    entries = db.relationship('NameEntry', backref='pack', lazy='dynamic', cascade='all, delete-orphan')


class NameEntry(db.Model):
    """Entrée d'un pack : nom fictif associé à un rôle."""
    __tablename__ = 'name_entry'

    id = db.Column(db.Integer, primary_key=True)
    pack_id = db.Column(db.Integer, db.ForeignKey('name_pack.id'), nullable=False)
    # 'officiel' | 'population'
    role = db.Column(db.String(20), nullable=False)
    label = db.Column(db.String(100), nullable=False)
```

Et sur `Session`, ajouter une FK optionnelle :
```python
name_pack_id = db.Column(db.Integer, db.ForeignKey('name_pack.id'), nullable=True)
name_pack    = db.relationship('NamePack', foreign_keys=[name_pack_id])
```

#### 4.2 — Nouvelles routes admin (`app/routes/admin.py`)

| Méthode | Route | Action |
|---------|-------|--------|
| GET | `/admin/namepacks` | Liste des packs + formulaire création |
| POST | `/admin/namepacks` | Créer un pack |
| POST | `/admin/namepacks/<id>/delete` | Supprimer un pack |
| POST | `/admin/namepacks/<id>/entries` | Ajouter un nom au pack |
| POST | `/admin/namepacks/<id>/entries/<eid>/delete` | Supprimer un nom |

Modifier `SessionConfigForm` : ajouter un `SelectField` pour choisir le pack actif (facultatif — valeur vide = pas de personnage).

Modifier `session_start()` : sauvegarder `new_session.name_pack_id = form.name_pack_id.data or None`.

#### 4.3 — Template admin

Nouvelle page `app/templates/admin/namepacks.html` :
- Liste des packs existants (accordéon ou tableau)
- Pour chaque pack : liste des noms officiel / population avec boutons suppression
- Formulaire d'ajout de pack (nom du pack)
- Formulaire d'ajout d'entrée (role + label)

Modifier `app/templates/admin/dashboard.html` : ajouter le sélecteur de pack dans le formulaire de démarrage de session.

- **Complexité** : 🔴 Élevée
- **Risques** : migration BDD — `db.create_all()` dans `create_app()` gère la création des nouvelles tables, pas besoin de migration Alembic. Vérifier que `db.create_all()` est bien appelé à l'init.

---

### [#3] Sélecteur de personnage — FEAT

**Problème** : Lors de la rédaction, les participants n'ont pas de moyen de s'identifier sous un nom fictif. Le modèle `Message` ne stocke pas de `sender_name`.

**Piste recommandée** : ⭐ Champ `sender_name` sur `Message` + `SelectField` dans les formulaires

#### 3.1 — Modèle (`app/models.py`)

Ajouter sur `Message` :
```python
# Nom fictif du personnage (depuis le NamePack de la session), None si sans identité
sender_name = db.Column(db.String(100), nullable=True)
```

#### 3.2 — Routes

**`officiel.py`** :
- `OfficielMessageForm` : ajouter `sender_name = SelectField(...)` avec `validators=[Optional()]` et `choices` chargées dynamiquement depuis `NameEntry.query.filter_by(pack_id=..., role='officiel')`
- Le champ n'est affiché que si la session a un pack actif
- La valeur vide ("— aucun nom —") doit être valide
- Enregistrer `msg.sender_name = form.sender_name.data or None`

**`population.py`** : idem avec `role='population'`

#### 3.3 — Templates

**`officiel/feed.html` et `population/feed.html`** :
- Ajouter le `<select>` à gauche de la `<textarea>` (dans `.compose-form`) — cf. maquette dans l'issue #3

**`partials/message_card.html`** :
- Afficher `message.sender_name` si non None (ex: sous le badge de rôle)

- **Complexité** : 🟡 Moyenne
- **Risques** : si la session n'a pas de pack, le formulaire ne doit pas montrer le sélecteur (condition `{% if active_session.name_pack_id %}`). Gérer le cas où l'utilisateur change de pack en cours de session (les anciens messages gardent leur `sender_name` figé — OK).

---

## Historique des résolutions

- [x] **[#2] ENHANCE : visibilité des messages programmés pour la Cellule de crise** — Résolu le 2026-04-15 — Messages `is_scheduled=True, is_published=False` affichés grisés en tête du feed officiel via `pending_messages` dans `htmx.py` et `officiel.py`. CSS `.message-pending` + `.pending-banner`. 95 tests verts.
