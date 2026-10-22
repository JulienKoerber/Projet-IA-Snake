import turtle
import time
import random

delay = 0.1

# Scores
score = 0
high_score = 0

# Créer la fenêtre (Fond sombre pour un look plus moderne)
wn = turtle.Screen()
wn.title("Snake Deluxe")
wn.bgcolor("#1e1e2e")
wn.setup(width=600, height=600)
wn.tracer(0)

# Tête du serpent (Forme ronde, couleur vive)
head = turtle.Turtle()
head.speed(0)
head.shape("circle")
head.color("#a6e3a1")
head.penup()
head.goto(0,0)
head.direction = "stop"

# Nourriture (Un cercle rouge vif)
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("#f38ba8")
food.penup()
food.goto(0,100)

segments = []

# Affichage du score (En blanc pour être lisible sur fond sombre)
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("#cdd6f4")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0  High Score: 0", align="center", font=("Courier", 20, "bold"))

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
        head.sety(y + 20)

    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)

    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)

    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)

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

# Boucle principale
while True:
    wn.update()

    # Vérifier si la tête touche un bord
    if head.xcor()>290 or head.xcor()<-290 or head.ycor()>290 or head.ycor()<-290:
        time.sleep(1)
        head.goto(0,0)
        head.direction = "stop"

        for segment in segments:
            segment.goto(1000, 1000)
        
        segments.clear()
        score = 0
        delay = 0.1

        pen.clear()
        pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 20, "bold")) 

    # Vérifier si la tête touche la nourriture
    if head.distance(food) < 20:
        x = random.randint(-280, 280)
        y = random.randint(-280, 280)
        food.goto(x,y)

        # Ajouter un segment (corps d'une nuance légèrement différente)
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("#89b4fa")
        new_segment.penup()
        segments.append(new_segment)

        delay -= 0.001
        score += 10

        if score > high_score:
            high_score = score
        
        pen.clear()
        pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 20, "bold")) 

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
        if segment.distance(head) < 20:
            time.sleep(1)
            head.goto(0,0)
            head.direction = "stop"
        
            for segment in segments:
                segment.goto(1000, 1000)
        
            segments.clear()
            score = 0
            delay = 0.1
        
            pen.clear()
            pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 20, "bold"))

    time.sleep(delay)