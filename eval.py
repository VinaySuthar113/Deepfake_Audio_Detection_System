import torch
import numpy as np
import librosa
import yaml
from torch.nn import functional as F
from model import RawNet

CONFIG_PATH = "model_config_RawNet.yaml"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = None


def load_model(model_path):
    global model

    if model is not None:
        return

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    model = RawNet(config["model"], device)

    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)

    model.to(device)
    model.eval()

    print("✅ Model loaded")


def pad_audio(audio, max_len=96000):
    if len(audio) >= max_len:
        return audio[:max_len]

    padded = np.zeros(max_len)
    padded[:len(audio)] = audio
    return padded


def preprocess_audio(audio_path):
    try:
        audio, sr = librosa.load(audio_path, sr=None)
    except:
        return None

    if audio is None or len(audio) == 0:
        return None

    audio, _ = librosa.effects.trim(audio)

    if len(audio) < 1000:
        return None

    if np.isnan(audio).any():
        return None

    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    if sr != 24000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=24000)

    audio = pad_audio(audio)

    audio = torch.tensor(audio).float().unsqueeze(0)

    return audio


def predict_audio(audio_path, model_path):
    load_model(model_path)

    audio = preprocess_audio(audio_path)

    if audio is None:
        return {
            "prediction": "INVALID",
            "fake_probability": 0.0,
            "real_probability": 0.0
        }

    audio = audio.to(device)

    try:
        with torch.no_grad():
            logits, _ = model(audio)

            if torch.isnan(logits).any():
                return {"prediction": "ERROR", "fake_probability": 0.0, "real_probability": 0.0}

            probs = F.softmax(logits, dim=-1)

        fake_prob = probs[0][0].item()
        real_prob = probs[0][1].item()

        prediction = "FAKE" if fake_prob > 0.6 else "REAL"

        return {
            "prediction": prediction,
            "fake_probability": round(fake_prob, 3),
            "real_probability": round(real_prob, 3)
        }

    except Exception as e:
        return {
            "prediction": "ERROR",
            "fake_probability": 0.0,
            "real_probability": 0.0,
            "message": str(e)
        }