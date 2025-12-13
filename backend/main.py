from services.report_generator import generate_report
from fastapi import FastAPI, UploadFile, File
import os, shutil

from utils.image_utils import preprocess_image
from models.deepfake_detector import predict_image


app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = preprocess_image(path)
    fake_prob = predict_image(image)

    if fake_prob > 0.7:
        risk = "High"
    elif fake_prob > 0.4:
        risk = "Medium"
    else:
        risk = "Low"

    report = generate_report(fake_prob, risk)

    return {
        "fake_probability": round(fake_prob, 2),
        "risk_level": risk,
        "report": report
    }
