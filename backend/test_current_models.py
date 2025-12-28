"""
Test your current 2-model ensemble to find weaknesses
This will show you exactly what types of deepfakes your models miss
"""
import os
from models.ensemble_detector import predict_ensemble
from tqdm import tqdm
import json
import numpy as np

# Test on different deepfake types
test_sets = {
    'faceswap': './test_data/faceswap/',  # Face-swap deepfakes (DeepFaceLab, FaceSwap)
    'stable_diffusion': './test_data/stable_diffusion/',  # AI-generated images (SD)
    'midjourney': './test_data/midjourney/',  # AI-generated images (Midjourney)
    'dalle': './test_data/dalle/',  # AI-generated images (DALL-E)
    'gan_faces': './test_data/gan_faces/',  # GAN-generated faces (StyleGAN, etc.)
    'real_photos': './test_data/real/',  # Real images (should score LOW)
}

results = {}
all_errors = []

print("="*70)
print("TESTING CURRENT ENSEMBLE - WEAKNESS DETECTION")
print("="*70)

for category, path in test_sets.items():
    if not os.path.exists(path):
        print(f"\n⚠ Skipping {category} (directory not found: {path})")
        continue
    
    files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    if len(files) == 0:
        print(f"\n⚠ Skipping {category} (no images found)")
        continue
    
    scores = []
    confidences = []
    agreements = []
    errors = []
    
    print(f"\n{'='*70}")
    print(f"Testing: {category.upper()}")
    print(f"{'='*70}")
    print(f"Images found: {len(files)}")
    
    for img_name in tqdm(files, desc=f"{category}"):
        img_path = os.path.join(path, img_name)
        
        try:
            result = predict_ensemble(img_path)
            score = result['score']
            confidence = result['confidence']
            agreement = result['model_agreement']
            individual = result['individual_scores']
            
            scores.append(score)
            confidences.append(confidence)
            agreements.append(agreement)
            
            # Determine if this is an error
            expected_fake = category != 'real_photos'
            predicted_fake = score > 0.5
            
            is_error = predicted_fake != expected_fake
            is_confident_error = is_error and confidence > 0.75
            
            if is_confident_error:
                errors.append({
                    'image': img_name,
                    'category': category,
                    'score': float(score),
                    'confidence': float(confidence),
                    'agreement': agreement,
                    'individual_scores': [float(s) for s in individual],
                    'expected': 'fake' if expected_fake else 'real',
                    'predicted': 'fake' if predicted_fake else 'real'
                })
                all_errors.append(errors[-1])
        
        except Exception as e:
            print(f"\n✗ Error on {img_name}: {e}")
    
    if not scores:
        continue
    
    avg_score = np.mean(scores)
    std_score = np.std(scores)
    avg_confidence = np.mean(confidences)
    
    # Calculate accuracy
    if category == 'real_photos':
        correct = sum(1 for s in scores if s < 0.5)
        expected_range = "< 0.5 (low = good)"
    else:
        correct = sum(1 for s in scores if s > 0.5)
        expected_range = "> 0.5 (high = good)"
    
    accuracy = (correct / len(scores)) * 100
    
    # Count agreement types
    unanimous = agreements.count('unanimous')
    strong = agreements.count('strong_agreement')
    moderate = agreements.count('moderate_agreement')
    disagree = agreements.count('disagreement')
    
    results[category] = {
        'count': len(scores),
        'avg_score': float(avg_score),
        'std_score': float(std_score),
        'avg_confidence': float(avg_confidence),
        'accuracy': float(accuracy),
        'score_range': [float(min(scores)), float(max(scores))],
        'agreement_breakdown': {
            'unanimous': unanimous,
            'strong_agreement': strong,
            'moderate_agreement': moderate,
            'disagreement': disagree
        },
        'errors': errors[:10]  # Top 10 errors
    }
    
    # Print summary
    print(f"\n  Average score: {avg_score:.3f} ± {std_score:.3f}")
    print(f"  Expected range: {expected_range}")
    print(f"  Accuracy: {accuracy:.1f}%")
    print(f"  Avg confidence: {avg_confidence:.3f}")
    print(f"\n  Model Agreement:")
    print(f"    Unanimous: {unanimous} ({unanimous/len(scores)*100:.1f}%)")
    print(f"    Strong: {strong} ({strong/len(scores)*100:.1f}%)")
    print(f"    Moderate: {moderate} ({moderate/len(scores)*100:.1f}%)")
    print(f"    Disagreement: {disagree} ({disagree/len(scores)*100:.1f}%)")
    
    # Weakness assessment
    print(f"\n  ASSESSMENT:")
    if category == 'real_photos':
        if avg_score > 0.4:
            print(f"    ⚠⚠⚠ CRITICAL: Very high false positive rate!")
            print(f"    Models think real photos are fake")
        elif avg_score > 0.3:
            print(f"    ⚠ WARNING: High false positive rate")
        else:
            print(f"    ✓ Good performance on real photos")
    else:
        if avg_score < 0.6:
            print(f"    ⚠⚠⚠ CRITICAL WEAKNESS: Poor detection!")
            print(f"    Models struggle significantly with {category}")
        elif avg_score < 0.7:
            print(f"    ⚠ WARNING: Below target detection rate")
            print(f"    Models could improve on {category}")
        else:
            print(f"    ✓ Good detection of {category}")
    
    # Show sample errors
    if errors:
        print(f"\n  Sample Confident Errors (showing {min(3, len(errors))}):")
        for err in errors[:3]:
            print(f"    - {err['image']}")
            print(f"      Score: {err['score']:.3f} | Expected: {err['expected']} | Got: {err['predicted']}")
            print(f"      Individual models: {[f'{s:.2f}' for s in err['individual_scores']]}")

# Overall Summary
print(f"\n\n{'='*70}")
print("OVERALL SUMMARY")
print(f"{'='*70}")

if results:
    # Find weakest categories
    fake_categories = {k: v for k, v in results.items() if k != 'real_photos'}
    
    if fake_categories:
        weakest = min(fake_categories.items(), key=lambda x: x[1]['avg_score'])
        strongest = max(fake_categories.items(), key=lambda x: x[1]['avg_score'])
        
        print(f"\nWeakest Detection: {weakest[0].upper()}")
        print(f"  Average score: {weakest[1]['avg_score']:.3f}")
        print(f"  Accuracy: {weakest[1]['accuracy']:.1f}%")
        
        print(f"\nStrongest Detection: {strongest[0].upper()}")
        print(f"  Average score: {strongest[1]['avg_score']:.3f}")
        print(f"  Accuracy: {strongest[1]['accuracy']:.1f}%")
    
    # Check false positives
    if 'real_photos' in results:
        real = results['real_photos']
        print(f"\nFalse Positive Rate (Real Photos):")
        print(f"  Average score: {real['avg_score']:.3f}")
        print(f"  Accuracy: {real['accuracy']:.1f}%")
        if real['avg_score'] > 0.35:
            print(f"  ⚠ High false positive rate - too sensitive!")

# Save detailed report
report = {
    'results': results,
    'all_confident_errors': all_errors,
    'summary': {
        'total_categories_tested': len(results),
        'total_images_tested': sum(r['count'] for r in results.values())
    }
}

output_file = './models_cache/weakness_report.json'
with open(output_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n{'='*70}")
print(f"✓ Detailed report saved to: {output_file}")
print(f"{'='*70}")

# Recommendations
print(f"\n{'='*70}")
print("RECOMMENDATIONS")
print(f"{'='*70}")

if results:
    fake_cats = {k: v for k, v in results.items() if k != 'real_photos'}
    
    if fake_cats:
        # Find categories below 70% accuracy
        weak_cats = [k for k, v in fake_cats.items() if v['avg_score'] < 0.7]
        
        if weak_cats:
            print(f"\n📌 PRIORITY: Train specialist models for:")
            for cat in weak_cats:
                score = results[cat]['avg_score']
                acc = results[cat]['accuracy']
                print(f"   - {cat.upper()} (score: {score:.2f}, accuracy: {acc:.1f}%)")
            
            print(f"\n   Next step:")
            print(f"   1. Collect more {weak_cats[0]} images (1000+ fake, 1000+ real)")
            print(f"   2. Run: python train_specialist.py --category {weak_cats[0]}")
        else:
            print(f"\n✓ All categories performing well (>70% detection)")
            print(f"  Consider training a meta-classifier to optimize score fusion")
    
    if 'real_photos' in results and results['real_photos']['avg_score'] > 0.35:
        print(f"\n📌 ISSUE: High false positive rate on real photos")
        print(f"   - Current avg score: {results['real_photos']['avg_score']:.3f}")
        print(f"   - Target: < 0.30")
        print(f"   - Solution: Adjust thresholds or train with more diverse real images")

print(f"\n{'='*70}")
print("Testing complete. Check weakness_report.json for full details.")
print(f"{'='*70}\n")
