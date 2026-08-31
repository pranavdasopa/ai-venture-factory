import os
from flask import Flask, request, jsonify, render_template
from app.agents.sai_agent import SAI

app = Flask(__name__)
sai = SAI()


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )