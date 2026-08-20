from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import os
import tempfile

app = Flask(__name__)

# =====================================================
# WHISPER
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

        # -------------------------------------------------
        # RECEIVE WAV
        # -------------------------------------------------

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

        # -------------------------------------------------
        # SAVE TEMP WAV
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as f:

            f.write(audio_data)
            temp_file = f.name

        print("Transcribing...")

        # -------------------------------------------------
        # FASTER WHISPER
        # -------------------------------------------------
        #
        # language=None:
        # Hindi -> Hindi
        # English -> English
        # Mixed speech -> automatic detection
        #

        segments, info = model.transcribe(
            temp_file,
            beam_size=5,
            language=None,
            vad_filter=True
        )

        # -------------------------------------------------
        # COLLECT TEXT
        # -------------------------------------------------

        text_parts = []

        for segment in segments:

            part = segment.text.strip()

            if part:
                text_parts.append(part)

        text = " ".join(text_parts).strip()

        # -------------------------------------------------
        # SERVER LOG
        # -------------------------------------------------

        print()
        print("==============================")
        print("DETECTED LANGUAGE")
        print("==============================")
        print(info.language)

        print()
        print("==============================")
        print("TRANSCRIPTION")
        print("==============================")
        print(text)
        print("==============================")

        # -------------------------------------------------
        # EMPTY
        # -------------------------------------------------

        if not text:

            return jsonify({
                "status": "error",
                "message": "Speech not understood"
            }), 400

        # -------------------------------------------------
        # SEND TO ESP32
        # -------------------------------------------------

        return jsonify({
            "status": "ok",
            "transcription": text
        })

    except Exception as e:

        print()
        print("==============================")
        print("SERVER ERROR")
        print("==============================")
        print(str(e))
        print("==============================")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:

        # -------------------------------------------------
        # DELETE TEMP FILE
        # -------------------------------------------------

        if temp_file:

            try:
                os.remove(temp_file)

            except Exception:
                pass


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
