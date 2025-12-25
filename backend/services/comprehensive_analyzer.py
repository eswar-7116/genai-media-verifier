import os
from PIL import Image
import config
from models.ensemble_detector import predict_ensemble
from models.frequency_analyzer import analyze_frequency_domain
from models.face_analyzer import analyze_face
from models.metadata_analyzer import analyze_metadata


def analyze_image_comprehensive(image_path):
    """
    Comprehensive image analysis using all detection methods.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        dict: Complete analysis results with scores and breakdown
    """
    try:
        # Load image once for reuse
        image = Image.open(image_path).convert('RGB')
        
        results = {
            'neural_network': None,
            'frequency_domain': None,
            'facial_analysis': None,
            'metadata_forensics': None,
            'final_score': 0.0,
            'risk_level': 'Unknown',
            'confidence': 0.0
        }
        
        # 1. Neural Network Ensemble
        if config.NEURAL_ENSEMBLE_ENABLED:
            try:
                neural_result = predict_ensemble(image)
                results['neural_network'] = neural_result
            except Exception as e:
                print(f"Neural network analysis failed: {e}")
                results['neural_network'] = {'score': 0.5, 'error': str(e)}
        
        # 2. Frequency Domain Analysis
        if config.FREQUENCY_ANALYSIS_ENABLED:
            try:
                freq_result = analyze_frequency_domain(image)
                results['frequency_domain'] = freq_result
            except Exception as e:
                print(f"Frequency analysis failed: {e}")
                results['frequency_domain'] = {'score': 0.5, 'error': str(e)}
        
        # 3. Facial Analysis
        if config.FACE_ANALYSIS_ENABLED:
            try:
                face_result = analyze_face(image)
                results['facial_analysis'] = face_result
            except Exception as e:
                print(f"Face analysis failed: {e}")
                results['facial_analysis'] = {'score': 0.5, 'error': str(e)}
        
        # 4. Metadata Forensics
        if config.METADATA_ANALYSIS_ENABLED:
            try:
                metadata_result = analyze_metadata(image_path)
                results['metadata_forensics'] = metadata_result
            except Exception as e:
                print(f"Metadata analysis failed: {e}")
                results['metadata_forensics'] = {'score': 0.5, 'error': str(e)}
        
        # Combine all scores
        final_score, confidence = combine_scores(results)
        results['final_score'] = final_score
        results['confidence'] = confidence
        results['risk_level'] = determine_risk_level(final_score)
        
        return results
    
    except Exception as e:
        print(f"Comprehensive analysis error: {e}")
        return {
            'error': str(e),
            'final_score': 0.5,
            'risk_level': 'Unknown'
        }


def combine_scores(results):
    """
    Combine scores from all methods using weighted ensemble.
    
    Returns:
        tuple: (final_score, confidence)
    """
    weights = config.ENSEMBLE_WEIGHTS
    
    scores = []
    active_weights = []
    confidences = []
    
    # Neural Network
    if results['neural_network'] and 'score' in results['neural_network']:
        scores.append(results['neural_network']['score'])
        active_weights.append(weights['neural'])
        
        if 'confidence' in results['neural_network']:
            confidences.append(results['neural_network']['confidence'])
    
    # Frequency Domain
    if results['frequency_domain'] and 'score' in results['frequency_domain']:
        scores.append(results['frequency_domain']['score'])
        active_weights.append(weights['frequency'])
        confidences.append(0.8)  # Default confidence for frequency
    
    # Face Analysis
    if results['facial_analysis'] and 'score' in results['facial_analysis']:
        scores.append(results['facial_analysis']['score'])
        active_weights.append(weights['face'])
        confidences.append(0.7)  # Default confidence for face
    
    # Metadata
    if results['metadata_forensics'] and 'score' in results['metadata_forensics']:
        scores.append(results['metadata_forensics']['score'])
        active_weights.append(weights['metadata'])
        confidences.append(0.6)  # Default confidence for metadata
    
    if len(scores) == 0:
        return 0.5, 0.0
    
    # Normalize weights
    total_weight = sum(active_weights)
    normalized_weights = [w / total_weight for w in active_weights]
    
    # Calculate weighted score
    final_score = sum(s * w for s, w in zip(scores, normalized_weights))
    
    # Calculate overall confidence
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
    
    return final_score, avg_confidence


def determine_risk_level(score):
    """Convert score to risk level"""
    thresholds = config.RISK_THRESHOLDS
    
    if score >= thresholds['high']:
        return "High"
    elif score >= thresholds['medium']:
        return "Medium"
    else:
        return "Low"


def generate_detailed_breakdown(results):
    """Generate human-readable breakdown of analysis"""
    breakdown = []
    
    # Neural Network
    if results.get('neural_network'):
        nn = results['neural_network']
        breakdown.append(f"Neural Network Analysis: {nn.get('score', 0.0):.2f}")
        if 'model_agreement' in nn:
            breakdown.append(f"  - Model Agreement: {nn['model_agreement']}")
        if 'num_models' in nn:
            breakdown.append(f"  - Models Used: {nn['num_models']}")
    
    # Frequency Domain
    if results.get('frequency_domain'):
        freq = results['frequency_domain']
        breakdown.append(f"Frequency Analysis: {freq.get('score', 0.0):.2f}")
        if freq.get('fft_anomaly'):
            breakdown.append("  - FFT anomaly detected")
        if freq.get('dct_anomaly'):
            breakdown.append("  - DCT anomaly detected")
    
    # Face Analysis
    if results.get('facial_analysis'):
        face = results['facial_analysis']
        breakdown.append(f"Facial Analysis: {face.get('score', 0.0):.2f}")
        if face.get('face_detected'):
            breakdown.append("  - Face detected")
            if face.get('symmetry_anomaly'):
                breakdown.append("  - Asymmetry detected")
            if face.get('eye_anomaly'):
                breakdown.append("  - Eye quality issues")
            if face.get('texture_anomaly'):
                breakdown.append("  - Unnatural skin texture")
        else:
            breakdown.append("  - No face detected")
    
    # Metadata
    if results.get('metadata_forensics'):
        meta = results['metadata_forensics']
        breakdown.append(f"Metadata Forensics: {meta.get('score', 0.0):.2f}")
        if not meta.get('exif_present'):
            breakdown.append("  - No EXIF data found")
        if meta.get('ela_anomalies'):
            breakdown.append("  - Compression anomalies detected")
        software = meta.get('editing_software_detected', 'Unknown')
        if software != 'Unknown':
            breakdown.append(f"  - Software: {software}")
    
    return "\n".join(breakdown)
