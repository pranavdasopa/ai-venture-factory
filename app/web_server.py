import os

from flask import Flask, request, jsonify, render_template

from app.agents.sai_agent import SAI
from app.agents.opportunity_agent import OpportunityAgent
from app.core.database import get_connection, initialize_database


# ==========================================
# APP INITIALIZATION
# ==========================================

app = Flask(__name__)

sai = SAI()
opportunity_agent = OpportunityAgent()

initialize_database()


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# HEALTH
# ==========================================

@app.route("/api/health")
def health():

    return jsonify({
        "company": "AI Venture Factory",
        "product": "SAI",
        "status": "ONLINE",
        "ai": "ONLINE"
    })


# ==========================================
# SAI CHAT
# ==========================================

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}

    message = str(
        data.get("message", "")
    ).strip()

    if not message:

        return jsonify({
            "success": False,
            "error": "Message is required."
        }), 400

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


# ==========================================
# USER PROFILE
# ==========================================

@app.route("/api/profile", methods=["POST"])
def create_profile():

    data = request.get_json() or {}

    name = str(
        data.get("name", "")
    ).strip()

    email = str(
        data.get("email", "")
    ).strip()

    goal = str(
        data.get("goal", "")
    ).strip()

    skills = str(
        data.get("skills", "")
    ).strip()

    if not name:

        return jsonify({
            "success": False,
            "error": "Name is required."
        }), 400

    if not email:

        return jsonify({
            "success": False,
            "error": "Email is required."
        }), 400

    try:

        connection = get_connection()

        cursor = connection.cursor()

        # Check whether this email already exists.
        existing = cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing:

            cursor.execute(
                """
                UPDATE users
                SET name = ?,
                    goal = ?,
                    skills = ?
                WHERE email = ?
                """,
                (
                    name,
                    goal,
                    skills,
                    email
                )
            )

            user_id = existing["id"]

            message = "Profile updated."

        else:

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    goal,
                    skills
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    goal,
                    skills
                )
            )

            user_id = cursor.lastrowid

            message = "Profile created."

        connection.commit()
        connection.close()

        return jsonify({
            "success": True,
            "user_id": user_id,
            "message": message
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
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
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


# ==========================================
# GOALS
# ==========================================

@app.route("/api/goals", methods=["GET"])
def get_goals():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            title,
            description,
            status,
            priority,
            created_at
        FROM tasks
        WHERE owner = 'user'
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    goals = []

    for row in rows:

        goals.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "priority": row["priority"],
            "created_at": row["created_at"]
        })

    return jsonify({
        "success": True,
        "goals": goals
    })


@app.route("/api/goals", methods=["POST"])
def add_goal():

    data = request.get_json() or {}

    goal = str(
        data.get("goal", "")
    ).strip()

    if not goal:

        return jsonify({
            "success": False,
            "error": "Goal is required."
        }), 400

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks
        (
            title,
            description,
            owner,
            status,
            priority
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            goal,
            "SAI user goal",
            "user",
            "todo",
            "high"
        )
    )

    connection.commit()

    goal_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "success": True,
        "goal_id": goal_id,
        "message": "Goal added."
    })


# ==========================================
# OPPORTUNITY ENGINE
# ==========================================

@app.route("/api/opportunities")
def opportunities():

    query = request.args.get(
        "q",
        ""
    ).strip()

    # --------------------------------------
    # If the user searches something,
    # perform normal opportunity search.
    # --------------------------------------

    if query:

        results = opportunity_agent.search(
            query
        )

    # --------------------------------------
    # Otherwise use temporary default
    # personalization.
    #
    # We will replace this with the actual
    # logged-in user's profile next.
    # --------------------------------------

    else:

        results = opportunity_agent.personalized_search(
            skills=[
                "Python",
                "AI"
            ],
            goal="Become an AI engineer"
        )

    return jsonify({
        "success": True,
        "opportunities": results
    })


# ==========================================
# SERVER
# ==========================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    print("=" * 60)
    print("SAI — SAHAYAK AI")
    print("=" * 60)
    print("AI Venture Factory")
    print("AI: ONLINE")
    print(f"PORT: {port}")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )