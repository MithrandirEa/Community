# User Stories — Community

> **Version** : 1.0  
> **Date** : 14 avril 2026  
> **Projet** : Community  
> **Auteur** : Punk-04 (GitHub Copilot)  
> **Statut** : Brouillon

---

## Table des matières

1. [Animateur](#1-animateur)
2. [Cellule de crise](#2-cellule-de-crise)
3. [Population](#3-population)
4. [Transverses](#4-transverses)

---

## Conventions

| Priorité | Signification |
|---|---|
| 🔴 Haute | Fonctionnalité bloquante — indispensable au bon fonctionnement de l'atelier |
| 🟠 Moyenne | Fonctionnalité importante — enrichit l'expérience sans être bloquante |
| 🟡 Basse | Fonctionnalité optionnelle — à implémenter si le temps le permet |

---

## 1. Animateur

### US-ADMIN-01 — Connexion sécurisée au back-office 🔴

> **En tant qu'** animateur,  
> **je veux** accéder à une interface d'administration protégée par un code,  
> **afin de** garder le contrôle exclusif sur la configuration et l'orchestration de la session.

**Critères d'acceptation :**
- [ ] L'accès à `/admin` redirige vers une page de connexion si non authentifié.
- [ ] Un code invalide affiche un message d'erreur sans révéler d'informations sensibles.
- [ ] La session admin expire si l'appareil est inactif plus de 60 minutes.

---

### US-ADMIN-02 — Définir l'heure fictive de simulation 🔴

> **En tant qu'** animateur,  
> **je veux** définir une heure de début fictive avant de lancer la session,  
> **afin de** que tous les horodatages des messages reflètent l'heure de la simulation, et non l'heure réelle.

**Critères d'acceptation :**
- [ ] Un champ de saisie d'heure (format HH:MM) est disponible dans le back-office avant le démarrage.
- [ ] Une fois la session démarrée, l'horloge fictive s'écoule en temps réel à partir de l'heure définie.
- [ ] L'heure fictive actuelle est affichée en permanence dans l'interface admin.
- [ ] Tous les messages publiés (manuels et programmés) sont horodatés selon cette horloge fictive.

---

### US-ADMIN-03 — Démarrer une session 🔴

> **En tant qu'** animateur,  
> **je veux** démarrer la session d'un simple clic,  
> **afin de** synchroniser le début de la simulation et déclencher la publication des messages programmés.

**Critères d'acceptation :**
- [ ] Un bouton « Démarrer la session » est disponible dans le back-office.
- [ ] Au démarrage, l'horloge fictive est activée à partir de l'heure définie.
- [ ] Les messages programmés de la cellule de crise commenceront à être publiés selon leur heure fictive.
- [ ] L'état « session en cours » est visible dans l'interface admin.

---

### US-ADMIN-04 — Gérer la photothèque (dossiers et photos) 🔴

> **En tant qu'** animateur,  
> **je veux** organiser la photothèque en dossiers thématiques par scénario et gérer leur contenu,  
> **afin de** disposer de visuels prêts à l'emploi pour chaque scénario d'animation, de session en session.

**Critères d'acceptation :**
- [ ] Je peux créer un nouveau dossier de scénario (nom libre).
- [ ] Je peux importer une ou plusieurs images dans un dossier (JPG, PNG, WebP, max 2 Mo chacune).
- [ ] Je peux supprimer une image d'un dossier.
- [ ] La photothèque est **persistante** : son contenu est conservé entre toutes les sessions et après réinitialisation.
- [ ] Les images importées sont immédiatement visibles dans la galerie du dossier correspondant.

---

### US-ADMIN-05 — Sélectionner le dossier de scénario actif 🔴

> **En tant qu'** animateur,  
> **je veux** choisir quel dossier de la photothèque est actif avant de démarrer la session,  
> **afin de** ne rendre accessible à la cellule de crise que les photos pertinentes pour le scénario du jour.

**Critères d'acceptation :**
- [ ] Une liste déroulante ou un sélecteur affiche tous les dossiers disponibles.
- [ ] Le dossier sélectionné devient le **dossier actif** de la session.
- [ ] Si aucun dossier n'est sélectionné au moment du démarrage, un avertissement est affiché.
- [ ] Seules les photos du dossier actif sont visibles lorsque la cellule de crise ajoute une photo à un message.

---

### US-ADMIN-06 — Terminer et réinitialiser une session 🔴

> **En tant qu'** animateur,  
> **je veux** terminer la session et effacer toutes les données générées,  
> **afin de** préparer proprement l'atelier suivant sans résidu de la session précédente.

**Critères d'acceptation :**
- [ ] Un bouton « Terminer la session » stoppe la session en cours.
- [ ] Un bouton « Réinitialiser » supprime tous les messages et commentaires de la session.
- [ ] Une confirmation (« Êtes-vous sûr ? ») est demandée avant la réinitialisation.
- [ ] La photothèque (tous les dossiers et photos), les messages programmés de la cellule de crise et le dossier actif sélectionné sont **conservés** après réinitialisation.
- [ ] L'horloge fictive est remise à zéro après réinitialisation.
- [ ] Un message de confirmation est affiché après réinitialisation réussie.

---

### US-ADMIN-07 — Configurer les codes d'accès 🔴

> **En tant qu'** animateur,  
> **je veux** définir les codes d'accès des deux comptes (cellule de crise et population),  
> **afin de** contrôler qui accède à quelle interface lors de l'atelier.

**Critères d'acceptation :**
- [ ] Je peux modifier les codes d'accès depuis l'interface admin.
- [ ] Les codes ne sont pas affichés en clair dans l'interface (masqués par défaut, affichage sur demande).
- [ ] La modification prend effet immédiatement (les sessions ouvertes avec l'ancien code restent valides jusqu'à expiration).

---

## 2. Cellule de crise

### US-CRISE-01 — Accès à l'interface officielle 🔴

> **En tant que** membre de la cellule de crise,  
> **je veux** accéder à l'interface dédiée via un code distribué par l'animateur,  
> **afin de** jouer mon rôle de communicant officiel pendant la simulation.

**Critères d'acceptation :**
- [ ] La page d'accueil propose une saisie de code d'accès.
- [ ] Le bon code redirige vers l'interface cellule de crise.
- [ ] Un code incorrect affiche un message d'erreur clair.

---

### US-CRISE-02 — Publier un message officiel avec texte 🔴

> **En tant que** membre de la cellule de crise,  
> **je veux** publier un message textuel dans le feed officiel,  
> **afin d'** informer la population sur l'évolution de la crise.

**Critères d'acceptation :**
- [ ] Un champ de saisie texte est disponible en haut de l'interface.
- [ ] Le bouton « Publier » envoie le message immédiatement.
- [ ] Le message apparaît en tête du feed avec l'**horodatage fictif** courant.
- [ ] Un message vide ne peut pas être publié (validation côté client et serveur).

---

### US-CRISE-05 — Programmer un message officiel pour publication différée 🔴

> **En tant que** membre de la cellule de crise,  
> **je veux** programmer un message pour qu'il soit publié automatiquement à une heure fictive donnée,  
> **afin de** préparer à l'avance le déroulement de la communication de crise.

**Critères d'acceptation :**
- [ ] Lors de la rédaction, un bouton « Programmer » (distinct de « Publier ») est disponible.
- [ ] Je peux saisir une heure fictive de publication (format HH:MM).
- [ ] Le message s'ajoute à une liste de messages programmés visible sous le formulaire.
- [ ] Le message est automatiquement publié quand l'horloge fictive atteint l'heure définie.
- [ ] Je peux supprimer un message programmé avant sa publication.
- [ ] Un message programmé peut inclure une photo de la photothèque.

---

### US-CRISE-03 — Joindre une photo à un message officiel 🟠

> **En tant que** membre de la cellule de crise,  
> **je veux** illustrer mon message avec une photo issue de la photothèque,  
> **afin de** rendre les alertes plus visuelles et percutantes.

**Critères d'acceptation :**
- [ ] Un bouton « Ajouter une photo » ouvre la galerie du **dossier actif** de la photothèque.
- [ ] Un clic sur une miniature sélectionne la photo.
- [ ] La photo choisie est prévisualisée avant publication.
- [ ] La photo est affichée dans le post publié.

---

### US-CRISE-04 — Répondre aux messages de la population 🟠

> **En tant que** membre de la cellule de crise,  
> **je veux** répondre à un message de la population directement depuis mon interface,  
> **afin de** simuler l'interaction officielle avec les citoyens sur les réseaux sociaux.

**Critères d'acceptation :**
- [ ] Un bouton « Répondre » est disponible sous chaque message de la population.
- [ ] La réponse est affichée indentée sous le message parent avec un badge « Officiel ».
- [ ] La réponse apparaît dans le feed de la population en temps réel.
- [ ] La réponse ne peut pas être modifiée après envoi.

---

## 3. Population

### US-POP-01 — Accès à l'interface population 🔴

> **En tant que** membre du groupe population,  
> **je veux** accéder à l'interface citoyenne via un code distribué par l'animateur,  
> **afin de** participer à la simulation depuis ma tablette.

**Critères d'acceptation :**
- [ ] La page d'accueil propose une saisie de code d'accès.
- [ ] Le bon code redirige vers l'interface population.
- [ ] Un code incorrect affiche un message d'erreur clair.

---

### US-POP-02 — Publier un message dans le feed 🔴

> **En tant que** membre du groupe population,  
> **je veux** publier un message texte libre dans le fil d'actualité,  
> **afin d'** exprimer mes réactions, poser des questions ou partager des informations pendant la crise simulée.

**Critères d'acceptation :**
- [ ] Un champ de saisie et un bouton "Publier" sont accessibles en bas ou en haut de l'écran.
- [ ] Le message apparaît dans le feed commun immédiatement.
- [ ] Un message vide ne peut pas être publié.

---

### US-POP-03 — Répondre à un message (citoyen ou officiel) 🔴

> **En tant que** membre du groupe population,  
> **je veux** répondre à un message existant dans le feed, qu'il soit citoyen ou officiel,  
> **afin de** participer aux échanges et réagir aux alertes.

**Critères d'acceptation :**
- [ ] Chaque message du feed (citoyen ou officiel) affiche un bouton « Répondre ».
- [ ] Un clic révèle un champ de saisie sous le message.
- [ ] La réponse est enregistrée et affichée indentée sous le message parent avec le label « Citoyen ».
- [ ] Le nombre de réponses est affiché sur le bouton (ex. `💬 Répondre (3)`).
- [ ] Une réponse ne peut pas être modifiée après envoi.

---

### US-POP-04 — Voir les alertes officielles dans mon feed 🔴

> **En tant que** membre du groupe population,  
> **je veux** voir les messages officiels de la cellule de crise directement dans mon fil d'actualité,  
> **afin d'** être informé des alertes comme sur un vrai réseau social.

**Critères d'acceptation :**
- [ ] Les messages officiels apparaissent dans le feed population avec un style visuel distinctif.
- [ ] Un badge ou une couleur différente permet de les identifier au premier coup d'œil.
- [ ] Ils s'insèrent dans le feed à leur **heure fictive** de publication (programmée ou immédiate).

---

## 4. Transverses

### US-SYS-01 — Mise à jour du feed en temps réel 🔴

> **En tant qu'** utilisateur (quel que soit mon rôle),  
> **je veux** que le fil d'actualité se mette à jour automatiquement,  
> **afin de** ne pas avoir à recharger manuellement la page pour voir les nouveaux messages.

**Critères d'acceptation :**
- [ ] Les nouveaux messages apparaissent dans un délai < 3 secondes.
- [ ] Aucune action manuelle (F5 ou swipe de rechargement) n'est nécessaire.
- [ ] La mise à jour fonctionne sur réseau local sans connexion internet.

---

### US-SYS-02 — Affichage responsive sur tablette 🔴

> **En tant qu'** utilisateur sur tablette,  
> **je veux** une interface lisible et utilisable sur écran tactile,  
> **afin de** participer confortablement à la simulation.

**Critères d'acceptation :**
- [ ] L'interface s'adapte aux résolutions tablettes courantes (768px–1024px).
- [ ] Les boutons ont une taille suffisante pour être actionnés au doigt (min. 44px).
- [ ] Aucun débordement horizontal du contenu.

---

### US-SYS-03 — Design inspiré des réseaux sociaux 🔴

> **En tant qu'** utilisateur,  
> **je veux** une interface visuellement proche des réseaux sociaux que je connais,  
> **afin de** m'immerger rapidement dans la simulation sans temps d'apprentissage.

**Critères d'acceptation :**
- [ ] Les messages sont présentés sous forme de "cards" avec avatar, texte et horodatage.
- [ ] Le fil est scrollable verticalement, messages récents en haut.
- [ ] Le code visuel (polices, icônes, mise en page) évoque un réseau social populaire.

### US-SYS-04 — Affichage de l'heure fictive courante 🔴

> **En tant qu'** utilisateur (quel que soit mon rôle),  
> **je veux** voir l'heure fictive de la simulation affichée en permanence,  
> **afin de** m'immerger dans le scénario et comprendre la temporalité des événements.

**Critères d'acceptation :**
- [ ] L'heure fictive est affichée en haut de chaque interface (population, cellule de crise, admin).
- [ ] Elle s'écoule en temps réel à partir de l'heure de début fixée par l'animateur.
- [ ] Elle n'affiche jamais l'heure système réelle.
- [ ] Si la session n'est pas démarrée, l'heure affichée est celle configurée (statique).

---

## Points ouverts

> Tous les points ouverts ont été résolus. Aucune question en attente.
