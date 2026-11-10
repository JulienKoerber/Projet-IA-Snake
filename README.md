# 🐍 Projet IA Snake - Apprentissage par Renforcement (Q-Learning)

Projet d'implémentation et de visualisation d'un agent intelligent autonome jouant au jeu classique **Snake**, basé sur l'algorithme d'apprentissage par renforcement **Q-Learning** (évaluation de Bellman et politique $\varepsilon$-greedy).

Ce projet a été adapté pour fonctionner **aussi bien en local qu'en application web HTTP (Flask)** prête à être déployée sur **PythonAnywhere**.

---

## 📋 Résumé des Travaux Réalisés (Architecture Option B)

Dans la version initiale, le jeu reposait sur les modules de bureau `turtle` (Tkinter) et `matplotlib.pyplot` en mode interactif. Ces modules sont incompatibles avec les serveurs web distants (environnements *headless* sans écran X11).

Pour répondre au besoin d'un déploiement HTTP sur **PythonAnywhere**, l'**Option B** a été implémentée avec succès :

1. **Backend Web Flask (`app.py` & `wsgi.py`) :**
   - Serveur léger en Python fournissant l'interface web et les routes d'API REST.
   - `/api/model` (GET / POST) : Chargement et synchronisation de la table Q (`q_model.json`).
   - `/api/model/reset` (POST) : Remise à zéro de la mémoire de l'IA.
   - `/api/highscore` (GET / POST) : Récupération et mise à jour persistante du meilleur score (`highscore.txt`).
   - Configuration WSGI standard prête pour PythonAnywhere.

2. **Frontend & Inférence Client-Side (`static/` & `templates/`) :**
   - **Moteur de jeu Canvas HTML5 :** Réplique exacte du damier bicolore vert (`#aad751` & `#a2d149`), des dimensions (600x600, pas de 20px) et des animations du Snake d'origine.
   - **Inférence IA en JavaScript (`q_learning.js`) :** L'agent évalue l'état et consulte la Q-table directement dans le navigateur du client.
     - **Avantages majeurs :** 60 FPS garantis, zéro latence réseau pour chaque déplacement, et **aucune consommation excessive du quota CPU journalier** (100s/jour) sur le compte gratuit PythonAnywhere.
   - **Graphique de progression en direct (Chart.js) :** Remplace `matplotlib` et affiche en temps réel l'évolution du score par partie ainsi que la moyenne glissante au fil des générations.
   - **Contrôles complets :** Modes IA ou Humain (clavier ZQSD / Flèches ou pavé tactile), vitesses Lente, Normale et Turbo (<kbd>Espace</kbd>), bouton pause (<kbd>P</kbd>), sauvegarde et réinitialisation.

3. **Entraînement Intensif Headless en Python (`headless_train.py`) :**
   - Script autonome sans interface graphique permettant d'entraîner l'agent à la vitesse maximale du CPU en local pour peupler `q_model.json` avant déploiement.

---

## 🧠 Modélisation de l'IA (Q-Learning)

L'agent apprend par essais-erreurs à maximiser ses récompenses cumulées.

### 1. Espace d'États (11 critères booléens)
L'état $s$ est un tuple de 11 booléens :
* **Dangers immédiats (relatifs à la tête et à sa direction) :**
  1. Danger tout droit (mur ou corps)
  2. Danger à droite
  3. Danger à gauche
* **Direction actuelle du serpent :**
  4. Vers la gauche
  5. Vers la droite
  6. Vers le haut
  7. Vers le bas
* **Position relative de la nourriture (pomme) :**
  8. Nourriture à gauche de la tête
  9. Nourriture à droite de la tête
  10. Nourriture au-dessus de la tête
  11. Nourriture en-dessous de la tête

### 2. Actions
À chaque case, 4 actions discrètes sont possibles :
$$\mathcal{A} = \{\text{"up"}, \text{"down"}, \text{"left"}, \text{"right"}\}$$
*(Les demi-tours immédiats à 180° sont bloqués).*

### 3. Fonction de Récompense
* Se rapproche de la pomme : **+1**
* S'éloigne de la pomme : **-2**
* Mange la pomme : **+10**
* Collision (mort contre mur ou propre corps) : **-10**

### 4. Mise à jour de Bellman
$$Q(s, a) \leftarrow (1 - \alpha) Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') \right]$$
* Taux d'apprentissage ($\alpha$) = `0.1`
* Facteur d'actualisation ($\gamma$) = `0.9`
* Taux d'exploration ($\varepsilon$) : Débute à `0.1` et décroît de `0.001` par génération jusqu'à un minimum de `0.01` ($\varepsilon$-greedy).

---

## 📁 Arborescence du Projet

```text
Projet-IA-Snake/
│
├── app.py                 # Serveur web Flask (API REST & routes)
├── wsgi.py                # Point d'entrée WSGI pour PythonAnywhere
├── requirements.txt       # Dépendances Python (Flask, gunicorn)
│
├── headless_train.py      # Entraîneur CPU ultra-rapide sans interface
├── q_learning.py          # Agent Q-learning d'origine en Python
├── snake-game.py          # Version d'origine de bureau avec Turtle
│
├── q_model.json           # Modèle sauvegardé (générations et Q-table)
├── highscore.txt          # Persistance du meilleur score
│
├── static/
│   ├── css/
│   │   └── style.css      # Feuille de styles personnalisée et responsive
│   └── js/
│       ├── q_learning.js  # Agent Q-learning en JavaScript (même logique)
│       └── game.js        # Moteur de jeu Canvas, Chart.js et contrôles
│
├── templates/
│   └── index.html         # Page web principale (Bootstrap 5, Chart.js)
│
└── README.md              # Documentation du projet
```

---

## 🚀 Utilisation en Local

### 1. Installation des dépendances
Dans un terminal ou invite de commande :
```bash
pip install -r requirements.txt
```

### 2. Lancer l'application Web Flask
```bash
python app.py
```
Ouvre ensuite ton navigateur à l'adresse : **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### 3. Entraîner l'IA rapidement en ligne de commande (optionnel)
Pour ajouter 200 parties d'entraînement en quelques secondes :
```bash
python headless_train.py --episodes 200
```

### 4. Lancer la version classique avec Turtle (version locale historique)
```bash
python snake-game.py
```

---

## 🌐 Déploiement sur PythonAnywhere (Étape par Étape)

Le projet a été spécialement configuré pour être mis en ligne sur **[PythonAnywhere](https://www.pythonanywhere.com/)** en quelques minutes.

### Étape 1 : Créer un compte
1. Inscris-toi gratuitement sur **PythonAnywhere** (choisis le plan gratuit *Beginner*).
2. Ton site aura pour URL : `https://<ton-nom-d-utilisateur>.pythonanywhere.com`.

### Étape 2 : Importer le projet
1. Ouvre l'onglet **Consoles** puis lance une console **Bash**.
2. Clone ton dépôt Git (ou décompresse l'archive du projet) :
   ```bash
   git clone https://github.com/ton-repo/Projet-IA-Snake.git
   cd Projet-IA-Snake
   ```

### Étape 3 : Créer un environnement virtuel
Dans la console Bash PythonAnywhere :
```bash
mkvirtualenv --python=python3.10 snake-env
pip install -r requirements.txt
```

### Étape 4 : Configurer l'application Web
1. Rends-toi dans l'onglet **Web** du tableau de bord PythonAnywhere.
2. Clique sur **"Add a new web app"**.
3. Choisis **"Manual configuration"** puis **Python 3.10**.

### Étape 5 : Configurer le fichier WSGI
1. Toujours dans l'onglet **Web**, clique sur le lien du fichier **"WSGI configuration file"** (ex: `/var/www/<ton-utilisateur>_pythonanywhere_com_wsgi.py`).
2. Supprime tout le contenu généré par défaut et remplace-le par :
   ```python
   import sys
   import os

   # Chemin absolu vers ton projet
   project_home = '/home/<ton-nom-d-utilisateur>/Projet-IA-Snake'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   # Import de l'application Flask
   from app import app as application
   ```
3. Sauvegarde le fichier en haut à droite.

### Étape 6 : Renseigner le Virtualenv et les Fichiers Statiques
1. Dans la section **Virtualenv**, entre le chemin :
   `/home/<ton-nom-d-utilisateur>/.virtualenvs/snake-env`
2. Dans la section **Static files** :
   - **URL** : `/static/`
   - **Directory** : `/home/<ton-nom-d-utilisateur>/Projet-IA-Snake/static`

### Étape 7 : Recharger l'application
Clique sur le gros bouton vert **"Reload <ton-nom-d-utilisateur>.pythonanywhere.com"** !

Ton projet est maintenant accessible en ligne 24h/24 par tout le monde ! 🎉
