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

    def get_safe_actions(self, head, segments, direction):
        hx, hy = head.xcor(), head.ycor()
        moves = {
            "up": (hx, hy + 20),
            "down": (hx, hy - 20),
            "left": (hx - 20, hy),
            "right": (hx + 20, hy)
        }
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
        valid_moves = {a: pt for a, pt in moves.items() if direction == "stop" or a != opposites.get(direction)}

        # 1. Vérification des collisions immédiates (murs et corps sans la queue qui avance)
        # Remarque : le dernier segment de queue libère sa case au prochain coup
        tail_pt = (segments[-1].xcor(), segments[-1].ycor()) if segments else None
        body_obstacles = set()
        for idx, seg in enumerate(segments):
            # Le dernier segment avance, sauf s'il n'y a qu'un segment
            if idx < len(segments) - 1:
                body_obstacles.add((seg.xcor(), seg.ycor()))

        def is_collision(pt, include_tail=True):
            x, y = pt
            if x > 280 or x < -280 or y > 280 or y < -280:
                return True
            if include_tail and tail_pt and pt == tail_pt:
                return False  # La queue libère sa case
            return pt in body_obstacles

        non_colliding = {a: pt for a, pt in valid_moves.items() if not is_collision(pt, False)}
        if not non_colliding:
            return list(valid_moves.keys())

        # 2. Test du chemin vers la queue (Tail-Safety)
        # Si le serpent est assez long (> 10 segments), la règle d'or pour dépasser 1000+ points
        # est de s'assurer qu'il existe toujours un chemin libre pour rejoindre sa propre queue.
        def has_path_to_tail(start_pt):
            if not tail_pt:
                return True
            queue = [start_pt]
            visited = {start_pt}
            while queue:
                cx, cy = queue.pop(0)
                if (cx, cy) == tail_pt:
                    return True
                for nx, ny in [(cx + 20, cy), (cx - 20, cy), (cx, cy + 20), (cx, cy - 20)]:
                    npt = (nx, ny)
                    if -280 <= nx <= 280 and -280 <= ny <= 280:
                        if npt not in visited and npt not in body_obstacles:
                            visited.add(npt)
                            queue.append(npt)
            return False

        tail_safe_moves = [a for a, pt in non_colliding.items() if has_path_to_tail(pt)]
        candidate_pool = tail_safe_moves if tail_safe_moves else list(non_colliding.keys())

        # 3. Flood Fill / BFS pour évaluer l'espace disponible
        max_depth = max(len(segments) + 10, 40)
        action_spaces = {}
        for a in candidate_pool:
            start_pt = non_colliding[a]
            visited = {start_pt}
            queue = [start_pt]
            count = 0
            while queue and count < max_depth:
                cx, cy = queue.pop(0)
                count += 1
                for nx, ny in [(cx + 20, cy), (cx - 20, cy), (cx, cy + 20), (cx, cy - 20)]:
                    npt = (nx, ny)
                    if -280 <= nx <= 280 and -280 <= ny <= 280:
                        if npt not in visited and npt not in body_obstacles:
                            visited.add(npt)
                            queue.append(npt)
            action_spaces[a] = count

        # Actions ayant assez d'espace pour le serpent
        safe_actions = [a for a, sp in action_spaces.items() if sp >= len(segments)]
        if safe_actions:
            return safe_actions

        max_sp = max(action_spaces.values())
        return [a for a, sp in action_spaces.items() if sp == max_sp]

    def get_action(self, state, head=None, segments=None, direction=None):
        if head is not None and segments is not None and direction is not None:
            actions = self.get_safe_actions(head, segments, direction)
        else:
            actions = ["up", "down", "left", "right"]

        # Plus elle fait de parties, moins elle joue au hasard (Exploration décroissante)
        current_epsilon = max(0.01, self.epsilon - (self.generations * 0.001))
        
        if random.uniform(0, 1) < current_epsilon:
            return random.choice(actions)
        
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ["up", "down", "left", "right"]}
        
        return max(actions, key=lambda a: self.q_table[state].get(a, 0.0))

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
                    