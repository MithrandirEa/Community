# Plan de résolution — Usopp 🎯

> Dernière mise à jour : 2026-04-16
> Statut global : ✅ Tous résolus

---

## Problèmes actifs

_Aucun problème actif._

---

## Historique des résolutions

- [x] **[#2] ENHANCE : visibilité des messages programmés** — Résolu le 2026-04-15 — Messages grisés en tête du feed officiel via `pending_messages`. CSS `.message-pending` + `.pending-banner`. PR #6.
- [x] **[#5] ENHANCE : sélecteur heure/minute** — Résolu le 2026-04-15 — `<input type="time">`. PR #7.
- [x] **[#4] FEAT : packs de noms fictifs** — Résolu le 2026-04-15 — Modèles `NamePack`, `NameEntry`, routes CRUD admin, template `/admin/namepacks`. PR #8.
- [x] **[#3] FEAT : sélecteur de personnage** — Résolu le 2026-04-15 — `sender_name` sur `Message`, `<select>` dans les formulaires officiel/population. PR #9.
- [x] **[#10] FIX : duplication des noms dans un pack** — Résolu le 2026-04-16 — Vérification unicité `(pack_id, role, label)` dans `namepack_add_entry`. PR #19.
- [x] **[#11] ENHANCE : détail des packs en modale** — Résolu le 2026-04-16 — `<dialog>` HTML5 avec bouton 'Voir le pack', fermeture au clic en dehors. PR #19.
- [x] **[#12] ENHANCE : dimensions max des photos (format 4:3)** — Résolu le 2026-04-16 — `.message-photo` avec `aspect-ratio: 4/3`, `object-fit: cover`, `max-height: 480px`. PR #19.
- [x] **[#13] FEAT : avatar pour les noms des packs** — Résolu le 2026-04-16 — `NameEntry.avatar_filename` + `Message.sender_avatar_filename`, route upload/delete, affichage `message_card.html`. Migration BDD requise. PR #19.
- [x] **[#14] ENHANCE : responsive de l'app** — Résolu le 2026-04-16 — Media queries `@media (max-width: 768px)` (tablette) et `@media (max-width: 480px)` (smartphone). PR #19.
- [x] **[#15] ENHANCE : badge + renommer "Noms"** — Résolu le 2026-04-16 — Badge déplacé après `.brand` dans tous les headers, 'Noms' → 'Pack de noms'. PR #19.
- [x] **[#17] CI/CD : GitHub Actions pour les tests** — Résolu le 2026-04-16 — `.github/workflows/tests.yml` : pytest sur push/PR vers `development` et `main`. PR #19.
