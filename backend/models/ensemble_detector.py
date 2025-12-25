import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
try:
    from transformers import SiglipImageProcessor
    SIGLIP_AVAILABLE = True
except ImportError:
    SIGLIP_AVAILABLE = False
from PIL import Image
import numpy as np

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
            ).to(DEVICE)
            model1.eval()
            
            self.models.append(model1)
            self.processors.append(processor1)
            self.model_names.append("Primary-DeepFake-Detector")
            self.model_types.append("huggingface")
            print("✓ Loaded Primary DeepFake Detector (Siglip)")
        except Exception as e:
            print(f"✗ Failed to load primary model: {e}")
        
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
            self.model_names.append("Alternative-DeepFake-Detector")
            self.model_types.append("huggingface")
            print("✓ Loaded Alternative DeepFake Detector")
        except Exception as e:
            print(f"✗ Failed to load alternative HF model: {e}")
        
        # Note: EfficientNet-B0 was removed because its classifier layer was untrained
        # and only giving random predictions. We rely on the 2 specialized deepfake models above.
        
        print(f"Ensemble initialized with {len(self.models)} diverse models")
    
    def predict_ensemble(self, image):
        """
        Run all models and combine predictions with weighted voting.
        
        Returns:
            dict: {
                'score': float (0-1, higher = more likely fake),
                'confidence': float,
                'individual_scores': list,
                'model_agreement': str
            }
        """
        if len(self.models) == 0:
            return {
                'score': 0.5,
                'confidence': 0.0,
                'individual_scores': [],
                'model_agreement': 'no_models',
                'error': 'No models loaded'
            }
        
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            image = image.convert('RGB')
        
        predictions = []
        confidences = []
        
        # Run each model
        for i, model in enumerate(self.models):
            try:
                if self.model_types[i] == "huggingface":
                    score, confidence = self._predict_huggingface(image, model, self.processors[i])
                else:
                    score, confidence = 0.5, 0.0
                
                predictions.append(score)
                confidences.append(confidence)
            except Exception as e:
                print(f"Model {self.model_names[i]} failed: {e}")
                predictions.append(0.5)
                confidences.append(0.0)
        
        # Weighted voting based on confidence
        final_score = self._weighted_voting(predictions, confidences)
        
        # Calculate agreement
        agreement = self._calculate_agreement(predictions)
        
        # Calculate overall confidence
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        return {
            'score': float(final_score),
            'confidence': float(avg_confidence),
            'individual_scores': [float(s) for s in predictions],
            'model_names': self.model_names,
            'model_agreement': agreement,
            'num_models': len(self.models)
        }
    
    def _predict_huggingface(self, image, model, processor):
        """Run inference on HuggingFace model"""
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


def predict_ensemble(image):
    """Convenience function"""
    detector = get_ensemble_detector()
    return detector.predict_ensemble(image)
