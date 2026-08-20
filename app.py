from flask import Flask, request, Response
import os
import json
from openai import OpenAI

app = Flask(__name__)

# =====================================================
# OPENAI
# =====================================================

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


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

    return Response(
        json.dumps({
            "status": "online"
        }, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


# =====================================================
# UPLOAD AUDIO
# =====================================================

@app.route("/uploadAudio", methods=["POST"])
def upload_audio():

    try:

        # ---------------------------------------------
        # RECEIVE ESP32 WAV
        # ---------------------------------------------

        audio_data = request.get_data()

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
        # WHISPER TRANSCRIPTION
        # ---------------------------------------------

        with open(filename, "rb") as audio_file:

            transcription = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )


        text = transcription.text.strip()


        # ---------------------------------------------
        # SERVER LOG
        # ---------------------------------------------

        print(
            "TRANSCRIPTION:",
            text
        )


        # ---------------------------------------------
        # SEND UTF-8 JSON TO ESP32
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
    # ERROR
    # =================================================

    except Exception as e:

        print(
            "ERROR:",
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
