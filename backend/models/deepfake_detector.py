import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load pretrained deepfake model
processor = AutoImageProcessor.from_pretrained(
    "dima806/deepfake_vs_real_image_detection",
    use_fast=True
)

model = AutoModelForImageClassification.from_pretrained(
    "dima806/deepfake_vs_real_image_detection"
).to(DEVICE)

model.eval()

def predict_image(image: Image.Image):
    inputs = processor(images=image, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

    fake_prob = probs[0][1].item()   # index 1 = fake
    return fake_prob
