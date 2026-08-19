from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "ESP32 Voice Server is ONLINE!"

@app.route("/test", methods=["POST"])
def test():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON received"
        }), 400

    print("ESP32 DATA:", data)

    return jsonify({
        "status": "ok",
        "message": "Data received"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
