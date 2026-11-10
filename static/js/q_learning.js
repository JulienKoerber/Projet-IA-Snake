/**
 * Agent Q-Learning en JavaScript
 * Implémente exactement les mêmes règles d'états (11 critères), d'actions
 * et d'apprentissage par équation de Bellman que la version Python (q_learning.py).
 */
class QLearningAgent {
    constructor() {
        this.epsilon = 0.1;   // Taux d'exploration initial
        this.alpha = 0.1;     // Taux d'apprentissage
        this.gamma = 0.9;     // Facteur d'actualisation (importance du futur)
        this.q_table = {};
        this.generations = 0;
        this.actions = ["up", "down", "left", "right"];
    }

    /**
     * Charge une table Q et un nombre de générations reçus de l'API Flask.
     */
    loadModel(data) {
        if (!data) return;
        this.generations = data.generations || 0;
        this.q_table = data.q_table || {};
    }

    /**
     * Exporte les données pour envoi au serveur Flask.
     */
    exportModel() {
        return {
            generations: this.generations,
            q_table: this.q_table
        };
    }

    /**
     * Réinitialise le modèle à zéro.
     */
    reset() {
        this.q_table = {};
        this.generations = 0;
    }

    /**
     * Calcule le taux d'exploration dynamique.
     * Diminue au fur et à mesure des générations (parties).
     */
    getCurrentEpsilon() {
        return Math.max(0.01, this.epsilon - (this.generations * 0.001));
    }

    /**
     * Calcule l'état (tuple de 11 booléens) basé sur la tête, la pomme, le corps et la direction.
     * Coordonnées centrées de -280 à 280 avec un pas de 20.
     */
    getStateKey(head, food, segments, direction) {
        const hx = head.x;
        const hy = head.y;

        const point_l = [hx - 20, hy];
        const point_r = [hx + 20, hy];
        const point_u = [hx, hy + 20];
        const point_d = [hx, hy - 20];

        const dir_l = direction === "left";
        const dir_r = direction === "right";
        const dir_u = direction === "up";
        const dir_d = direction === "down";

        const isCollision = (pt) => {
            const [x, y] = pt;
            if (x > 280 || x < -280 || y > 280 || y < -280) {
                return true;
            }
            for (let i = 0; i < segments.length; i++) {
                const seg = segments[i];
                const dx = seg.x - x;
                const dy = seg.y - y;
                if (Math.hypot(dx, dy) < 15) {
                    return true;
                }
            }
            return false;
        };

        const danger_straight = (dir_r && isCollision(point_r)) ||
                                (dir_l && isCollision(point_l)) ||
                                (dir_u && isCollision(point_u)) ||
                                (dir_d && isCollision(point_d));

        const danger_right = (dir_u && isCollision(point_r)) ||
                             (dir_d && isCollision(point_l)) ||
                             (dir_l && isCollision(point_u)) ||
                             (dir_r && isCollision(point_d));

        const danger_left = (dir_u && isCollision(point_l)) ||
                            (dir_d && isCollision(point_r)) ||
                            (dir_r && isCollision(point_u)) ||
                            (dir_l && isCollision(point_d));

        const stateList = [
            danger_straight,
            danger_right,
            danger_left,
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            food.x < hx,
            food.x > hx,
            food.y > hy,
            food.y < hy
        ];

        // Format identique à str(tuple(state)) en Python
        // Ex: "(False, False, False, False, False, True, False, True, False, True, False)"
        return "(" + stateList.map(v => v ? "True" : "False").join(", ") + ")";
    }

    /**
     * Analyse spatiale avancée (Action Masking & Flood Fill) :
     * Empêche les suicides immédiats et évalue la surface libre accessible
     * pour ne pas s'enfermer dans un cul-de-sac plus petit que le corps.
     */
    getSafeActions(head, segments, direction) {
        const hx = head.x;
        const hy = head.y;
        const moves = {
            up: [hx, hy + 20],
            down: [hx, hy - 20],
            left: [hx - 20, hy],
            right: [hx + 20, hy]
        };
        const opposites = { up: "down", down: "up", left: "right", right: "left" };

        const validMoves = {};
        for (const [a, pt] of Object.entries(moves)) {
            if (direction === "stop" || a !== opposites[direction]) {
                validMoves[a] = pt;
            }
        }

        const isCollision = (pt) => {
            const [x, y] = pt;
            if (x > 280 || x < -280 || y > 280 || y < -280) return true;
            for (let i = 0; i < segments.length; i++) {
                const seg = segments[i];
                if (Math.hypot(seg.x - x, seg.y - y) < 15) return true;
            }
            return false;
        };

        const nonColliding = {};
        for (const [a, pt] of Object.entries(validMoves)) {
            if (!isCollision(pt)) {
                nonColliding[a] = pt;
            }
        }

        const nonCollidingActions = Object.keys(nonColliding);
        if (nonCollidingActions.length === 0) {
            return Object.keys(validMoves);
        }

        // BFS / Flood Fill pour calculer l'espace disponible
        const maxDepth = Math.max(segments.length + 5, 30);
        const actionSpaces = {};

        for (const [a, startPt] of Object.entries(nonColliding)) {
            const visited = new Set();
            visited.add(`${startPt[0]},${startPt[1]}`);
            const queue = [startPt];
            let count = 0;

            while (queue.length > 0 && count < maxDepth) {
                const [cx, cy] = queue.shift();
                count++;

                const neighbors = [
                    [cx + 20, cy],
                    [cx - 20, cy],
                    [cx, cy + 20],
                    [cx, cy - 20]
                ];

                for (const [nx, ny] of neighbors) {
                    const key = `${nx},${ny}`;
                    if (!visited.has(key) && !isCollision([nx, ny])) {
                        visited.add(key);
                        queue.push([nx, ny]);
                    }
                }
            }
            actionSpaces[a] = count;
        }

        // Actions avec assez de place pour tout le corps du serpent
        const safeActions = Object.keys(actionSpaces).filter(a => actionSpaces[a] >= segments.length);
        if (safeActions.length > 0) {
            return safeActions;
        }

        // Sinon, action qui offre le plus d'espace de survie
        const maxSp = Math.max(...Object.values(actionSpaces));
        return Object.keys(actionSpaces).filter(a => actionSpaces[a] === maxSp);
    }

    /**
     * Choisit une action selon la stratégie epsilon-greedy combinée
     * avec le filtre des actions spatialement sécurisées.
     */
    getAction(stateKey, head = null, segments = null, direction = null) {
        let actions = this.actions;
        if (head && segments && direction) {
            actions = this.getSafeActions(head, segments, direction);
        }

        const curEpsilon = this.getCurrentEpsilon();

        // Exploration aléatoire restreinte aux actions viables
        if (Math.random() < curEpsilon) {
            const randIndex = Math.floor(Math.random() * actions.length);
            return actions[randIndex];
        }

        // Exploitation de la table Q parmi les actions viables
        if (!this.q_table[stateKey]) {
            this.q_table[stateKey] = { up: 0.0, down: 0.0, left: 0.0, right: 0.0 };
        }

        const actionsObj = this.q_table[stateKey];
        let bestAction = actions[0];
        let bestVal = -Infinity;

        // Choix du meilleur Q(s, a)
        for (const act of actions) {
            const val = actionsObj[act] !== undefined ? actionsObj[act] : 0.0;
            if (val > bestVal) {
                bestVal = val;
                bestAction = act;
            }
        }

        return bestAction;
    }

    /**
     * Met à jour la Q-table via l'équation de Bellman :
     * Q(s, a) = (1 - alpha) * Q(s, a) + alpha * (reward + gamma * max_a' Q(s', a'))
     */
    train(stateKey, action, reward, nextStateKey, gameOver) {
        if (!this.q_table[stateKey]) {
            this.q_table[stateKey] = { up: 0.0, down: 0.0, left: 0.0, right: 0.0 };
        }
        if (!this.q_table[nextStateKey]) {
            this.q_table[nextStateKey] = { up: 0.0, down: 0.0, left: 0.0, right: 0.0 };
        }

        const oldValue = this.q_table[stateKey][action] || 0.0;
        const nextMax = Math.max(...Object.values(this.q_table[nextStateKey]));
        const newValue = (1 - this.alpha) * oldValue + this.alpha * (reward + this.gamma * nextMax);

        this.q_table[stateKey][action] = newValue;

        if (gameOver) {
            this.generations += 1;
        }
    }
}
