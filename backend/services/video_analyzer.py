import os
from PIL import Image
from utils.video_utils import extract_frames
from models.deepfake_detector import predict_image
from services.report_generator import generate_report

def analyze_video(video_path):
    frames_dir = "temp_frames"
    extract_frames(video_path, frames_dir, fps=1)

    frame_scores = []

    for frame in os.listdir(frames_dir):
        frame_path = os.path.join(frames_dir, frame)

        try:
            img = Image.open(frame_path).convert("RGB")
            prob = predict_image(img)
            frame_scores.append(prob)
        except:
            continue

    if not frame_scores:
        return None

    avg_prob = sum(frame_scores) / len(frame_scores)

    if avg_prob > 0.7:
        risk = "High"
    elif avg_prob > 0.4:
        risk = "Medium"
    else:
        risk = "Low"

    report = generate_report(
        media_type="video",
        fake_probability=avg_prob,
        risk_level=risk,
        frames_analyzed=len(frame_scores)
    )

    return {
        "frames_analyzed": len(frame_scores),
        "average_fake_probability": round(avg_prob, 2),
        "risk_level": risk,
        "report": report
    }

