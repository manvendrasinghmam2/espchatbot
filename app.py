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


@app.route("/uploadAudio", methods=["POST"])
def upload_audio():

    try:

        # ESP32 se complete WAV receive karo
        audio_data = request.get_data()

        print("Audio received:", len(audio_data), "bytes")

        if not audio_data:
            return jsonify({
                "status": "error",
                "message": "No audio received"
            }), 400

        # Temporary WAV file
        filename = "/tmp/audio.wav"

        with open(filename, "wb") as f:
            f.write(audio_data)

        # Speech recognition
        recognizer = sr.Recognizer()

        with sr.AudioFile(filename) as source:

            audio = recognizer.record(source)

        print("Recognizing speech...")

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

        print("Speech not understood")

        return jsonify({
            "status": "error",
            "message": "Speech not understood"
        }), 400

    except sr.RequestError as e:

        print("Google speech service error:", e)

        return jsonify({
            "status": "error",
            "message": "Speech service error",
            "details": str(e)
        }), 500

    except Exception as e:

        print("SERVER ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
