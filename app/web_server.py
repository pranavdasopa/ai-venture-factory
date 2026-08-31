from flask import Flask, request, jsonify, render_template

from app.agents.sai_agent import SAI
from app.agents.opportunity_agent import OpportunityAgent
from app.agents.memory_agent import MemoryAgent

app = Flask(__name__)

sai = SAI()
opportunities = OpportunityAgent()
memory = MemoryAgent()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "company": "AI Venture Factory",
        "product": "SAI",
        "status": "ONLINE",
        "ai": "ONLINE",
        "memory": "ONLINE",
        "opportunities": "ONLINE"
    })


@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}
    message = str(data.get("message", "")).strip()

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


@app.route("/api/opportunities")
def get_opportunities():

    query = request.args.get("q", "").strip()

    try:
        results = opportunities.search(query)

        return jsonify({
            "success": True,
            "count": len(results),
            "opportunities": results
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/api/memory")
def get_memory():

    return jsonify({
        "success": True,
        "memory": memory.get_memory()
    })


@app.route("/api/goals", methods=["GET"])
def get_goals():

    data = memory.get_memory()

    return jsonify({
        "success": True,
        "goals": data["goals"]
    })


@app.route("/api/goals", methods=["POST"])
def add_goal():

    data = request.get_json() or {}

    goal = str(data.get("goal", "")).strip()

    if not goal:
        return jsonify({
            "success": False,
            "error": "Goal is required."
        }), 400

    memory.add_goal(goal)

    return jsonify({
        "success": True,
        "goal": goal,
        "goals": memory.get_memory()["goals"]
    })


if __name__ == "__main__":

    print("=" * 60)
    print("SAI — SAHAYAK AI")
    print("=" * 60)
    print("AI: ONLINE")
    print("Memory: ONLINE")
    print("Goals: ONLINE")
    print("Opportunity Engine: ONLINE")
    print("Web Server: ONLINE")
    print()
    print("http://127.0.0.1:5000")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )