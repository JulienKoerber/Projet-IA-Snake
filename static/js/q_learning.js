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
     * Choisit une action selon la stratégie epsilon-greedy.
     */
    getAction(stateKey) {
        const curEpsilon = this.getCurrentEpsilon();

        // Exploration aléatoire
        if (Math.random() < curEpsilon) {
            const randIndex = Math.floor(Math.random() * this.actions.length);
            return this.actions[randIndex];
        }

        // Exploitation de la table Q
        if (!this.q_table[stateKey]) {
            this.q_table[stateKey] = { up: 0.0, down: 0.0, left: 0.0, right: 0.0 };
        }

        const actionsObj = this.q_table[stateKey];
        let bestAction = this.actions[0];
        let bestVal = -Infinity;

        // Choix du meilleur Q(s, a)
        for (const act of this.actions) {
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
