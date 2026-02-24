import os
from PIL import Image
import numpy as np
import config
from models.ensemble_detector import predict_ensemble
from models.frequency_analyzer import analyze_frequency_domain
from models.face_analyzer import analyze_face
from models.metadata_analyzer import analyze_metadata


def analyze_image_comprehensive(image_path):
    try:

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
        

        if config.NEURAL_ENSEMBLE_ENABLED:
            try:
                neural_result = predict_ensemble(image)
                results['neural_network'] = neural_result
            except Exception as e:
                print(f"Neural network analysis failed: {e}")
                results['neural_network'] = {'score': 0.5, 'error': str(e)}
        

        if config.FREQUENCY_ANALYSIS_ENABLED:
            try:
                freq_result = analyze_frequency_domain(image)
                results['frequency_domain'] = freq_result
            except Exception as e:
                print(f"Frequency analysis failed: {e}")
                results['frequency_domain'] = {'score': 0.5, 'error': str(e)}
        

        if config.FACE_ANALYSIS_ENABLED:
            try:
                face_result = analyze_face(image)
                results['facial_analysis'] = face_result
            except Exception as e:
                print(f"Face analysis failed: {e}")
                results['facial_analysis'] = {'score': 0.5, 'error': str(e)}
        

        if config.METADATA_ANALYSIS_ENABLED:
            try:
                metadata_result = analyze_metadata(image_path)
                results['metadata_forensics'] = metadata_result
            except Exception as e:
                print(f"Metadata analysis failed: {e}")
                results['metadata_forensics'] = {'score': 0.5, 'error': str(e)}
        

        final_score, confidence = combine_scores_aggressive(results)
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


def combine_scores_aggressive(results):
    weights = config.ENSEMBLE_WEIGHTS.copy()
    
    scores = []
    active_weights = []
    confidences = []
    

    nn_result = results.get('neural_network')
    if nn_result and 'score' in nn_result:
        nn_score = nn_result['score']
        nn_confidence = nn_result.get('confidence', 0.8)
        agreement = nn_result.get('model_agreement', 'unknown')
        
        scores.append(nn_score)
        base_weight = weights['neural']
        

        if nn_confidence > 0.95 and agreement == 'unanimous':
            base_weight *= 2.5

        elif nn_confidence > 0.93 and agreement in ['unanimous', 'strong_agreement']:
            base_weight *= 2.0

        elif nn_confidence > 0.90:
            base_weight *= 1.7

        elif nn_confidence > 0.85:
            base_weight *= 1.4
        
        active_weights.append(base_weight)
        confidences.append(nn_confidence)
    

    freq_result = results.get('frequency_domain')
    if freq_result and 'score' in freq_result:
        freq_score = freq_result['score']
        scores.append(freq_score)
        freq_weight = weights['frequency']
        

        if nn_result and 'score' in nn_result:
            nn_score = nn_result['score']

            if nn_score > 0.7 and freq_score > 0.6:
                freq_weight *= 1.4

            elif nn_score < 0.3 and freq_score < 0.4:
                freq_weight *= 1.4
        
        active_weights.append(freq_weight)
        confidences.append(0.7)
    

    face_result = results.get('facial_analysis')
    if face_result and 'score' in face_result:
        face_score = face_result['score']
        face_detected = face_result.get('face_detected', False)
        
        if not face_detected:

            if config.FACE_NOT_DETECTED_REDISTRIBUTE and len(active_weights) > 0:
                active_weights[0] += weights['face']
        else:
            scores.append(face_score)
            face_weight = weights['face']
            

            eye_score = face_result.get('eye_quality_score', 0.5)
            texture_score = face_result.get('skin_texture_score', 0.5)
            symmetry_score = face_result.get('symmetry_score', 0.5)
            

            high_anomalies = sum([
                eye_score > 0.7,
                texture_score > 0.7,
                symmetry_score > 0.65
            ])
            
            if high_anomalies >= 2:

                face_weight *= 1.5

                if nn_result and nn_result.get('score', 0) > 0.7:
                    face_weight *= 1.3
            
            active_weights.append(face_weight)
            confidences.append(0.75)
    

    meta_result = results.get('metadata_forensics')
    if meta_result and 'score' in meta_result:
        meta_score = meta_result['score']
        scores.append(meta_score)
        meta_weight = weights['metadata']
        

        if meta_result.get('exif_suspicious', False) or meta_result.get('ela_anomalies', False):
            meta_weight *= 1.4
        
        active_weights.append(meta_weight)
        confidences.append(0.65)
    
    if len(scores) == 0:
        return 0.5, 0.0
    

    if len(scores) >= 3:
        agreement_count = 0
        for i in range(len(scores)):
            for j in range(i+1, len(scores)):
                if abs(scores[i] - scores[j]) < 0.15:
                    agreement_count += 1
        

        if agreement_count >= 2:
            for idx in range(len(active_weights)):
                active_weights[idx] *= 1.2
    

    total_weight = sum(active_weights)
    normalized_weights = [w / total_weight for w in active_weights]
    

    final_score = sum(s * w for s, w in zip(scores, normalized_weights))
    

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
    

    if len(scores) >= 2:
        score_variance = np.var(scores)
        if score_variance < 0.04:
            avg_confidence = min(avg_confidence * 1.3, 1.0)
        elif score_variance < 0.08:
            avg_confidence = min(avg_confidence * 1.15, 1.0)
    
    return final_score, avg_confidence


def determine_risk_level(score):
    thresholds = config.RISK_THRESHOLDS
    
    if score >= thresholds['high']:
        return "High"
    elif score >= thresholds['medium']:
        return "Medium"
    else:
        return "Low"


def generate_detailed_breakdown(results):
    breakdown = []
    

    if results.get('neural_network'):
        nn = results['neural_network']
        breakdown.append(f"Neural Network Analysis: {nn.get('score', 0.0):.2f}")
        if 'model_agreement' in nn:
            breakdown.append(f"  - Model Agreement: {nn['model_agreement']}")
        if 'num_models' in nn:
            breakdown.append(f"  - Models Used: {nn['num_models']}")
    

    if results.get('frequency_domain'):
        freq = results['frequency_domain']
        breakdown.append(f"Frequency Analysis: {freq.get('score', 0.0):.2f}")
        if freq.get('fft_anomaly'):
            breakdown.append("  - FFT anomaly detected")
        if freq.get('dct_anomaly'):
            breakdown.append("  - DCT anomaly detected")
    

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
