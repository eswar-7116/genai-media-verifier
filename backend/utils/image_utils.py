from PIL import Image

def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((299, 299))
    return img

if __name__ == "__main__":
    img = preprocess_image("uploads/test.jpg")
    img.show()
