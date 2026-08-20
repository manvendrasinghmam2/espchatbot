from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import os
import tempfile

app = Flask(__name__)

# =====================================================
# WHISPER MODEL
# =====================================================

print("Loading Whisper model...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Whisper model loaded!")

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
        "status": "online",
        "speech_engine": "local faster-whisper"
    })

# =====================================================
# UPLOAD AUDIO
# =====================================================

@app.route("/uploadAudio", methods=["POST"])
def upload_audio():

    temp_file = None

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

        # ---------------------------------------------
        # TEMP WAV FILE
        # ---------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as f:

            f.write(audio_data)
            temp_file = f.name

        print("Transcribing...")

        # ---------------------------------------------
        # WHISPER
        # ---------------------------------------------

        segments, info = model.transcribe(
            temp_file,
            beam_size=5,
            language=None,
            vad_filter=True
        )

        text_parts = []

        for segment in segments:

            text_parts.append(
                segment.text.strip()
            )

        text = " ".join(text_parts).strip()

        print()
        print("==============================")
        print("TRANSCRIPTION")
        print("==============================")
        print(text)
        print("==============================")

        # ---------------------------------------------
        # EMPTY SPEECH
        # ---------------------------------------------

        if not text:

            return jsonify({
                "status": "error",
                "message": "Speech not understood"
            }), 400

        # ---------------------------------------------
        # RESPONSE
        # ---------------------------------------------

        return jsonify({
            "status": "ok",
            "transcription": text
        })

    except Exception as e:

        print()
        print("==============================")
        print("ERROR")
        print("==============================")
        print(str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:

        if temp_file:

            try:
                os.remove(temp_file)
            except:
                pass


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
