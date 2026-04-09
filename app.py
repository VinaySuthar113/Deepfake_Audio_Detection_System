from flask import Flask, render_template, request, jsonify
import os
import uuid
import subprocess
import gdown
from eval import predict_audio

app = Flask(__name__)

# ✅ Model path
MODEL_PATH = "model.pth"

# ✅ Google Drive FILE ID
FILE_ID = "1Ad2PWuzmW_XObp2ojKS6uDjURuSSAtRw"

# ✅ Download model automatically
def download_model():
    if not os.path.exists(MODEL_PATH):
        print("📥 Downloading model from Google Drive...")

        url = f"https://drive.google.com/uc?id={FILE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)

        print("✅ Model downloaded successfully")

download_model()

# ✅ Temp folder
UPLOAD_FOLDER = "temp_audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🔧 Convert audio → WAV
def convert_to_wav(input_path, output_path):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "24000",
        output_path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise Exception("FFmpeg conversion failed")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        file = request.files["audio"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Save file
        ext = os.path.splitext(file.filename)[1] or ".webm"
        raw_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}{ext}")
        wav_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.wav")

        file.save(raw_path)

        # Convert
        convert_to_wav(raw_path, wav_path)

        # Predict
        result = predict_audio(wav_path, MODEL_PATH)

        # Cleanup
        os.remove(raw_path)
        os.remove(wav_path)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "prediction": "ERROR",
            "fake_probability": 0.0,
            "real_probability": 0.0,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)