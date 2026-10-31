import turtle
import time
import random

# Vitesse initiale (ralentie car on avance de 20px au lieu de 10px maintenant)
delay = 0.1 

# Scores
score = 0
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

# Créer la fenêtre
wn = turtle.Screen()
wn.title("Jeu Snake")
wn.bgcolor("#aad751")
wn.setup(width=600, height=600)
wn.tracer(0)

# Dessiner le damier (la grille de la map)
grid_pen = turtle.Turtle()
grid_pen.speed(0)
grid_pen.hideturtle()

def draw_grid():
    grid_pen.up()
    # On centre parfaitement la grille sur des multiples de 20 (de -280 à 280)
    for x in range(-280, 281, 20):
        for y in range(-280, 281, 20):
            grid_pen.goto(x, y)
            grid_pen.down()
            grid_pen.shape("square")
            grid_pen.shapesize(1, 1) # Un carré de 20x20 pixels
            
            # Alternance basée sur la position pour créer l'effet damier
            if ((x / 20) + (y / 20)) % 2 == 0:
                grid_pen.color("#a2d149") # Vert normal
            else:
                grid_pen.color("#aad751") # Vert clair
            
            grid_pen.stamp()
            grid_pen.up()

# Dessiner la grille au démarrage
draw_grid()

segments = []

# Tête du serpent
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("#388a34")
head.penup()
head.goto(0, 0) # Parfaitement au centre de la grille
head.direction = "stop"

# Création du corps initial
for _ in range(2):
    seg = turtle.Turtle()
    seg.speed(0)
    seg.shape("square")
    seg.color("#4caf50")
    seg.penup()
    seg.goto(0, -20 * (len(segments) + 1))
    segments.append(seg)

# Nourriture (Pomme)
food = turtle.Turtle()
food.speed(0)
food.shape("square")
food.color("#e74c3c")
food.penup()
food.goto(0, 100) # Aligné sur la grille (multiple de 20)

# Affichage du score
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
    # Le serpent avance désormais de 20 pixels pour s'emboîter dans les cases
    if head.direction == "up":
        head.sety(head.ycor() + 20)
    if head.direction == "down":
        head.sety(head.ycor() - 20)
    if head.direction == "left":
        head.setx(head.xcor() - 20)
    if head.direction == "right":
        head.setx(head.xcor() + 20)

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
    delay = 0.1 # On réinitialise à la nouvelle vitesse

    pen.clear()
    pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 18, "bold"))

# Boucle principale
while True:
    wn.update()

    # Les bordures sont maintenant à 280 (la dernière case valide de la grille)
    if head.xcor() > 280 or head.xcor() < -280 or head.ycor() > 280 or head.ycor() < -280:
        reset_game()

    # Si la tête touche la nourriture
    if head.distance(food) < 15:
        # La pomme apparait UNIQUEMENT sur des multiples de 20
        x = random.randrange(-280, 281, 20)
        y = random.randrange(-280, 281, 20)
        food.goto(x, y)

        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("#4caf50")
        new_segment.penup()
        segments.append(new_segment)

        # On accélère le jeu progressivement
        delay -= 0.002
        score += 10

        if score > high_score:
            high_score = score
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))
        
        pen.clear()
        pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 18, "bold"))

    # Déplacer le corps du serpent
    for index in range(len(segments)-1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x, y)

    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x, y)

    move()    

    # Vérifier la collision avec le corps
    for segment in segments:
        if segment.distance(head) < 10:
            reset_game()

    time.sleep(delay)

wn.mainloop()