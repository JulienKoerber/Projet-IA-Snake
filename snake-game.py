import turtle
import time
import random
import os
import matplotlib.pyplot as plt
from q_learning import QLearningAgent

# --- PARAMÈTRES ---
ACTIVER_IA = True  # Mets sur False pour jouer toi-même au clavier
VITESSE_IA = 0.05  # Vitesse d'observation. Appuie sur ESPACE en jeu pour passer à 0.0 (Vitesse max)
RESET_IA = True    # True = Efface la mémoire et remet les évolutions à 0 au démarrage

delay = VITESSE_IA if ACTIVER_IA else 0.1

# --- REMISE À ZÉRO DE L'IA ---
if RESET_IA and os.path.exists("q_model.json"):
    os.remove("q_model.json")

# --- INITIALISATION MATPLOTLIB ---
plt.ion()  # Active le mode interactif pour le graphique en direct
fig = plt.figure()

plot_scores = []
plot_mean_scores = []
total_score = 0

# --- SCORES ET IA ---
score = 0
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

# Initialisation de l'agent si l'IA est activée
agent = QLearningAgent() if ACTIVER_IA else None

# --- CRÉATION DE LA FENÊTRE TURTLE ---
wn = turtle.Screen()
wn.title("Jeu Snake - IA Q-Learning (Espace = Turbo)")
wn.bgcolor("#aad751")
wn.setup(width=600, height=600)
wn.tracer(0)

# --- DESSIN DU DAMIER ---
grid_pen = turtle.Turtle()
grid_pen.speed(0)
grid_pen.hideturtle()

def draw_grid():
    grid_pen.up()
    # Grille parfaitement centrée sur des multiples de 20 (de -280 à 280)
    for x in range(-280, 281, 20):
        for y in range(-280, 281, 20):
            grid_pen.goto(x, y)
            grid_pen.down()
            grid_pen.shape("square")
            grid_pen.shapesize(1, 1)
            
            if ((x / 20) + (y / 20)) % 2 == 0:
                grid_pen.color("#a2d149")
            else:
                grid_pen.color("#aad751")
            
            grid_pen.stamp()
            grid_pen.up()

draw_grid()

# --- ÉLÉMENTS DU JEU ---
segments = []

# Tête
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("#388a34")
head.penup()
head.goto(0, 0)
head.direction = "stop"

# Corps initial
for _ in range(2):
    seg = turtle.Turtle()
    seg.speed(0)
    seg.shape("square")
    seg.color("#4caf50")
    seg.penup()
    seg.goto(0, -20 * (len(segments) + 1))
    segments.append(seg)

# Nourriture
food = turtle.Turtle()
food.speed(0)
food.shape("square")
food.color("#e74c3c")
food.penup()
food.goto(0, 100)

# Affichage du score sur l'écran de jeu
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("#2c5e1a")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)

def update_score():
    pen.clear()
    texte = f"Score: {score}  High: {high_score}"
    if ACTIVER_IA:
        texte += f"  Évolutions: {agent.generations}"
    pen.write(texte, align="center", font=("Courier", 14, "bold"))

update_score()

# --- FONCTIONS DE DÉPLACEMENT ET CONTRÔLES ---
def go_up():
    if head.direction != "down": head.direction = "up"
def go_down():
    if head.direction != "up": head.direction = "down"
def go_left():
    if head.direction != "right": head.direction = "left"
def go_right():
    if head.direction != "left": head.direction = "right"

def move():
    if head.direction == "up": head.sety(head.ycor() + 20)
    if head.direction == "down": head.sety(head.ycor() - 20)
    if head.direction == "left": head.setx(head.xcor() - 20)
    if head.direction == "right": head.setx(head.xcor() + 20)

# Fonction pour basculer la vitesse avec ESPACE
def toggle_speed():
    global delay
    if not ACTIVER_IA: return # On ne l'active que si l'IA joue
    
    if delay == 0.0:
        delay = VITESSE_IA # Retour à la vitesse d'observation
    else:
        delay = 0.0 # Vitesse Turbo d'entraînement

# --- CONTRÔLES CLAVIER ---
wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(go_up, "Up")
wn.onkeypress(go_down, "Down")
wn.onkeypress(go_left, "Left")
wn.onkeypress(go_right, "Right")
wn.onkeypress(toggle_speed, "space") # La touche Espace est maintenant liée !

# --- FONCTION GRAPHIQUE ---
def update_plot(current_score, generation):
    global total_score
    
    plot_scores.append(current_score)
    total_score += current_score
    if generation > 0:
        mean_score = total_score / generation
    else:
        mean_score = 0
    plot_mean_scores.append(mean_score)
    
    plt.clf()
    plt.title('Progression de l\'IA Q-Learning')
    plt.xlabel('Nombre d\'évolutions (Parties)')
    plt.ylabel('Score')
    
    plt.plot(plot_scores, label='Score de la partie', color='#a2d149')
    plt.plot(plot_mean_scores, label='Score moyen', color='#388a34', linewidth=2)
    
    plt.legend()
    plt.pause(0.001)

# --- RÉINITIALISATION ---
def reset_game():
    global score, delay
    head.goto(0, 0)
    head.direction = "stop"
    
    for segment in segments:
        segment.goto(1000, 1000)
    segments.clear()
    
    for _ in range(2):
        seg = turtle.Turtle()
        seg.speed(0)
        seg.shape("square")
        seg.color("#4caf50")
        seg.penup()
        seg.goto(0, -20 * (len(segments) + 1))
        segments.append(seg)
        
    score = 0
    # Si un humain joue, on remet le delay à 0.1 pour réinitialiser la difficulté
    if not ACTIVER_IA:
        delay = 0.1 
    # (Si l'IA joue, on ne touche pas au 'delay' pour conserver le choix du Turbo ou non)
    
    update_score()

# --- BOUCLE PRINCIPALE ---
while True:
    wn.update()
    
    # 1. État avant le mouvement (Pour l'IA)
    state = None
    if ACTIVER_IA:
        state = agent.get_state(head, food, segments, head.direction)
        action = agent.get_action(state)
        # L'IA donne une action, on empêche le demi-tour immédiat
        if action == "up" and head.direction != "down": head.direction = "up"
        if action == "down" and head.direction != "up": head.direction = "down"
        if action == "left" and head.direction != "right": head.direction = "left"
        if action == "right" and head.direction != "left": head.direction = "right"

    # Déplacer le corps
    for index in range(len(segments)-1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x, y)
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x, y)

    # --- ON MESURE LA DISTANCE AVANT DE BOUGER ---
    old_distance = head.distance(food)

    move()
    
    # --- ON MESURE LA DISTANCE APRES AVOIR BOUGÉ ---
    new_distance = head.distance(food)
    
    # Évaluation pour l'IA
    if new_distance < old_distance:
        reward = 1    # Récompense : On se rapproche de la pomme !
    else:
        reward = -2   # Punition : On s'éloigne ou on tourne en rond !
        
    game_over = False

    # Collision avec les murs
    if head.xcor() > 280 or head.xcor() < -280 or head.ycor() > 280 or head.ycor() < -280:
        game_over = True
        reward = -10  # Grosse punition pour la mort

    # Collision avec le corps
    for segment in segments:
        if segment.distance(head) < 10:
            game_over = True
            reward = -10  # Grosse punition pour la mort

    # Manger la pomme
    if head.distance(food) < 15:
        # Apparition de la pomme sur un multiple de 20
        x = random.randrange(-280, 281, 20)
        y = random.randrange(-280, 281, 20)
        food.goto(x, y)
        
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("#4caf50")
        new_segment.penup()
        segments.append(new_segment)
        
        score += 10
        reward = 10  # Grosse récompense pour avoir mangé
        if score > high_score:
            high_score = score
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))
        update_score()

    # 2. Entraînement de l'IA (mise à jour de la Q-table)
    if ACTIVER_IA:
        next_state = agent.get_state(head, food, segments, head.direction)
        agent.train(state, action, reward, next_state, game_over)

    # Gestion de la fin de partie
    if game_over:
        if ACTIVER_IA:
            update_plot(score, agent.generations)
        else:
            time.sleep(1) # Pause si le joueur humain meurt
        reset_game()

    # Pause pour régler la vitesse visuelle (IA ou Humain)
    if delay > 0:
        time.sleep(delay)

wn.mainloop()