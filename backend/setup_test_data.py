"""
Script to help you organize test datasets
Run this to create the proper folder structure
"""
import os

# Create test data structure
base_dir = './test_data'

categories = [
    'faceswap',           # Face-swap deepfakes (DeepFaceLab, FaceSwap, etc.)
    'stable_diffusion',   # Stable Diffusion generated images
    'midjourney',         # Midjourney generated images
    'dalle',              # DALL-E generated images
    'gan_faces',          # GAN-generated faces (StyleGAN, ProGAN, etc.)
    'real',               # Real photos (from cameras, phones)
]

print("Creating test data directories...")

for category in categories:
    path = os.path.join(base_dir, category)
    os.makedirs(path, exist_ok=True)
    print(f"✓ Created: {path}")

print("\n" + "="*70)
print("DIRECTORY STRUCTURE CREATED")
print("="*70)

print(f"\nNow add images to these folders:")
print(f"  {base_dir}/")

for category in categories:
    print(f"    ├── {category}/  <- Add {category} images here")

print(f"\n{'='*70}")
print("WHERE TO GET TEST IMAGES")
print(f"{'='*70}\n")

print("1. FACESWAP (Deepfake videos/images):")
print("   - FaceForensics++: https://github.com/ondyari/FaceForensics")
print("   - Celeb-DF: https://github.com/yuezunli/celeb-deepfakeforensics")
print("   - Extract frames from deepfake videos")
print("   - Aim for: 50-100 images\n")

print("2. STABLE DIFFUSION:")
print("   - Generate yourself: https://stablediffusionweb.com/")
print("   - Lexica: https://lexica.art/ (download SD images)")
print("   - Civitai: https://civitai.com/ (many SD examples)")
print("   - Aim for: 50-100 images\n")

print("3. MIDJOURNEY:")
print("   - Midjourney Showcase: https://www.midjourney.com/showcase")
print("   - Discord community images")
print("   - Aim for: 50-100 images\n")

print("4. DALL-E:")
print("   - OpenAI examples: https://labs.openai.com/")
print("   - Reddit r/dalle2")
print("   - Aim for: 50-100 images\n")

print("5. GAN FACES:")
print("   - ThisPersonDoesNotExist: https://thispersondoesnotexist.com/")
print("   - Generated Photos: https://generated.photos/")
print("   - StyleGAN samples")
print("   - Aim for: 50-100 images\n")

print("6. REAL PHOTOS:")
print("   - Your own photos from phone/camera")
print("   - FFHQ dataset: https://github.com/NVlabs/ffhq-dataset")
print("   - CelebA: http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html")
print("   - Unsplash: https://unsplash.com/ (royalty free)")
print("   - Aim for: 100-200 images (diverse!)\n")

print(f"{'='*70}")
print("MINIMUM TO START")
print(f"{'='*70}\n")

print("You can start testing with as few as:")
print("  - 20-30 images per fake category")
print("  - 50+ real photos")
print("\nBut more is better for accurate assessment.\n")

print(f"{'='*70}")
print("AFTER ADDING IMAGES")
print(f"{'='*70}\n")

print("Run the test script:")
print("  python test_current_models.py")
print("\nThis will:")
print("  1. Test your 2 current models on all categories")
print("  2. Show which types they detect well vs. poorly")
print("  3. Generate weakness_report.json with detailed analysis")
print("  4. Tell you which specialist model to train next\n")
