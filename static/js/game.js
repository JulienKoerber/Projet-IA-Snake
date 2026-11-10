/**
 * Moteur de jeu Snake & Visualiseur d'IA Q-Learning
 * Compatible desktop & mobile, rendu Canvas 600x600, graphiques Chart.js en direct.
 */

// --- CONFIGURATION DE LA GRILLE (Identique à Turtle) ---
const CELL_SIZE = 20;
const GRID_MIN = -280;
const GRID_MAX = 280;
const CANVAS_SIZE = 600;
const MARGIN = 10; // (600 - 580) / 2 = 10px

// Couleurs du thème Snake Google / Turtle
const COLOR_BG_1 = "#aad751";
const COLOR_BG_2 = "#a2d149";
const COLOR_HEAD = "#388a34";
const COLOR_BODY = "#4caf50";
const COLOR_BODY_BORDER = "#388a34";
const COLOR_FOOD = "#e74c3c";
const COLOR_EYES = "#ffffff";
const COLOR_PUPILS = "#1b4d18";

// --- ÉTAT DU JEU ---
let head = { x: 0, y: 0, direction: "stop" };
let segments = [];
let food = { x: 0, y: 100 };
let score = 0;
let highScore = 0;
let isRunning = false;
let gameMode = "ai"; // "ai" ou "human"
let speedMode = "normal"; // "slow", "normal", "turbo"

// Taux de rafraîchissement selon la vitesse (en ms)
const SPEEDS = {
    slow: 70,    // Lente : observation détaillée (14 pas/sec)
    normal: 25,  // Normale : dynamique et réactive (40 pas/sec)
    fast: 8,     // Rapide : très fluide et rapide (120 pas/sec)
    turbo: 0     // Turbo : batching multi-pas (~400 pas/sec, équivalent Turtle delay=0.0)
};

// Agent IA
const agent = new QLearningAgent();

// Variables de progression pour le graphique
let plotScores = [];
let plotMeanScores = [];
let totalScore = 0;
let chartInstance = null;

// Timer de boucle
let gameTimer = null;
let autoSaveInterval = 10; // Sauvegarder sur le serveur toutes les 10 évolutions

// Éléments du DOM
const canvas = document.getElementById("snakeCanvas");
const ctx = canvas.getContext("2d");

const elScore = document.getElementById("valScore");
const elHighScore = document.getElementById("valHighScore");
const elGenerations = document.getElementById("valGenerations");
const elEpsilon = document.getElementById("valEpsilon");
const elStatesCount = document.getElementById("valStatesCount");
const elStatusBadge = document.getElementById("statusBadge");

const btnPlayPause = document.getElementById("btnPlayPause");
const btnReset = document.getElementById("btnReset");
const btnSave = document.getElementById("btnSave");
const btnResetModel = document.getElementById("btnResetModel");

// --- CONVERSIONS DE COORDONNÉES TURTLE <-> CANVAS ---
// Turtle: (0,0) au centre, x [-280..280], y [-280..280]
// Canvas: (0,0) en haut à gauche
function turtleToCanvas(x, y) {
    const cx = (x + 300) - (CELL_SIZE / 2);
    const cy = (300 - y) - (CELL_SIZE / 2);
    return { cx, cy };
}

function randomGridCoord() {
    const steps = (GRID_MAX - GRID_MIN) / CELL_SIZE + 1; // 29 cases
    const randomIndex = Math.floor(Math.random() * steps);
    return GRID_MIN + randomIndex * CELL_SIZE;
}

// --- INITIALISATION DU JEU ---
function initGame() {
    head = { x: 0, y: 0, direction: "stop" };
    segments = [
        { x: 0, y: -20 },
        { x: 0, y: -40 }
    ];
    score = 0;
    updateStatsDisplay();
    draw();
}

function spawnFood() {
    let valid = false;
    let newX = 0;
    let newY = 0;
    while (!valid) {
        newX = randomGridCoord();
        newY = randomGridCoord();
        valid = true;
        if (head.x === newX && head.y === newY) {
            valid = false;
            continue;
        }
        for (let seg of segments) {
            if (seg.x === newX && seg.y === newY) {
                valid = false;
                break;
            }
        }
    }
    food = { x: newX, y: newY };
}

// --- RENDU GRAPHIQUE ---
function drawGrid() {
    for (let x = GRID_MIN; x <= GRID_MAX; x += CELL_SIZE) {
        for (let y = GRID_MIN; y <= GRID_MAX; y += CELL_SIZE) {
            const { cx, cy } = turtleToCanvas(x, y);
            const isAlt = ((x / CELL_SIZE) + (y / CELL_SIZE)) % 2 === 0;
            ctx.fillStyle = isAlt ? COLOR_BG_2 : COLOR_BG_1;
            ctx.fillRect(cx, cy, CELL_SIZE, CELL_SIZE);
        }
    }
}

function drawApple() {
    const { cx, cy } = turtleToCanvas(food.x, food.y);
    const radius = CELL_SIZE / 2 - 2;
    const centerX = cx + CELL_SIZE / 2;
    const centerY = cy + CELL_SIZE / 2;

    // Corps de la pomme
    ctx.beginPath();
    ctx.fillStyle = COLOR_FOOD;
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fill();

    // Tige de la pomme
    ctx.beginPath();
    ctx.strokeStyle = "#795548";
    ctx.lineWidth = 2;
    ctx.moveTo(centerX, centerY - radius + 1);
    ctx.lineTo(centerX + 2, centerY - radius - 3);
    ctx.stroke();

    // Petite feuille verte
    ctx.beginPath();
    ctx.fillStyle = "#27ae60";
    ctx.ellipse(centerX + 4, centerY - radius - 2, 3, 1.5, Math.PI / 4, 0, Math.PI * 2);
    ctx.fill();
}

function drawSnake() {
    // Corps
    segments.forEach((seg, idx) => {
        const { cx, cy } = turtleToCanvas(seg.x, seg.y);
        ctx.fillStyle = COLOR_BODY;
        roundRect(ctx, cx + 1, cy + 1, CELL_SIZE - 2, CELL_SIZE - 2, 4);
        ctx.fill();
    });

    // Tête
    const { cx, cy } = turtleToCanvas(head.x, head.y);
    ctx.fillStyle = COLOR_HEAD;
    roundRect(ctx, cx + 1, cy + 1, CELL_SIZE - 2, CELL_SIZE - 2, 5);
    ctx.fill();

    // Yeux du serpent orientés selon la direction
    drawSnakeEyes(cx, cy, head.direction);
}

function drawSnakeEyes(cx, cy, direction) {
    const eyeRadius = 3;
    const pupilRadius = 1.5;
    let eye1 = { x: cx + 6, y: cy + 6 };
    let eye2 = { x: cx + 14, y: cy + 6 };
    let pupilOffset = { dx: 0, dy: 0 };

    if (direction === "up") {
        eye1 = { x: cx + 5, y: cy + 5 };
        eye2 = { x: cx + 15, y: cy + 5 };
        pupilOffset = { dx: 0, dy: -1 };
    } else if (direction === "down") {
        eye1 = { x: cx + 5, y: cy + 15 };
        eye2 = { x: cx + 15, y: cy + 15 };
        pupilOffset = { dx: 0, dy: 1 };
    } else if (direction === "left") {
        eye1 = { x: cx + 5, y: cy + 5 };
        eye2 = { x: cx + 5, y: cy + 15 };
        pupilOffset = { dx: -1, dy: 0 };
    } else if (direction === "right") {
        eye1 = { x: cx + 15, y: cy + 5 };
        eye2 = { x: cx + 15, y: cy + 15 };
        pupilOffset = { dx: 1, dy: 0 };
    }

    // Dessin yeux
    [eye1, eye2].forEach(pos => {
        ctx.beginPath();
        ctx.fillStyle = COLOR_EYES;
        ctx.arc(pos.x, pos.y, eyeRadius, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.fillStyle = COLOR_PUPILS;
        ctx.arc(pos.x + pupilOffset.dx, pos.y + pupilOffset.dy, pupilRadius, 0, Math.PI * 2);
        ctx.fill();
    });
}

function roundRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
}

function draw() {
    ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    drawGrid();
    drawApple();
    drawSnake();
}

// --- LOGIQUE DU JEU & ÉTAPE RL ---
function simulationStep() {
    let stateKey = null;
    let action = null;

    // 1. Choix de l'action si IA (avec analyse spatiale & Flood Fill)
    if (gameMode === "ai") {
        stateKey = agent.getStateKey(head, food, segments, head.direction);
        action = agent.getAction(stateKey, head, segments, head.direction);

        // Empêcher demi-tour immédiat
        if (action === "up" && head.direction !== "down") head.direction = "up";
        if (action === "down" && head.direction !== "up") head.direction = "down";
        if (action === "left" && head.direction !== "right") head.direction = "left";
        if (action === "right" && head.direction !== "left") head.direction = "right";
    }

    // Déplacement du corps
    for (let i = segments.length - 1; i > 0; i--) {
        segments[i].x = segments[i - 1].x;
        segments[i].y = segments[i - 1].y;
    }
    if (segments.length > 0) {
        segments[0].x = head.x;
        segments[0].y = head.y;
    }

    // Distance avant mouvement
    const oldDistance = Math.hypot(head.x - food.x, head.y - food.y);

    // Déplacement de la tête
    if (head.direction === "up") head.y += CELL_SIZE;
    if (head.direction === "down") head.y -= CELL_SIZE;
    if (head.direction === "left") head.x -= CELL_SIZE;
    if (head.direction === "right") head.x += CELL_SIZE;

    // Distance après mouvement
    const newDistance = Math.hypot(head.x - food.x, head.y - food.y);

    // Récompense équilibrée : +1.5 en rapprochement, -0.5 en éloignement (permet les détours stratégiques)
    let reward = (newDistance < oldDistance) ? 1.5 : -0.5;
    let gameOver = false;

    // Collision murs
    if (head.x > GRID_MAX || head.x < GRID_MIN || head.y > GRID_MAX || head.y < GRID_MIN) {
        gameOver = true;
        reward = -15;
    }

    // Collision corps
    for (let seg of segments) {
        if (Math.hypot(seg.x - head.x, seg.y - head.y) < 10) {
            gameOver = true;
            reward = -15;
            break;
        }
    }

    // Manger la pomme
    if (!gameOver && Math.hypot(head.x - food.x, head.y - food.y) < 15) {
        spawnFood();
        segments.push({ x: head.x, y: head.y });
        score += 10;
        reward = 15;

        if (score > highScore) {
            highScore = score;
            saveHighScoreToServer(highScore);
        }
        updateStatsDisplay();
    }

    // 2. Entraînement de l'IA (mise à jour Q-Table)
    if (gameMode === "ai" && stateKey && action) {
        const nextStateKey = agent.getStateKey(head, food, segments, head.direction);
        agent.train(stateKey, action, reward, nextStateKey, gameOver);
    }

    // 3. Gestion fin de partie
    if (gameOver) {
        if (gameMode === "ai") {
            updatePlot(score, agent.generations);
            // Sauvegarde automatique régulière vers le serveur Flask
            if (agent.generations % autoSaveInterval === 0) {
                saveModelToServer(false);
            }
        }
        initGame();
    }
}

// Boucle principale d'exécution
function step() {
    if (!isRunning) return;

    if (speedMode === "turbo") {
        // En mode Turbo : batching de 5 pas par frame (comme le delay=0.0 de Turtle)
        const batchSize = 5;
        for (let i = 0; i < batchSize; i++) {
            simulationStep();
        }
        draw();
        gameTimer = setTimeout(step, 6);
    } else {
        simulationStep();
        draw();
        const delay = SPEEDS[speedMode] !== undefined ? SPEEDS[speedMode] : 25;
        gameTimer = setTimeout(step, delay);
    }
}

function scheduleNextStep() {
    if (!isRunning) return;
    clearTimeout(gameTimer);
    step();
}

// --- GESTION DU GRAPHIQUE PROGRESSION (CHART.JS) ---
function initChart() {
    const ctxChart = document.getElementById("progressChart").getContext("2d");
    chartInstance = new Chart(ctxChart, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Score de la partie",
                    data: [],
                    borderColor: "#a2d149",
                    backgroundColor: "rgba(162, 209, 73, 0.15)",
                    borderWidth: 1.5,
                    pointRadius: 1,
                    fill: false,
                    tension: 0.1
                },
                {
                    label: "Score moyen",
                    data: [],
                    borderColor: "#2c5e1a",
                    backgroundColor: "rgba(44, 94, 26, 0.2)",
                    borderWidth: 2.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: {
                    title: { display: true, text: "Évolutions (Parties)" },
                    grid: { color: "rgba(0,0,0,0.05)" }
                },
                y: {
                    title: { display: true, text: "Score" },
                    beginAtZero: true,
                    grid: { color: "rgba(0,0,0,0.05)" }
                }
            },
            plugins: {
                legend: { position: "top" }
            }
        }
    });
}

function updatePlot(currentScore, generation) {
    plotScores.push(currentScore);
    totalScore += currentScore;
    const meanScore = generation > 0 ? (totalScore / generation).toFixed(1) : 0;
    plotMeanScores.push(meanScore);

    // Limiter la taille du graphique pour la fluidité (dernières 100 parties)
    const MAX_POINTS = 100;
    let displayLabels = [];
    let displayScores = [];
    let displayMeans = [];

    const startIdx = Math.max(0, plotScores.length - MAX_POINTS);
    for (let i = startIdx; i < plotScores.length; i++) {
        displayLabels.push(i + 1);
        displayScores.push(plotScores[i]);
        displayMeans.push(plotMeanScores[i]);
    }

    if (chartInstance) {
        chartInstance.data.labels = displayLabels;
        chartInstance.data.datasets[0].data = displayScores;
        chartInstance.data.datasets[1].data = displayMeans;
        chartInstance.update();
    }

    updateStatsDisplay();
}

function updateStatsDisplay() {
    elScore.textContent = score;
    elHighScore.textContent = highScore;
    elGenerations.textContent = agent.generations;
    elEpsilon.textContent = (agent.getCurrentEpsilon() * 100).toFixed(1) + "%";
    elStatesCount.textContent = Object.keys(agent.q_table).length;
}

// --- CONTRÔLES ET ÉVÉNEMENTS ---
function togglePlayPause() {
    isRunning = !isRunning;
    if (isRunning) {
        btnPlayPause.innerHTML = `<i class="bi bi-pause-fill"></i> Pause`;
        btnPlayPause.className = "btn btn-warning";
        elStatusBadge.textContent = "En cours";
        elStatusBadge.className = "badge bg-success";
        scheduleNextStep();
    } else {
        clearTimeout(gameTimer);
        btnPlayPause.innerHTML = `<i class="bi bi-play-fill"></i> Reprendre`;
        btnPlayPause.className = "btn btn-success";
        elStatusBadge.textContent = "En pause";
        elStatusBadge.className = "badge bg-secondary";
    }
}

function setSpeed(newSpeed) {
    speedMode = newSpeed;
    document.querySelectorAll(".btn-speed").forEach(b => {
        b.classList.remove("active");
        if (b.dataset.speed === newSpeed) b.classList.add("active");
    });
    if (isRunning) {
        scheduleNextStep();
    }
}

function setMode(newMode) {
    gameMode = newMode;
    document.querySelectorAll(".btn-mode").forEach(b => {
        b.classList.remove("active");
        if (b.dataset.mode === newMode) b.classList.add("active");
    });
    initGame();
}

// Clavier : flèches, ZQSD / WASD, Espace (Turbo), P (Pause)
window.addEventListener("keydown", (e) => {
    const k = e.key.toLowerCase();

    // Turbo toggle avec Espace
    if (e.code === "Space") {
        e.preventDefault();
        setSpeed(speedMode === "turbo" ? "normal" : "turbo");
        return;
    }

    // Pause avec P
    if (k === "p") {
        togglePlayPause();
        return;
    }

    // Direction (manuel ou humain)
    if (gameMode === "human") {
        if ((k === "arrowup" || k === "z" || k === "w") && head.direction !== "down") {
            head.direction = "up";
        } else if ((k === "arrowdown" || k === "s") && head.direction !== "up") {
            head.direction = "down";
        } else if ((k === "arrowleft" || k === "q" || k === "a") && head.direction !== "right") {
            head.direction = "left";
        } else if ((k === "arrowright" || k === "d") && head.direction !== "left") {
            head.direction = "right";
        }
    }
});

// Boutons directionnels à l'écran (mobile / souris)
document.querySelectorAll(".d-pad-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const dir = btn.dataset.dir;
        if (gameMode === "human") {
            if (dir === "up" && head.direction !== "down") head.direction = "up";
            if (dir === "down" && head.direction !== "up") head.direction = "down";
            if (dir === "left" && head.direction !== "right") head.direction = "left";
            if (dir === "right" && head.direction !== "left") head.direction = "right";
        }
    });
});

// Boutons d'action
btnPlayPause.addEventListener("click", togglePlayPause);
btnReset.addEventListener("click", () => {
    initGame();
    if (!isRunning) draw();
});

btnSave.addEventListener("click", () => saveModelToServer(true));
btnResetModel.addEventListener("click", resetModelOnServer);

document.querySelectorAll(".btn-speed").forEach(b => {
    b.addEventListener("click", () => setSpeed(b.dataset.speed));
});

document.querySelectorAll(".btn-mode").forEach(b => {
    b.addEventListener("click", () => setMode(b.dataset.mode));
});

// --- INTERACTIONS AVEC L'API FLASK ---
async function fetchModelFromServer() {
    try {
        const res = await fetch("/api/model");
        if (res.ok) {
            const data = await res.json();
            agent.loadModel(data);
            updateStatsDisplay();
            console.log(`Modèle chargé : ${agent.generations} générations, ${Object.keys(agent.q_table).length} états.`);
        }
    } catch (err) {
        console.warn("Impossible de charger le modèle depuis Flask, utilisation d'un modèle vierge:", err);
    }
}

async function fetchHighScoreFromServer() {
    try {
        const res = await fetch("/api/highscore");
        if (res.ok) {
            const data = await res.json();
            highScore = data.highscore || 0;
            updateStatsDisplay();
        }
    } catch (err) {
        console.warn("Erreur chargement highscore:", err);
    }
}

async function saveModelToServer(showToast = true) {
    try {
        const payload = agent.exportModel();
        const res = await fetch("/api/model", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok && showToast) {
            alert(` Modèle sauvegardé avec succès sur le serveur !\n(${payload.generations} générations, ${Object.keys(payload.q_table).length} états)`);
        }
    } catch (err) {
        console.error("Erreur lors de la sauvegarde du modèle :", err);
    }
}

async function saveHighScoreToServer(scoreVal) {
    try {
        await fetch("/api/highscore", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ score: scoreVal })
        });
    } catch (err) {
        console.warn("Erreur synchronisation highscore :", err);
    }
}

async function resetModelOnServer() {
    if (!confirm("Attention : Voulez-vous vraiment effacer la mémoire de l'IA et remettre les générations à zéro ?")) {
        return;
    }
    try {
        const res = await fetch("/api/model/reset", { method: "POST" });
        if (res.ok) {
            agent.reset();
            plotScores = [];
            plotMeanScores = [];
            totalScore = 0;
            if (chartInstance) {
                chartInstance.data.labels = [];
                chartInstance.data.datasets[0].data = [];
                chartInstance.data.datasets[1].data = [];
                chartInstance.update();
            }
            updateStatsDisplay();
            initGame();
            alert("Mémoire réinitialisée à zéro !");
        }
    } catch (err) {
        console.error("Erreur réinitialisation :", err);
    }
}

// --- DÉMARRAGE DE L'APPLICATION ---
async function startApp() {
    initChart();
    await fetchHighScoreFromServer();
    await fetchModelFromServer();
    initGame();
    // Démarrage automatique
    togglePlayPause();
}

window.addEventListener("DOMContentLoaded", startApp);
