import turtle
import time
import random

delay = 0.05

# Scores
score = 0
# Charger le high score depuis un fichier externe s'il existe
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

# Créer la fenêtre
wn = turtle.Screen()
wn.title("Jeu Snake")
wn.bgcolor("#aad751")  # Couleur de fond principale (vert clair)
wn.setup(width=600, height=600)
wn.tracer(0)

# Dessiner le damier (la grille de la map)
grid_pen = turtle.Turtle()
grid_pen.speed(0)
grid_pen.hideturtle()

def draw_grid():
    # Taille de la map : de -300 à 300 (soit 600x600), avec des carreaux de 20x20
    grid_pen.up()
    
    for x in range(-290, 300, 20):
        for y in range(-290, 300, 20):
            grid_pen.goto(x, y)
            grid_pen.down()
            grid_pen.shape("square")
            grid_pen.shapesize(1, 1) # Un carré de 20x20 pixels
            # Alternance basée sur la position pour créer l'effet damier
            if (x // 20 + y // 20) % 2 == 0:
                grid_pen.color("#a2d149") # Vert normal
            else:
                grid_pen.color("#aad751") # Vert clair
            grid_pen.stamp()
            grid_pen.up()

# Dessiner la grille au démarrage
draw_grid()

# Initialisation de la liste des segments avant de créer les segments de base
segments = []

# Tête du serpent (Vert foncé classique)
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("#388a34")
head.penup()
head.goto(0,0)
head.direction = "stop"

for _ in range(2):
    seg = turtle.Turtle()
    seg.speed(0)
    seg.shape("square")
    seg.color("#4caf50")
    seg.penup()
    seg.goto(0, -20 * (len(segments) + 1))  # Alignés en dessous de la tête
    segments.append(seg)

# Nourriture (Une pomme rouge)
food = turtle.Turtle()
food.speed(0)
food.shape("square") # Souvent carré ou rond, carré fait très rétro
food.color("#e74c3c")
food.penup()
food.goto(0,100)

# Affichage du score (En vert très foncé pour contraster avec le fond)
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("#2c5e1a")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 18, "bold"))

# Déplacements
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 10)

    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 10)

    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 10)

    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 10)

# Contrôles du clavier
wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(go_up, "Up")
wn.onkeypress(go_down, "Down")
wn.onkeypress(go_left, "Left")
wn.onkeypress(go_right, "Right")

def reset_game():
    global score, delay
    time.sleep(1)
    head.goto(0,0)
    head.direction = "stop"

    for segment in segments:
        segment.goto(1000, 1000)
    
    segments.clear()
    
    # Recréer les 3 blocs initiaux
    for _ in range(2):
        seg = turtle.Turtle()
        seg.speed(0)
        seg.shape("square")
        seg.color("#4caf50")
        seg.penup()
        seg.goto(0, -20 * (len(segments) + 1))
        segments.append(seg)

    score = 0
    delay = 0.05

    pen.clear()
    pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 18, "bold"))

# Boucle principale
while True:
    wn.update()

    # Vérifier si la tête touche un bord
    if head.xcor()>295 or head.xcor()<-295 or head.ycor()>295 or head.ycor()<-295:
        reset_game()

    # Vérifier si la tête touche la nourriture
    if head.distance(food) < 15:
        x = random.randrange(-280, 281, 10)
        y = random.randrange(-280, 281, 10)
        food.goto(x,y)

        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("#4caf50")
        new_segment.penup()
        segments.append(new_segment)

        delay -= 0.0005
        score += 10

        if score > high_score:
            high_score = score
            # Sauvegarder le nouveau record dans le fichier
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))
        
        pen.clear()
        pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 18, "bold"))

    # Déplacer les segments
    for index in range(len(segments)-1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x, y)

    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x,y)

    move()    

    # Vérifier la collision avec le corps
    for segment in segments:
        if segment.distance(head) < 10:
            reset_game()

    time.sleep(delay)

wn.mainloop()