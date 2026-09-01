import os
from flask import Flask, request, jsonify, render_template
from app.agents.sai_agent import SAI
from app.core.database import get_connection, initialize_database

app = Flask(__name__)
sai = SAI()

initialize_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "company": "AI Venture Factory",
        "product": "SAI",
        "status": "ONLINE",
        "ai": "ONLINE"
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    try:
        response = sai.chat(message)

        return jsonify({
            "success": True,
            "response": response
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/api/profile", methods=["POST"])
def create_profile():
    data = request.get_json() or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    goal = str(data.get("goal", "")).strip()
    skills = str(data.get("skills", "")).strip()

    if not name or not email:
        return jsonify({
            "success": False,
            "error": "Name and email are required."
        }), 400

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (name, email, goal, skills)
            VALUES (?, ?, ?, ?)
        """, (name, email, goal, skills))

        connection.commit()
        user_id = cursor.lastrowid
        connection.close()

        return jsonify({
            "success": True,
            "user_id": user_id,
            "message": "Profile created."
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400


@app.route("/api/profile/<int:user_id>")
def get_profile(user_id):
    connection = get_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    if not user:
        return jsonify({
            "success": False,
            "error": "User not found."
        }), 404

    return jsonify({
        "success": True,
        "profile": dict(user)
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )