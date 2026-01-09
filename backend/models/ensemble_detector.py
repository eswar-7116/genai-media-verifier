import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import numpy as np
from models.progress_tracker import get_progress_tracker

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class EnsembleDetector:
    def __init__(self):
        self.models = []
        self.processors = []
        self.model_names = []
        self.model_types = []
        
        # Load Model 1: Primary HuggingFace model (Siglip architecture)
        try:
            cache_dir = "./models_cache/huggingface"
            processor1 = AutoImageProcessor.from_pretrained(
                "prithivMLmods/Deep-Fake-Detector-Model",
                cache_dir=cache_dir,
                use_fast=True
            )
            model1 = AutoModelForImageClassification.from_pretrained(
                "prithivMLmods/Deep-Fake-Detector-Model",
                cache_dir=cache_dir
            ).to(DEVICE)
            model1.eval()
            
            self.models.append(model1)
            self.processors.append(processor1)
            self.model_names.append("prithivMLmods/Deep-Fake-Detector-Model")
            self.model_types.append("huggingface")
        except Exception as e:
            pass
        
        # Load Model 2: Alternative HuggingFace model (different architecture)
        try:
            cache_dir = "./models_cache/huggingface"
            processor2 = AutoImageProcessor.from_pretrained(
                "dima806/deepfake_vs_real_image_detection",
                cache_dir=cache_dir
            )
            model2 = AutoModelForImageClassification.from_pretrained(
                "dima806/deepfake_vs_real_image_detection",
                cache_dir=cache_dir
            ).to(DEVICE)
            model2.eval()
            
            self.models.append(model2)
            self.processors.append(processor2)
            self.model_names.append("dima806/deepfake_vs_real_image_detection")
            self.model_types.append("huggingface")
        except Exception as e:
            pass
    
    def predict_ensemble(self, image, silent=False):
        """
        Run all models and combine predictions with weighted voting.
        
        Args:
            image: PIL Image or path to image
            silent: If True, suppress progress updates (useful for batch/video analysis)
        
        Returns:
            dict: {
                'score': float (0-1, higher = more likely fake),
                'confidence': float,
                'individual_scores': list,
                'model_agreement': str
            }
        """
        tracker = get_progress_tracker()
        
        if not silent:
            tracker.update("🔍 Starting deepfake detection analysis...")
        
        if len(self.models) == 0:
            if not silent:
                tracker.update("❌ ERROR: No models available")
            return {
                'score': 0.5,
                'confidence': 0.0,
                'individual_scores': [],
                'model_agreement': 'no_models',
                'error': 'No models loaded'
            }
        
        if not silent:
            tracker.update(f"📊 Loaded {len(self.models)} AI models for analysis")
            tracker.update(f"🖥️ Using device: {DEVICE.upper()}")
        
        if isinstance(image, str):
            if not silent:
                tracker.update("📂 Loading image file...")
            image = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            if not silent:
                tracker.update("🖼️ Processing image...")
            image = image.convert('RGB')
        
        if not silent:
            tracker.update(f"✓ Image loaded: {image.size[0]}x{image.size[1]} pixels")
        
        predictions = []
        confidences = []
        
        # Run each model
        if not silent:
            tracker.update("\n🤖 Running neural network predictions...")
        for i, model in enumerate(self.models):
            try:
                if not silent:
                    model_short_name = self.model_names[i].split('/')[-1]
                    tracker.update(f"  [{i+1}/{len(self.models)}] {model_short_name}")
                    tracker.update(f"      → Preprocessing image...")
                
                if self.model_types[i] == "huggingface":
                    score, confidence = self._predict_huggingface(image, model, self.processors[i], i+1, len(self.models), silent)
                else:
                    score, confidence = 0.5, 0.0
                
                predictions.append(score)
                confidences.append(confidence)
                
                if not silent:
                    result = "FAKE" if score > 0.5 else "REAL"
                    tracker.update(f"      ✓ Prediction: {result} (score: {score:.3f}, confidence: {confidence:.3f})")
            except Exception as e:
                if not silent:
                    tracker.update(f"      ❌ Model failed: {e}")
                predictions.append(0.5)
                confidences.append(0.0)
        
        # Weighted voting based on confidence
        if not silent:
            tracker.update("\n🔄 Combining predictions...")
            tracker.update("   → Using weighted voting based on confidence scores...")
        final_score = self._weighted_voting(predictions, confidences)
        
        # Calculate agreement
        if not silent:
            tracker.update("   → Calculating model agreement...")
        agreement = self._calculate_agreement(predictions)
        
        # Calculate overall confidence
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        if not silent:
            tracker.update("\n📋 Analysis complete!")
            tracker.update(f"   Final Score: {final_score:.3f} ({'FAKE' if final_score > 0.5 else 'REAL'})")
            tracker.update(f"   Average Confidence: {avg_confidence:.3f}")
            tracker.update(f"   Model Agreement: {agreement.replace('_', ' ').title()}")
        
        return {
            'score': float(final_score),
            'confidence': float(avg_confidence),
            'individual_scores': [float(s) for s in predictions],
            'model_names': self.model_names,
            'model_agreement': agreement,
            'num_models': len(self.models)
        }
    
    def _predict_huggingface(self, image, model, processor, model_num, total_models, silent=False):
        """Run inference on HuggingFace model"""
        if not silent:
            tracker = get_progress_tracker()
            tracker.update(f"      → Running neural network inference...")
        inputs = processor(images=image, return_tensors="pt").to(DEVICE)
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
        
        fake_prob = probs[0][1].item()
        confidence = max(probs[0]).item()
        
        return fake_prob, confidence
    
    def _weighted_voting(self, predictions, confidences):
        """Combine predictions using confidence-weighted voting"""
        if len(predictions) == 0:
            return 0.5
        
        total_weight = sum(confidences)
        
        if total_weight == 0:
            return np.mean(predictions)
        
        weighted_sum = sum(p * c for p, c in zip(predictions, confidences))
        final_score = weighted_sum / total_weight
        
        return final_score
    
    def _calculate_agreement(self, predictions):
        """Calculate how much models agree"""
        if len(predictions) < 2:
            return "single_model"
        
        pred_array = np.array(predictions)
        std = np.std(pred_array)
        
        if std < 0.1:
            return "unanimous"
        elif std < 0.2:
            return "strong_agreement"
        elif std < 0.3:
            return "moderate_agreement"
        else:
            return "disagreement"


# Global instance
_ensemble_detector = None

def get_ensemble_detector():
    global _ensemble_detector
    if _ensemble_detector is None:
        _ensemble_detector = EnsembleDetector()
    return _ensemble_detector


def predict_ensemble(image, silent=False):
    """Convenience function"""
    detector = get_ensemble_detector()
    return detector.predict_ensemble(image, silent=silent)
