import random
import json
import os

class QLearningAgent:
    def __init__(self):
        self.epsilon = 0.1     # Exploration (sera désactivée peu à peu)
        self.alpha = 0.1       # Taux d'apprentissage
        self.gamma = 0.9       # Importance du futur
        self.q_table = {}
        self.generations = 0
        self.load_model()

    def get_state(self, head, food, segments, direction):
        hx, hy = head.xcor(), head.ycor()
        
        # Coordonnées des cases adjacentes
        point_l = (hx - 20, hy)
        point_r = (hx + 20, hy)
        point_u = (hx, hy + 20)
        point_d = (hx, hy - 20)

        dir_l = direction == "left"
        dir_r = direction == "right"
        dir_u = direction == "up"
        dir_d = direction == "down"

        # Fonction pour vérifier si une case spécifique est un mur ou le corps
        def is_collision(pt):
            x, y = pt
            if x > 280 or x < -280 or y > 280 or y < -280:
                return True
            for seg in segments:
                if seg.distance(x, y) < 15:
                    return True
            return False

        # Détection des dangers relative à la direction du serpent
        danger_straight = (dir_r and is_collision(point_r)) or \
                          (dir_l and is_collision(point_l)) or \
                          (dir_u and is_collision(point_u)) or \
                          (dir_d and is_collision(point_d))

        danger_right = (dir_u and is_collision(point_r)) or \
                       (dir_d and is_collision(point_l)) or \
                       (dir_l and is_collision(point_u)) or \
                       (dir_r and is_collision(point_d))

        danger_left = (dir_u and is_collision(point_l)) or \
                      (dir_d and is_collision(point_r)) or \
                      (dir_r and is_collision(point_u)) or \
                      (dir_l and is_collision(point_d))

        # Nouvel état beaucoup plus précis (11 critères au lieu de 9)
        state = (
            danger_straight,
            danger_right,
            danger_left,
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            food.xcor() < hx,  # Nourriture à gauche
            food.xcor() > hx,  # Nourriture à droite
            food.ycor() > hy,  # Nourriture en haut
            food.ycor() < hy   # Nourriture en bas
        )
        return state

    def get_action(self, state):
        actions = ["up", "down", "left", "right"]
        # Plus elle fait de parties, moins elle joue au hasard (Exploration décroissante)
        current_epsilon = max(0.01, self.epsilon - (self.generations * 0.001))
        
        if random.uniform(0, 1) < current_epsilon:
            return random.choice(actions)
        
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in actions}
        
        return max(self.q_table[state], key=self.q_table[state].get)

    def train(self, state, action, reward, next_state, game_over):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ["up", "down", "left", "right"]}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in ["up", "down", "left", "right"]}

        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values())
        
        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
        self.q_table[state][action] = new_value

        if game_over:
            self.generations += 1
            self.save_model()

    def save_model(self):
        string_q_table = {str(k): v for k, v in self.q_table.items()}
        data = {"generations": self.generations, "q_table": string_q_table}
        with open("q_model.json", "w") as f:
            json.dump(data, f)

    def load_model(self):
        if os.path.exists("q_model.json"):
            with open("q_model.json", "r") as f:
                data = json.load(f)
                self.generations = data.get("generations", 0)
                try:
                    self.q_table = {eval(k): v for k, v in data.get("q_table", {}).items()}
                except:
                    self.q_table = {}