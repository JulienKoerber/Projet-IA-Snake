import os
import json
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(BASE_DIR, "q_model.json")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")


def load_model_data():
    if os.path.exists(MODEL_FILE):
        try:
            with open(MODEL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            app.logger.error(f"Erreur lecture modèle: {e}")
    return {"generations": 0, "q_table": {}}


def save_model_data(data):
    with open(MODEL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def get_current_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            return 0
    return 0


def set_current_highscore(score):
    with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
        f.write(str(score))


@app.route("/")
def index():
    highscore = get_current_highscore()
    model_data = load_model_data()
    generations = model_data.get("generations", 0)
    q_table_size = len(model_data.get("q_table", {}))
    return render_template(
        "index.html",
        highscore=highscore,
        generations=generations,
        q_table_size=q_table_size,
    )


@app.route("/api/model", methods=["GET"])
def get_model():
    data = load_model_data()
    return jsonify(data)


@app.route("/api/model", methods=["POST"])
def save_model():
    data = request.get_json(silent=True)
    if not data or "q_table" not in data:
        return jsonify({"error": "Données invalides"}), 400

    generations = int(data.get("generations", 0))
    q_table = data.get("q_table", {})
    save_model_data({"generations": generations, "q_table": q_table})
    return jsonify({
        "success": True,
        "generations": generations,
        "states_count": len(q_table),
    })


@app.route("/api/model/reset", methods=["POST"])
def reset_model():
    save_model_data({"generations": 0, "q_table": {}})
    return jsonify({"success": True, "generations": 0, "states_count": 0})


@app.route("/api/highscore", methods=["GET"])
def get_highscore():
    return jsonify({"highscore": get_current_highscore()})


@app.route("/api/highscore", methods=["POST"])
def update_highscore():
    data = request.get_json(silent=True)
    if not data or "score" not in data:
        return jsonify({"error": "Score manquant"}), 400

    new_score = int(data.get("score", 0))
    current_high = get_current_highscore()
    updated = False
    if new_score > current_high:
        set_current_highscore(new_score)
        current_high = new_score
        updated = True

    return jsonify({"highscore": current_high, "updated": updated})


if __name__ == "__main__":
    # Écoute en local sur le port 5000 avec rechargement automatique
    app.run(host="0.0.0.0", port=5000, debug=True)
