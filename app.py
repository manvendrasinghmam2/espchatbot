from flask import Flask, request, jsonify
import os
import speech_recognition as sr

app = Flask(__name__)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return "ESP32 Voice Server is ONLINE!"


# =====================================================
# HEALTH
# =====================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "online"
    })


# =====================================================
# TEST
# =====================================================

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


# =====================================================
# UPLOAD AUDIO
# =====================================================

@app.route("/uploadAudio", methods=["POST"])
def upload_audio():

    try:

        audio_data = request.get_data()

        if not audio_data:

            return jsonify({
                "status": "error",
                "message": "No audio received"
            }), 400


        print()
        print("==============================")
        print("AUDIO RECEIVED")
        print("==============================")
        print("Bytes:", len(audio_data))


        # =================================================
        # SAVE WAV
        # =================================================

        filename = "/tmp/audio.wav"

        with open(filename, "wb") as f:
            f.write(audio_data)


        # =================================================
        # SPEECH RECOGNIZER
        # =================================================

        recognizer = sr.Recognizer()


        # =================================================
        # READ WAV
        # =================================================

        with sr.AudioFile(filename) as source:

            audio = recognizer.record(source)


        # =================================================
        # ENGLISH FIRST
        # =================================================

        text = None

        try:

            text = recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            print()
            print("ENGLISH RESULT:")
            print(text)


        except sr.UnknownValueError:

            text = None


        except sr.RequestError as e:

            return jsonify({
                "status": "error",
                "message": "Speech service error",
                "details": str(e)
            }), 500


        # =================================================
        # IF ENGLISH FAILED -> HINDI
        # =================================================

        if not text:

            try:

                text = recognizer.recognize_google(
                    audio,
                    language="hi-IN"
                )

                print()
                print("HINDI RESULT:")
                print(text)


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


        # =================================================
        # FINAL RESULT
        # =================================================

        print()
        print("==============================")
        print("TRANSCRIPTION")
        print("==============================")
        print(text)
        print("==============================")


        return jsonify({
            "status": "ok",
            "transcription": text
        })


    # =====================================================
    # ERROR
    # =====================================================

    except Exception as e:

        print()
        print("==============================")
        print("ERROR")
        print("==============================")
        print(str(e))
        print("==============================")


        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =====================================================
# START
# =====================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
