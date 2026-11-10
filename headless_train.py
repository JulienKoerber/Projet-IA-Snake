"""
Script d'entraînement intensif sans interface graphique (Headless).
Permet d'entraîner l'agent Q-Learning à la vitesse maximale du CPU
et de mettre à jour le fichier q_model.json sans ouvrir de fenêtre Turtle.
"""

import math
import random
import argparse
from q_learning import QLearningAgent


class HeadlessPoint:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def xcor(self):
        return self.x

    def ycor(self):
        return self.y

    def goto(self, x, y):
        self.x = x
        self.y = y

    def setx(self, x):
        self.x = x

    def sety(self, y):
        self.y = y

    def distance(self, target_or_x, y=None):
        if y is not None:
            tx, ty = target_or_x, y
        else:
            tx, ty = target_or_x.xcor(), target_or_x.ycor()
        return math.hypot(self.x - tx, self.y - ty)


def random_grid_coord():
    return random.randrange(-280, 281, 20)


def run_headless_training(episodes=200):
    agent = QLearningAgent()
    print(f"--- Démarrage de l'entraînement Headless : {episodes} épisodes ---")
    print(f"Générations initiales : {agent.generations}")
    print(f"Taille initiale de la Q-table : {len(agent.q_table)} états")

    best_score = 0
    scores_history = []

    for ep in range(1, episodes + 1):
        head = HeadlessPoint(0, 0)
        direction = "stop"
        segments = [HeadlessPoint(0, -20), HeadlessPoint(0, -40)]
        food = HeadlessPoint(random_grid_coord(), random_grid_coord())

        score = 0
        steps_without_food = 0
        max_steps = 500  # Empêche les boucles infinies potentielles

        while steps_without_food < max_steps:
            steps_without_food += 1

            # 1. État et action
            state = agent.get_state(head, food, segments, direction)
            action = agent.get_action(state)

            if action == "up" and direction != "down":
                direction = "up"
            elif action == "down" and direction != "up":
                direction = "down"
            elif action == "left" and direction != "right":
                direction = "left"
            elif action == "right" and direction != "left":
                direction = "right"

            # Déplacement du corps
            for idx in range(len(segments) - 1, 0, -1):
                segments[idx].goto(segments[idx - 1].xcor(), segments[idx - 1].ycor())
            if len(segments) > 0:
                segments[0].goto(head.xcor(), head.ycor())

            old_dist = head.distance(food)

            # Déplacement tête
            if direction == "up":
                head.sety(head.ycor() + 20)
            elif direction == "down":
                head.sety(head.ycor() - 20)
            elif direction == "left":
                head.setx(head.xcor() - 20)
            elif direction == "right":
                head.setx(head.xcor() + 20)

            new_dist = head.distance(food)
            reward = 1 if new_dist < old_dist else -2
            game_over = False

            # Collision murs
            if (head.xcor() > 280 or head.xcor() < -280 or
                head.ycor() > 280 or head.ycor() < -280):
                game_over = True
                reward = -10

            # Collision corps
            if not game_over:
                for seg in segments:
                    if seg.distance(head) < 10:
                        game_over = True
                        reward = -10
                        break

            # Manger la pomme
            if not game_over and head.distance(food) < 15:
                score += 10
                reward = 10
                steps_without_food = 0
                food.goto(random_grid_coord(), random_grid_coord())
                segments.append(HeadlessPoint(head.xcor(), head.ycor()))

            # Apprentissage
            next_state = agent.get_state(head, food, segments, direction)
            agent.train(state, action, reward, next_state, game_over)

            if game_over:
                break

        scores_history.append(score)
        if score > best_score:
            best_score = score

        if ep % 50 == 0 or ep == episodes:
            avg_last_50 = sum(scores_history[-50:]) / min(len(scores_history), 50)
            print(f"Épisode {ep}/{episodes} | Score: {score} | Max: {best_score} | Moyenne (50): {avg_last_50:.1f} | États: {len(agent.q_table)}")

    agent.save_model()
    print(f"\n--- Entraînement terminé ! ---")
    print(f"Modèle sauvegardé dans 'q_model.json' (Total générations: {agent.generations})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraînement Headless Q-Learning Snake")
    parser.add_argument("--episodes", type=int, default=100, help="Nombre de parties à simuler")
    args = parser.parse_args()
    run_headless_training(args.episodes)
