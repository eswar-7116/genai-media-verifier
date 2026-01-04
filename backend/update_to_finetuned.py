"""
Script to update ensemble_detector.py to use fine-tuned models.
Run this AFTER training is complete.
"""

import os
from pathlib import Path

def update_ensemble_detector():
    """Update ensemble_detector.py to load fine-tuned models"""
    
    ensemble_file = Path("models/ensemble_detector.py")
    
    if not ensemble_file.exists():
        print(f"❌ Error: {ensemble_file} not found!")
        return
    
    # Read current content
    with open(ensemble_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if fine-tuned models exist
    prithiv_path = Path("fine_tuned_models/prithiv_finetuned")
    dima_path = Path("fine_tuned_models/dima_finetuned")
    
    use_prithiv = prithiv_path.exists()
    use_dima = dima_path.exists()
    
    if not use_prithiv and not use_dima:
        print("❌ No fine-tuned models found!")
        print("Please run train_deepfake_models.py first.")
        return
    
    # Replace model loading code for Model 1
    if use_prithiv:
        old_code_1 = '''            cache_dir = "./models_cache/huggingface"
            if SIGLIP_AVAILABLE:
                processor1 = SiglipImageProcessor.from_pretrained(
                    "prithivMLmods/Deep-Fake-Detector-Model",
                    cache_dir=cache_dir
                )
            else:
                processor1 = AutoImageProcessor.from_pretrained(
                    "prithivMLmods/Deep-Fake-Detector-Model",
                    cache_dir=cache_dir
                )
            model1 = AutoModelForImageClassification.from_pretrained(
                "prithivMLmods/Deep-Fake-Detector-Model",
                cache_dir=cache_dir
            ).to(DEVICE)'''
        
        new_code_1 = '''            # Load FINE-TUNED model
            fine_tuned_path = "./fine_tuned_models/prithiv_finetuned"
            if SIGLIP_AVAILABLE:
                processor1 = SiglipImageProcessor.from_pretrained(fine_tuned_path)
            else:
                processor1 = AutoImageProcessor.from_pretrained(fine_tuned_path)
            model1 = AutoModelForImageClassification.from_pretrained(
                fine_tuned_path
            ).to(DEVICE)'''
        
        content = content.replace(old_code_1, new_code_1)
        print("✓ Updated Model 1 to use fine-tuned version")
    
    # Replace model loading code for Model 2
    if use_dima:
        old_code_2 = '''            cache_dir = "./models_cache/huggingface"
            processor2 = AutoImageProcessor.from_pretrained(
                "dima806/deepfake_vs_real_image_detection",
                cache_dir=cache_dir
            )
            model2 = AutoModelForImageClassification.from_pretrained(
                "dima806/deepfake_vs_real_image_detection",
                cache_dir=cache_dir
            ).to(DEVICE)'''
        
        new_code_2 = '''            # Load FINE-TUNED model
            fine_tuned_path = "./fine_tuned_models/dima_finetuned"
            processor2 = AutoImageProcessor.from_pretrained(fine_tuned_path)
            model2 = AutoModelForImageClassification.from_pretrained(
                fine_tuned_path
            ).to(DEVICE)'''
        
        content = content.replace(old_code_2, new_code_2)
        print("✓ Updated Model 2 to use fine-tuned version")
    
    # Create backup
    backup_file = ensemble_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(open(ensemble_file, 'r', encoding='utf-8').read())
    print(f"✓ Created backup: {backup_file}")
    
    # Write updated content
    with open(ensemble_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✓ Successfully updated {ensemble_file}")
    print("\nYour ensemble detector now uses the fine-tuned models!")
    print("The models have been specifically trained on:")
    print("  - DALLE images")
    print("  - GAN faces")
    print("  - Midjourney images")
    print("  - Real photos")
    print("  - Stable Diffusion images")
    print("\nThey should now be much better at detecting these types of AI-generated content!")


if __name__ == "__main__":
    print("="*60)
    print("UPDATING ENSEMBLE DETECTOR TO USE FINE-TUNED MODELS")
    print("="*60 + "\n")
    update_ensemble_detector()
