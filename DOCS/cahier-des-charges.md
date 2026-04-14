# Cahier des charges — Community

> **Version** : 1.0  
> **Date** : 14 avril 2026  
> **Projet** : Community  
> **Auteur** : Punk-04 (GitHub Copilot)  
> **Statut** : Brouillon

---

## Table des matières

1. [Présentation du projet](#1-présentation-du-projet)
2. [Contexte et problème métier](#2-contexte-et-problème-métier)
3. [Objectifs](#3-objectifs)
4. [Périmètre fonctionnel](#4-périmètre-fonctionnel)
5. [Parties prenantes](#5-parties-prenantes)
6. [Contraintes](#6-contraintes)
7. [Critères de succès](#7-critères-de-succès)

---

## 1. Présentation du projet

**Community** est une application web développée avec le framework Python **Flask**. Elle est conçue pour être utilisée dans le cadre d'ateliers d'animation scientifique sur la **gestion de crise**, destinés principalement à des collégiens et lycéens.

L'application simule un **réseau social fictif** dans lequel deux groupes d'acteurs interagissent comme lors d'une situation de crise réelle :

| Groupe | Rôle dans la simulation |
|---|---|
| **Cellule de crise** | Service communication d'une mairie diffusant alertes et informations officielles |
| **Population** | Citoyens réagissant, s'informant et échangeant des messages |

---

## 2. Contexte et problème métier

### 2.1 Contexte pédagogique

Les Petits Débrouillards conduisent des ateliers de sensibilisation à la gestion de crise à destination du jeune public. Ces ateliers nécessitent un outil de simulation immersif permettant aux participants de vivre la dynamique informationnelle d'une crise (flux d'informations officielles, rumeurs, réactions citoyennes, etc.) dans un cadre contrôlé.

### 2.2 Problème à résoudre

Aujourd'hui, il n'existe pas d'outil dédié et maîtrisé pour simuler cette dynamique de communication de crise. Les animateurs s'appuient sur des supports statiques (diaporamas, jeux de rôle papier) qui ne permettent pas de restituer la temporalité et l'aspect visuel des échanges sur les réseaux sociaux.

### 2.3 Solution proposée

Développement d'une application web autonome, déployable sur réseau local, reproduisant les codes visuels des fils d'actualité (*feeds*) des réseaux sociaux, avec deux interfaces distinctes selon le rôle (officiel / population).

---

## 3. Objectifs

| # | Objectif | Priorité |
|---|---|---|
| O1 | Simuler en temps réel un échange bidirectionnel entre officiels et population | Haute |
| O2 | Permettre à la cellule de crise de programmer ses messages à l'avance pour une heure fictive définie | Haute |
| O3 | Offrir une interface visuellement immersive inspirée des réseaux sociaux | Haute |
| O4 | Fonctionner sans connexion internet sur un réseau local | Haute |
| O5 | Réinitialiser entièrement les données à la fin de chaque session | Haute |
| O6 | Organiser la photothèque en dossiers thématiques par scénario, persistants entre les sessions | Haute |
| O7 | Permettre aux messages de la population de recevoir des commentaires | Moyenne |

---

## 4. Périmètre fonctionnel

### 4.1 Dans le périmètre (IN SCOPE)

- Interface **Cellule de crise** : rédaction, programmation et publication de messages texte et photo
- Interface **Population** : rédaction de messages texte, commentaires sur les messages
- Interface **Animateur** : gestion de la photothèque (dossiers par scénario), sélection du dossier actif pour la session, configuration des codes d'accès, démarrage/arrêt/réinitialisation de session, réglage de l'heure fictive de simulation
- Photothèque **persistante** organisée en dossiers par scénario ; l'animateur sélectionne le dossier actif avant chaque session
- Authentification par **code d'accès** distribué par l'animateur
- Horodatage fictif des messages basé sur une heure de début définie par l'animateur
- Affichage en temps réel sur tablettes
- Réinitialisation manuelle des données déclenchée par l'animateur

### 4.2 Hors périmètre (OUT OF SCOPE)

- Gestion multi-sessions simultanées
- Modération manuelle des messages en cours de session
- Fonctionnalités de "partage" ou "like" natifs
- Comptes utilisateurs individuels pour les membres de la population
- Accès depuis internet (hors LAN)
- Notifications push
- Export des données post-session

---

## 5. Parties prenantes

| Partie prenante | Rôle |
|---|---|
| **Les Petits Débrouillards** | Commanditaire — définit les besoins pédagogiques |
| **Animateur(s)** | Utilisateur principal — configure la session (dossier scénario actif, codes, heure fictive) et orchestre son déroulement |
| **Participants (collégiens/lycéens)** | Utilisateurs finaux — jouent les rôles officiels ou population |
| **Équipe technique** | Développement et maintenance de l'application |

---

## 6. Contraintes

### 6.1 Contraintes techniques

| Contrainte | Détail |
|---|---|
| Framework | Python / Flask |
| Serveur | Raspberry Pi (déploiement code source) |
| Réseau | LAN uniquement, sans accès internet |
| Appareils | Tablettes (navigateur web standard) |
| Participants simultanés | 15 à 30 par session |
| Base de données | Légère, embarquée (SQLite recommandé) |

### 6.2 Contraintes fonctionnelles

- Trois comptes distincts : `animateur` (admin), `cellule-de-crise`, `population`
- L'accès aux comptes participants se fait via un code distribué par l'animateur avant la session
- Les données de session (messages, commentaires) ne sont **pas persistées** entre les sessions
- La réinitialisation des données est déclenchée **manuellement** par l'animateur
- L'horodatage des messages repose sur une **heure fictive** (heure de début configurable, s'écoulant en temps réel)

### 6.3 Contraintes pédagogiques

- L'interface doit être **immédiatement compréhensible** par un jeune public sans formation préalable
- Le design doit reproduire les codes visuels des réseaux sociaux pour favoriser l'immersion

---

## 7. Critères de succès

| Critère | Indicateur de validation |
|---|---|
| Immersion | Les participants s'approprient les rôles dans les 5 premières minutes |
| Fiabilité | Aucun crash lors d'une session de 30 à 60 minutes |
| Facilité d'utilisation | L'animateur peut démarrer une session seul sans documentation complexe |
| Performance réseau | Latence de mise à jour du feed < 3 secondes sur réseau local |
| Réinitialisation | Données effacées proprement en fin de session en un clic |

---

## Points ouverts

| # | Question | Responsable |
|---|---|---|
| 1 | Le type de scénarios de crise est-il figé ou configurable dynamiquement (nom de la ville, événement) ? | Commanditaire |
| 2 | L'animateur peut-il créer et renommer des dossiers de scénario directement depuis l'interface web, ou la gestion des dossiers se fait-elle manuellement sur la Raspberry Pi ? | Commanditaire / Équipe technique |
| 3 | L'animateur doit-il pouvoir définir une durée de session fixe (ex. 45 min) après laquelle la simulation s'arrête automatiquement ? | Commanditaire |
