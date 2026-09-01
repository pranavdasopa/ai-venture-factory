import os
import sqlite3

from flask import Flask, request, jsonify, render_template

from app.agents.sai_agent import SAI
from app.agents.opportunity_agent import OpportunityAgent
from app.core.database import get_connection, initialize_database


# ==========================================
# APP
# ==========================================

app = Flask(__name__)

sai = SAI()
opportunity_agent = OpportunityAgent()


# ==========================================
# DATABASE
# ==========================================

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
# CHAT
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


    connection = get_connection()

    connection.row_factory = sqlite3.Row


    try:

        existing = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()


        if existing:

            user_id = existing["id"]

            connection.execute(
                """
                UPDATE users
                SET
                    name = ?,
                    goal = ?,
                    skills = ?
                WHERE id = ?
                """,
                (
                    name,
                    goal,
                    skills,
                    user_id
                )
            )

            connection.commit()

            return jsonify({
                "success": True,
                "user_id": user_id,
                "message": "Profile updated."
            })


        cursor = connection.execute(
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

        connection.commit()

        user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "user_id": user_id,
            "message": "Profile created."
        })


    finally:

        connection.close()


# ==========================================
# GET PROFILE
# ==========================================

@app.route("/api/profile/<int:user_id>")
def get_profile(user_id):

    connection = get_connection()

    connection.row_factory = sqlite3.Row


    try:

        user = connection.execute(
            """
            SELECT
                id,
                name,
                email,
                goal,
                skills,
                created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()


        if not user:

            return jsonify({
                "success": False,
                "error": "User not found."
            }), 404


        return jsonify({
            "success": True,
            "profile": dict(user)
        })


    finally:

        connection.close()


# ==========================================
# GOALS
# ==========================================

@app.route("/api/goals", methods=["GET"])
def get_goals():

    connection = get_connection()

    connection.row_factory = sqlite3.Row


    try:

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
            ORDER BY id DESC
            """
        ).fetchall()


        goals = [
            dict(row)
            for row in rows
        ]


        return jsonify({
            "success": True,
            "goals": goals
        })


    finally:

        connection.close()


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


    try:

        cursor = connection.execute(
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
                "",
                "USER",
                "todo",
                "high"
            )
        )


        connection.commit()

        goal_id = cursor.lastrowid


        return jsonify({
            "success": True,
            "goal_id": goal_id,
            "message": "Goal added."
        })


    finally:

        connection.close()


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

        results = opportunity_agent.search(
            query
        )


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

        connection.row_factory = sqlite3.Row


        try:

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


        finally:

            connection.close()


        if not user:

            return jsonify({
                "success": False,
                "error": "User not found."
            }), 404


        skills_text = (
            user["skills"] or ""
        )

        goal = (
            user["goal"] or ""
        )


        # Convert comma-separated skills
        # into a real Python list.

        skills = [
            skill.strip()
            for skill in skills_text.split(",")
            if skill.strip()
        ]


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
    # General opportunities
    # --------------------------------------

    results = opportunity_agent.search()


    return jsonify({
        "success": True,
        "personalized": False,
        "opportunities": results
    })


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

    connection.row_factory = sqlite3.Row


    try:

        rows = connection.execute(
            """
            SELECT
                id,
                user_id,
                opportunity_id,
                title,
                company,
                url,
                status,
                created_at
            FROM applications
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        ).fetchall()


        applications = [
            dict(row)
            for row in rows
        ]


        return jsonify({
            "success": True,
            "applications": applications
        })


    finally:

        connection.close()


# ==========================================
# SAVE APPLICATION
# ==========================================

@app.route("/api/applications", methods=["POST"])
def save_application():

    data = request.get_json() or {}


    try:

        user_id = int(
            data.get("user_id")
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "success": False,
            "error": "Valid user_id is required."
        }), 400


    opportunity_id = str(
        data.get(
            "opportunity_id",
            ""
        )
    ).strip()


    title = str(
        data.get(
            "title",
            ""
        )
    ).strip()


    company = str(
        data.get(
            "company",
            ""
        )
    ).strip()


    url = str(
        data.get(
            "url",
            ""
        )
    ).strip()


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


    connection = get_connection()

    connection.row_factory = sqlite3.Row


    try:

        user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()


        if not user:

            return jsonify({
                "success": False,
                "error": "User not found."
            }), 404


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

            return jsonify({
                "success": True,
                "application_id": existing["id"],
                "message": "Opportunity already saved."
            })


        cursor = connection.execute(
            """
            INSERT INTO applications
            (
                user_id,
                opportunity_id,
                title,
                company,
                url,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                opportunity_id,
                title,
                company,
                url,
                "saved"
            )
        )


        connection.commit()


        return jsonify({
            "success": True,
            "application_id": cursor.lastrowid,
            "message": "Opportunity saved."
        })


    finally:

        connection.close()


# ==========================================
# UPDATE APPLICATION STATUS
# ==========================================

@app.route(
    "/api/applications/<int:application_id>",
    methods=["PATCH"]
)
def update_application(
    application_id
):

    data = request.get_json() or {}


    status = str(
        data.get(
            "status",
            ""
        )
    ).strip().lower()


    allowed_statuses = {
        "saved",
        "applied",
        "interview",
        "offer",
        "rejected"
    }


    if status not in allowed_statuses:

        return jsonify({
            "success": False,
            "error": (
                "Invalid status. "
                "Use: saved, applied, "
                "interview, offer, rejected."
            )
        }), 400


    connection = get_connection()


    try:

        cursor = connection.execute(
            """
            UPDATE applications
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                application_id
            )
        )


        connection.commit()


        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "error": "Application not found."
            }), 404


        return jsonify({
            "success": True,
            "application_id": application_id,
            "status": status,
            "message": "Application updated."
        })


    finally:

        connection.close()


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


    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )