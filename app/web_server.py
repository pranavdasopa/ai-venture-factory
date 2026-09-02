import json
import os

from flask import Flask, request, jsonify, render_template

from app.agents.sai_agent import SAI
from app.agents.opportunity_agent import OpportunityAgent
from app.agents.company_builder_agent import CompanyBuilderAgent

from app.core.database import (
    get_connection,
    initialize_database
)


# ==========================================
# APPLICATION
# ==========================================

app = Flask(__name__)

initialize_database()

sai = SAI()
opportunity_agent = OpportunityAgent()
company_builder = CompanyBuilderAgent()


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

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            INSERT INTO users
            (name, email, goal, skills)
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

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        connection.close()


@app.route("/api/profile/<int:user_id>")
def get_profile(user_id):

    connection = get_connection()

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

@app.route("/api/goals")
def get_goals():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT title
        FROM tasks
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return jsonify({
        "success": True,
        "goals": [
            row["title"]
            for row in rows
        ]
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

    cursor = connection.execute(
        """
        INSERT INTO tasks
        (title, description, owner, status, priority)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            goal,
            "User goal",
            "User",
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

    if query:

        results = opportunity_agent.search(
            query
        )

        return jsonify({
            "success": True,
            "personalized": False,
            "opportunities": results
        })

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

    results = opportunity_agent.search()

    return jsonify({
        "success": True,
        "personalized": False,
        "opportunities": results
    })


# ==========================================
# COMPANY BUILDER
# ==========================================

@app.route("/api/companies/build", methods=["POST"])
def build_company():

    data = request.get_json() or {}

    idea = str(
        data.get("idea", "")
    ).strip()

    user_id = data.get(
        "user_id"
    )

    if not idea:

        return jsonify({
            "success": False,
            "error": "Startup idea is required."
        }), 400

    if len(idea) < 10:

        return jsonify({
            "success": False,
            "error": "Startup idea is too short."
        }), 400

    if user_id is not None:

        try:

            user_id = int(user_id)

        except (ValueError, TypeError):

            return jsonify({
                "success": False,
                "error": "Invalid user_id."
            }), 400

    try:

        # ----------------------------------
        # Generate company blueprint
        # ----------------------------------

        blueprint = company_builder.build(
            idea
        )

        # ----------------------------------
        # Save everything atomically
        # ----------------------------------

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                INSERT INTO companies
                (
                    user_id,
                    name,
                    idea,
                    industry,
                    status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    blueprint["company_name"],
                    idea,
                    blueprint["industry"],
                    "blueprint"
                )
            )

            company_id = cursor.lastrowid

            # ----------------------------------
            # Save blueprint
            # ----------------------------------

            connection.execute(
                """
                INSERT INTO company_blueprints
                (
                    company_id,
                    problem,
                    target_customer,
                    proposed_solution,
                    value_proposition,
                    market_hypothesis,
                    competitors,
                    business_model,
                    pricing_hypothesis,
                    mvp_scope,
                    technical_architecture,
                    technology_stack,
                    risks,
                    validation_experiments,
                    next_actions,
                    raw_response
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    blueprint["problem"],
                    blueprint["target_customer"],
                    blueprint["proposed_solution"],
                    blueprint["value_proposition"],
                    blueprint["market_hypothesis"],
                    json.dumps(
                        blueprint["competitors"]
                    ),
                    blueprint["business_model"],
                    blueprint["pricing_hypothesis"],
                    json.dumps(
                        blueprint["mvp_scope"]
                    ),
                    blueprint["technical_architecture"],
                    json.dumps(
                        blueprint["technology_stack"]
                    ),
                    json.dumps(
                        blueprint["risks"]
                    ),
                    json.dumps(
                        blueprint["validation_experiments"]
                    ),
                    json.dumps(
                        blueprint["next_actions"]
                    ),
                    json.dumps(
                        blueprint
                    )
                )
            )

            # ----------------------------------
            # Save execution tasks
            # ----------------------------------

            for position, task in enumerate(
                blueprint["execution_tasks"]
            ):

                connection.execute(
                    """
                    INSERT INTO execution_tasks
                    (
                        company_id,
                        title,
                        description,
                        department,
                        owner,
                        priority,
                        status,
                        position
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        company_id,
                        task["title"],
                        task["description"],
                        task["department"],
                        None,
                        task["priority"],
                        "todo",
                        position
                    )
                )

            connection.commit()

        except Exception:

            connection.rollback()

            raise

        finally:

            connection.close()


        return jsonify({
            "success": True,
            "company_id": company_id,
            "company": blueprint
        }), 201


    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ==========================================
# LIST COMPANIES
# ==========================================

@app.route("/api/companies")
def list_companies():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            user_id,
            name,
            idea,
            industry,
            status,
            created_at,
            updated_at
        FROM companies
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return jsonify({
        "success": True,
        "companies": [
            dict(row)
            for row in rows
        ]
    })


# ==========================================
# GET COMPANY
# ==========================================

@app.route("/api/companies/<int:company_id>")
def get_company(company_id):

    connection = get_connection()

    company = connection.execute(
        """
        SELECT
            id,
            user_id,
            name,
            idea,
            industry,
            status,
            created_at,
            updated_at
        FROM companies
        WHERE id = ?
        """,
        (company_id,)
    ).fetchone()

    if not company:

        connection.close()

        return jsonify({
            "success": False,
            "error": "Company not found."
        }), 404


    blueprint = connection.execute(
        """
        SELECT *
        FROM company_blueprints
        WHERE company_id = ?
        """,
        (company_id,)
    ).fetchone()


    tasks = connection.execute(
        """
        SELECT
            id,
            company_id,
            title,
            description,
            department,
            owner,
            priority,
            status,
            position,
            created_at,
            updated_at
        FROM execution_tasks
        WHERE company_id = ?
        ORDER BY position ASC
        """,
        (company_id,)
    ).fetchall()


    connection.close()


    blueprint_data = None

    if blueprint:

        blueprint_data = dict(
            blueprint
        )

        json_fields = [
            "competitors",
            "mvp_scope",
            "technology_stack",
            "risks",
            "validation_experiments",
            "next_actions"
        ]

        for field in json_fields:

            try:

                blueprint_data[field] = json.loads(
                    blueprint_data[field]
                )

            except (
                TypeError,
                json.JSONDecodeError
            ):

                pass


    return jsonify({
        "success": True,
        "company": dict(company),
        "blueprint": blueprint_data,
        "execution_tasks": [
            dict(task)
            for task in tasks
        ]
    })


# ==========================================
# COMPANY TASKS
# ==========================================

@app.route("/api/companies/<int:company_id>/tasks")
def company_tasks(company_id):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            company_id,
            title,
            description,
            department,
            owner,
            priority,
            status,
            position,
            created_at,
            updated_at
        FROM execution_tasks
        WHERE company_id = ?
        ORDER BY position ASC
        """,
        (company_id,)
    ).fetchall()

    connection.close()

    return jsonify({
        "success": True,
        "company_id": company_id,
        "tasks": [
            dict(row)
            for row in rows
        ]
    })


# ==========================================
# UPDATE COMPANY TASK
# ==========================================

@app.route(
    "/api/companies/<int:company_id>/tasks/<int:task_id>",
    methods=["PATCH"]
)
def update_company_task(
    company_id,
    task_id
):

    data = request.get_json() or {}

    status = data.get("status")
    priority = data.get("priority")

    allowed_statuses = [
        "todo",
        "in_progress",
        "blocked",
        "done"
    ]

    allowed_priorities = [
        "high",
        "medium",
        "low"
    ]

    if status is not None:

        status = str(status)

        if status not in allowed_statuses:

            return jsonify({
                "success": False,
                "error": "Invalid status."
            }), 400


    if priority is not None:

        priority = str(priority)

        if priority not in allowed_priorities:

            return jsonify({
                "success": False,
                "error": "Invalid priority."
            }), 400


    if status is None and priority is None:

        return jsonify({
            "success": False,
            "error": "Nothing to update."
        }), 400


    connection = get_connection()

    task = connection.execute(
        """
        SELECT id
        FROM execution_tasks
        WHERE id = ?
        AND company_id = ?
        """,
        (
            task_id,
            company_id
        )
    ).fetchone()

    if not task:

        connection.close()

        return jsonify({
            "success": False,
            "error": "Task not found."
        }), 404


    fields = []
    values = []

    if status is not None:

        fields.append(
            "status = ?"
        )

        values.append(status)

    if priority is not None:

        fields.append(
            "priority = ?"
        )

        values.append(priority)


    fields.append(
        "updated_at = CURRENT_TIMESTAMP"
    )

    values.extend([
        task_id,
        company_id
    ])


    connection.execute(
        f"""
        UPDATE execution_tasks
        SET {", ".join(fields)}
        WHERE id = ?
        AND company_id = ?
        """,
        values
    )

    connection.commit()

    connection.close()


    return jsonify({
        "success": True,
        "message": "Task updated."
    })


# ==========================================
# RUN LOCAL SERVER
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