import os

from flask import Flask, request, jsonify, render_template

from app.agents.sai_agent import SAI
from app.agents.opportunity_agent import OpportunityAgent
from app.core.database import get_connection, initialize_database


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
# PROFILE
# ==========================================

@app.route("/api/profile", methods=["POST"])
def create_profile():

    data = request.get_json() or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    goal = str(data.get("goal", "")).strip()
    skills = str(data.get("skills", "")).strip()

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

    user_id = request.args.get(
        "user_id",
        ""
    ).strip()

    # --------------------------------------
    # Explicit search
    # --------------------------------------

    if query:

        results = opportunity_agent.search(query)

        return jsonify({
            "success": True,
            "personalized": False,
            "opportunities": results
        })

    # --------------------------------------
    # Personalized search
    # --------------------------------------

    if user_id:

        try:

            user_id = int(user_id)

        except ValueError:

            return jsonify({
                "success": False,
                "error": "Invalid user_id."
            }), 400

        connection = get_connection()

        user = connection.execute(
            """
            SELECT
                id,
                name,
                goal,
                skills
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

        skills = user["skills"] or ""
        goal = user["goal"] or ""

        results = opportunity_agent.personalized_search(
            skills=skills,
            goal=goal
        )

        return jsonify({
            "success": True,
            "personalized": True,
            "user_id": user_id,
            "opportunities": results
        })

    # --------------------------------------
    # No user supplied.
    # Return general opportunities.
    # --------------------------------------

    results = opportunity_agent.search()

    return jsonify({
        "success": True,
        "personalized": False,
        "opportunities": results
    })


# ==========================================
# SERVER
# ==========================================

# ==========================================
# APPLICATION TRACKER
# ==========================================

@app.route("/api/applications", methods=["GET"])
def get_applications():

    user_id = request.args.get(
        "user_id",
        ""
    ).strip()

    if not user_id:

        return jsonify({
            "success": False,
            "error": "user_id is required."
        }), 400

    try:
        user_id = int(user_id)
    except ValueError:

        return jsonify({
            "success": False,
            "error": "Invalid user_id."
        }), 400

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM applications
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return jsonify({
        "success": True,
        "applications": [
            dict(row)
            for row in rows
        ]
    })


@app.route("/api/applications", methods=["POST"])
def save_application():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    opportunity_id = str(
        data.get("opportunity_id", "")
    ).strip()

    title = str(
        data.get("title", "")
    ).strip()

    company = str(
        data.get("company", "")
    ).strip()

    url = str(
        data.get("url", "")
    ).strip()

    if not user_id:
        return jsonify({
            "success": False,
            "error": "user_id is required."
        }), 400

    if not opportunity_id:
        return jsonify({
            "success": False,
            "error": "opportunity_id is required."
        }), 400

    if not title:
        return jsonify({
            "success": False,
            "error": "Opportunity title is required."
        }), 400

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid user_id."
        }), 400

    connection = get_connection()

    existing = connection.execute(
        """
        SELECT id
        FROM applications
        WHERE user_id = ?
        AND opportunity_id = ?
        """,
        (
            user_id,
            opportunity_id
        )
    ).fetchone()

    if existing:

        connection.close()

        return jsonify({
            "success": True,
            "message": "Opportunity already saved.",
            "application_id": existing["id"]
        })

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO applications
        (
            user_id,
            opportunity_id,
            title,
            company,
            url
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            opportunity_id,
            title,
            company,
            url
        )
    )

    connection.commit()

    application_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "success": True,
        "message": "Opportunity saved.",
        "application_id": application_id
    })


@app.route(
    "/api/applications/<int:application_id>",
    methods=["PATCH"]
)
def update_application(application_id):

    data = request.get_json() or {}

    status = str(
        data.get("status", "")
    ).strip().lower()

    notes = data.get("notes")

    allowed_statuses = {
        "saved",
        "applied",
        "interview",
        "offer",
        "rejected"
    }

    if status and status not in allowed_statuses:

        return jsonify({
            "success": False,
            "error": (
                "Invalid status. Use: "
                "saved, applied, interview, "
                "offer, rejected."
            )
        }), 400

    connection = get_connection()

    existing = connection.execute(
        """
        SELECT id
        FROM applications
        WHERE id = ?
        """,
        (application_id,)
    ).fetchone()

    if not existing:

        connection.close()

        return jsonify({
            "success": False,
            "error": "Application not found."
        }), 404

    if status and notes is not None:

        connection.execute(
            """
            UPDATE applications
            SET status = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                status,
                str(notes),
                application_id
            )
        )

    elif status:

        connection.execute(
            """
            UPDATE applications
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                status,
                application_id
            )
        )

    elif notes is not None:

        connection.execute(
            """
            UPDATE applications
            SET notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                str(notes),
                application_id
            )
        )

    else:

        connection.close()

        return jsonify({
            "success": False,
            "error": "Nothing to update."
        }), 400

    connection.commit()

    connection.close()

    return jsonify({
        "success": True,
        "message": "Application updated."
    })
if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    print("=" * 60)
    print("SAI — SAHAYAK AI")
    print("AI Venture Factory")
    print("AI: ONLINE")
    print(f"PORT: {port}")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )