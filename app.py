from flask import Flask, request, jsonify, Response
import os
import json
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
# AUDIO UPLOAD
# =====================================================

@app.route("/uploadAudio", methods=["POST"])
def upload_audio():

    try:

        # ---------------------------------------------
        # RECEIVE AUDIO FROM ESP32
        # ---------------------------------------------

        audio_data = request.get_data()

        print(
            "Audio received:",
            len(audio_data),
            "bytes"
        )

        if not audio_data:

            return Response(
                json.dumps({
                    "status": "error",
                    "message": "No audio received"
                }, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            ), 400


        # ---------------------------------------------
        # SAVE WAV
        # ---------------------------------------------

        filename = "/tmp/audio.wav"

        with open(filename, "wb") as f:
            f.write(audio_data)


        # ---------------------------------------------
        # SPEECH RECOGNITION
        # ---------------------------------------------

        recognizer = sr.Recognizer()

        with sr.AudioFile(filename) as source:

            audio = recognizer.record(source)


        print("Recognizing speech...")


        # ---------------------------------------------
        # HINDI + ENGLISH
        # ---------------------------------------------

        text = recognizer.recognize_google(
            audio,
            language="hi-IN"
        )


        print(
            "TRANSCRIPTION:",
            text
        )


        # ---------------------------------------------
        # RETURN UTF-8 JSON
        # ---------------------------------------------

        response_data = {
            "status": "ok",
            "transcription": text
        }


        return Response(
            json.dumps(
                response_data,
                ensure_ascii=False
            ),
            content_type="application/json; charset=utf-8"
        )


    # =================================================
    # SPEECH NOT UNDERSTOOD
    # =================================================

    except sr.UnknownValueError:

        print(
            "Speech not understood"
        )

        return Response(
            json.dumps({
                "status": "error",
                "message": "Speech not understood"
            }, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        ), 400


    # =================================================
    # GOOGLE SERVICE ERROR
    # =================================================

    except sr.RequestError as e:

        print(
            "Speech service error:",
            str(e)
        )

        return Response(
            json.dumps({
                "status": "error",
                "message": "Speech service error",
                "details": str(e)
            }, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        ), 500


    # =================================================
    # OTHER ERROR
    # =================================================

    except Exception as e:

        print(
            "SERVER ERROR:",
            str(e)
        )

        return Response(
            json.dumps({
                "status": "error",
                "message": str(e)
            }, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        ), 500


# =====================================================
# START SERVER
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
