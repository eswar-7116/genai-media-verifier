"""
Test and compare original vs fine-tuned models.
This helps you see the improvement from fine-tuning.
"""

import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CACHE_DIR = "./models_cache/huggingface"


def load_model(model_path, is_finetuned=False):
    """Load a model and processor"""
    try:
        processor = AutoImageProcessor.from_pretrained(model_path)
        model = AutoModelForImageClassification.from_pretrained(model_path).to(DEVICE)
        model.eval()
        return processor, model
    except Exception as e:
        print(f"Error loading model from {model_path}: {e}")
        return None, None


def predict_single_image(image_path, processor, model):
    """Get prediction for a single image"""
    try:
        image = Image.open(image_path).convert('RGB')
        inputs = processor(images=image, return_tensors="pt").to(DEVICE)
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
        
        fake_prob = probs[0][1].item()
        return fake_prob
    except Exception as e:
        print(f"Error predicting {image_path}: {e}")
        return None


def test_on_sample(data_path, processor, model, num_samples=50):
    """Test model on a sample of images from each category"""
    
    categories = {
        'real': 0,
        'dalle': 1,
        'gan_faces': 1,
        'midjourney': 1,
        'stable_diffusion': 1
    }
    
    results = {
        'correct': 0,
        'total': 0,
        'by_category': {}
    }
    
    for category, true_label in categories.items():
        category_path = data_path / category
        
        if not category_path.exists():
            print(f"⚠ Skipping {category} (folder not found)")
            continue
        
        # Get sample images
        images = list(category_path.glob('*.jpg')) + list(category_path.glob('*.png'))
        sample_images = images[:num_samples] if len(images) > num_samples else images
        
        print(f"\nTesting on {len(sample_images)} images from '{category}'...")
        
        category_correct = 0
        category_total = 0
        predictions = []
        
        for img_path in tqdm(sample_images, desc=category):
            pred_score = predict_single_image(img_path, processor, model)
            
            if pred_score is None:
                continue
            
            # Threshold at 0.5
            pred_label = 1 if pred_score > 0.5 else 0
            predictions.append(pred_score)
            
            if pred_label == true_label:
                category_correct += 1
                results['correct'] += 1
            
            category_total += 1
            results['total'] += 1
        
        if category_total > 0:
            accuracy = category_correct / category_total
            avg_score = np.mean(predictions) if predictions else 0
            
            results['by_category'][category] = {
                'accuracy': accuracy,
                'correct': category_correct,
                'total': category_total,
                'avg_prediction': avg_score
            }
            
            print(f"  Accuracy: {accuracy:.2%} ({category_correct}/{category_total})")
            print(f"  Avg prediction score: {avg_score:.3f}")
    
    overall_accuracy = results['correct'] / results['total'] if results['total'] > 0 else 0
    results['overall_accuracy'] = overall_accuracy
    
    return results


def compare_models():
    """Compare original and fine-tuned models"""
    
    data_path = Path("../test_data")
    
    if not data_path.exists():
        print(f"❌ Error: Data directory not found at {data_path}")
        return
    
    print("="*70)
    print("MODEL COMPARISON: Original vs Fine-tuned")
    print("="*70)
    
    # Test Original Model 1
    print("\n" + "="*70)
    print("Testing ORIGINAL Model 1: prithivMLmods/Deep-Fake-Detector-Model")
    print("="*70)
    
    processor1_orig, model1_orig = load_model(
        "prithivMLmods/Deep-Fake-Detector-Model"
    )
    
    if processor1_orig and model1_orig:
        results1_orig = test_on_sample(data_path, processor1_orig, model1_orig)
        print(f"\n✓ Overall Accuracy: {results1_orig['overall_accuracy']:.2%}")
    else:
        results1_orig = None
        print("❌ Could not load original model 1")
    
    # Test Fine-tuned Model 1
    finetuned1_path = Path("fine_tuned_models/prithiv_finetuned")
    if finetuned1_path.exists():
        print("\n" + "="*70)
        print("Testing FINE-TUNED Model 1")
        print("="*70)
        
        processor1_ft, model1_ft = load_model(str(finetuned1_path))
        
        if processor1_ft and model1_ft:
            results1_ft = test_on_sample(data_path, processor1_ft, model1_ft)
            print(f"\n✓ Overall Accuracy: {results1_ft['overall_accuracy']:.2%}")
            
            if results1_orig:
                improvement = results1_ft['overall_accuracy'] - results1_orig['overall_accuracy']
                print(f"📈 Improvement: {improvement:+.2%}")
        else:
            results1_ft = None
    else:
        print(f"\n⚠ Fine-tuned model 1 not found at {finetuned1_path}")
        results1_ft = None
    
    # Test Original Model 2
    print("\n" + "="*70)
    print("Testing ORIGINAL Model 2: dima806/deepfake_vs_real_image_detection")
    print("="*70)
    
    processor2_orig, model2_orig = load_model(
        "dima806/deepfake_vs_real_image_detection"
    )
    
    if processor2_orig and model2_orig:
        results2_orig = test_on_sample(data_path, processor2_orig, model2_orig)
        print(f"\n✓ Overall Accuracy: {results2_orig['overall_accuracy']:.2%}")
    else:
        results2_orig = None
        print("❌ Could not load original model 2")
    
    # Test Fine-tuned Model 2
    finetuned2_path = Path("fine_tuned_models/dima_finetuned")
    if finetuned2_path.exists():
        print("\n" + "="*70)
        print("Testing FINE-TUNED Model 2")
        print("="*70)
        
        processor2_ft, model2_ft = load_model(str(finetuned2_path))
        
        if processor2_ft and model2_ft:
            results2_ft = test_on_sample(data_path, processor2_ft, model2_ft)
            print(f"\n✓ Overall Accuracy: {results2_ft['overall_accuracy']:.2%}")
            
            if results2_orig:
                improvement = results2_ft['overall_accuracy'] - results2_orig['overall_accuracy']
                print(f"📈 Improvement: {improvement:+.2%}")
        else:
            results2_ft = None
    else:
        print(f"\n⚠ Fine-tuned model 2 not found at {finetuned2_path}")
        results2_ft = None
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    comparison = {
        'model1_original': results1_orig['overall_accuracy'] if results1_orig else None,
        'model1_finetuned': results1_ft['overall_accuracy'] if results1_ft else None,
        'model2_original': results2_orig['overall_accuracy'] if results2_orig else None,
        'model2_finetuned': results2_ft['overall_accuracy'] if results2_ft else None,
    }
    
    for key, value in comparison.items():
        if value is not None:
            print(f"{key}: {value:.2%}")
    
    # Save results
    output_file = "model_comparison_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'model1_original': results1_orig,
            'model1_finetuned': results1_ft,
            'model2_original': results2_orig,
            'model2_finetuned': results2_ft,
        }, f, indent=2, default=str)
    
    print(f"\n✓ Detailed results saved to {output_file}")


if __name__ == "__main__":
    compare_models()
