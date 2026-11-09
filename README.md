# Projet-IA-Snake

Projet d'implémentation d'une intelligence artificielle dans un moteur de jeu Snake.

Un jeu classique de Snake développé en Python (avec `turtle`) intégrant une Intelligence Artificielle basée sur l'algorithme d'apprentissage par renforcement **Q-Learning**. L'IA apprend à jouer toute seule, en temps réel, et ses performances sont affichées sur un graphique dynamique.

## Fonctionnalités

* **Mode IA / Joueur :** Laissez l'IA s'entraîner ou reprenez le contrôle pour jouer vous-même.

* **Graphique d'apprentissage en direct :** Suivez la progression de l'IA (score par partie et moyenne) grâce à `matplotlib`.

* **Mode Turbo :** Accélérez l'entraînement de l'IA instantanément en appuyant sur `ESPACE`.

* **Sauvegarde automatique :** L'IA sauvegarde son "cerveau" (Q-table) dans un fichier JSON pour ne pas perdre sa progression, ainsi que le meilleur score (High Score).

* **Système de Récompenses optimisé :** L'agent est récompensé s'il se rapproche de la pomme et puni s'il s'en éloigne ou heurte un mur.

* **Profiler mémoire intégré :** Suivi en direct de l'allocation mémoire de l'application via `tracemalloc`.

## Prérequis et Installation

Assurez-vous d'avoir Python installé sur votre machine. Le module `turtle` est inclus par défaut dans Python. Vous aurez seulement besoin d'installer `matplotlib` pour l'affichage du graphique.

1. Clonez ce dépôt ou téléchargez les fichiers.

2. Installez les dépendances nécessaires :

   ```
   pip install matplotlib
   
   ```

## Utilisation

Lancez le jeu avec `python snake-game.py`. Le panneau « Profiler mémoire Snake » affiche en direct la mémoire Python encore occupée, regroupée par fonction, ainsi que le nombre de blocs et le pic mémoire observé. Il s'actualise chaque seconde.

Appuyez sur **P** pour masquer ou réafficher le panneau. Le profiler utilise `tracemalloc` : il mesure les allocations Python toujours vivantes (et non le cumul des allocations déjà libérées).

## Configuration (Paramètres)

En haut du fichier `snake-game.py`, vous pouvez modifier trois paramètres principaux pour changer le comportement du programme :

```
ACTIVER_IA = True  # Mettre sur False pour jouer au clavier
VITESSE_IA = 0.05  # Vitesse d'observation du jeu
RESET_IA = True    # Mettre sur True pour effacer la mémoire au démarrage

```

## Contrôles du Jeu

### Contrôle Général
* **[ P ]** : Masquer ou réafficher le panneau du profiler mémoire.

### Mode IA (`ACTIVER_IA = True`)

* **[ ESPACE ]** : Bascule entre la vitesse d'observation (`VITESSE_IA`) et la vitesse maximale (Turbo) pour accélérer l'entraînement de l'IA.

### Mode Humain (`ACTIVER_IA = False`)

* **[ Z, Q, S, D ]** ou **[ Flèches directionnelles ]** : Déplacer le serpent.

## Comment l'IA apprend-elle ? (Q-Learning)

L'IA analyse son environnement et prend des décisions basées sur un système de récompenses et de punitions (Reward System) défini dans la boucle du jeu :

* **+10** : Le serpent mange la pomme (Objectif principal).

* **+1** : Le serpent effectue un mouvement qui le **rapproche** de la pomme.

* **-2** : Le serpent effectue un mouvement qui l'**éloigne** de la pomme (évite qu'il ne tourne en rond indéfiniment).

* **-10** : Le serpent meurt (Touche un mur ou son propre corps).

À chaque action, l'IA met à jour sa **Q-table** (sauvegardée dans `q_model.json`), ajustant les probabilités de prendre une direction spécifique selon l'état actuel de son environnement (dangers autour, position de la pomme). Plus elle joue de générations, moins elle explore au hasard et plus elle exploite ses connaissances.

## Structure des fichiers

* `snake-game.py` : Script principal gérant le jeu (interface graphique, boucle principale, calcul des récompenses, affichage du profiler).

* `q_learning.py` : (Requis) Contient la classe `QLearningAgent` définissant la logique du cerveau de l'IA.

* `q_model.json` : Fichier généré automatiquement qui stocke la mémoire (Q-table) de l'IA.

* `highscore.txt` : Fichier généré automatiquement pour sauvegarder le record du jeu.