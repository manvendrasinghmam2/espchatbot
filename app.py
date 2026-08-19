from flask import Flask, request, jsonify
import os
import speech_recognition as sr

app = Flask(__name__)


@app.route("/")
def home():
    return "ESP32 Voice Server is ONLINE!"


@app.route("/health")
def health():
    return jsonify({
        "status": "online"
    })


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


@app.route("/uploadAudio", methods=["POST"])
def upload_audio():

    try:
        audio_data = request.get_data()

        if not audio_data:
            return jsonify({
                "status": "error",
                "message": "No audio received"
            }), 400

        print("Audio received:", len(audio_data), "bytes")

        # Temporary WAV file
        filename = "/tmp/audio.wav"

        with open(filename, "wb") as f:
            f.write(audio_data)

        recognizer = sr.Recognizer()

        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)

        # Hindi + English
        text = recognizer.recognize_google(
            audio,
            language="hi-IN"
        )

        print("TRANSCRIPTION:", text)

        return jsonify({
            "status": "ok",
            "transcription": text
        })

    except sr.UnknownValueError:

        return jsonify({
            "status": "error",
            "message": "Speech not understood"
        }), 400

    except sr.RequestError as e:

        return jsonify({
            "status": "error",
            "message": "Speech service error",
            "details": str(e)
        }), 500

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port
    )
