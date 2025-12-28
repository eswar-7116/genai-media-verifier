"""
Comprehensive Video Deepfake Detector - HYBRID APPROACH
Combines all Layer 1 and Layer 2 analyses
"""
import os
from PIL import Image
import numpy as np

# Layer 1
from models.video.metadata_analyzer import analyze_video_metadata
from models.video.frame_extractor import smart_frame_extraction

# Layer 2A - Visual
from models.ensemble_detector import predict_ensemble
from models.face_analyzer import analyze_face
from models.frequency_analyzer import analyze_frequency_domain
from models.video.temporal_analyzer import analyze_temporal_consistency
from models.video.video_3d_model import analyze_with_3d_model

# Layer 2B - Audio
from models.video.audio_analyzer import analyze_audio_stream

# Layer 2C - Physiological
from models.video.physiological_analyzer import analyze_physiological_signals

# Layer 2D - Physics
from models.video.physics_checker import analyze_physics_consistency


def analyze_video_comprehensive(video_path, output_dir="temp_frames"):
    """
    Comprehensive hybrid video deepfake detection
    
    Returns:
        dict: Complete analysis results with multi-modal scoring
    """
    try:
        print(f"\n{'='*60}")
        print(f"HYBRID VIDEO DEEPFAKE DETECTION")
        print(f"{'='*60}\n")
        
        results = {
            'layer1_metadata': None,
            'layer2a_frame_based': None,
            'layer2a_3d_video': None,
            'layer2a_temporal': None,
            'layer2b_audio': None,
            'layer2c_physiological': None,
            'layer2d_physics': None,
            'final_score': 0.0,
            'risk_level': 'Unknown',
            'confidence': 0.0,
            'method_breakdown': {}
        }
        
        # =====================================================
        # LAYER 1: Pre-Analysis (Metadata & Quick Checks)
        # =====================================================
        print("LAYER 1: Metadata Analysis...")
        metadata_result = analyze_video_metadata(video_path)
        results['layer1_metadata'] = metadata_result
        
        has_audio = metadata_result.get('has_audio', False)
        print(f"  ✓ Metadata score: {metadata_result.get('score', 0):.2f}")
        print(f"  ✓ Audio present: {has_audio}")
        
        # =====================================================
        # LAYER 2: Content-Based Multi-Modal Analysis
        # =====================================================
        
        # Smart frame extraction
        print("\nLAYER 2A: Extracting frames intelligently...")
        frame_data = smart_frame_extraction(video_path, output_dir, target_frames=50)
        
        if not frame_data or len(frame_data['frames']) == 0:
            return {
                'error': 'Failed to extract frames',
                'final_score': 0.5
            }
        
        frame_paths = frame_data['frames']
        timestamps = frame_data['timestamps']
        print(f"  ✓ Extracted {len(frame_paths)} frames")
        print(f"  ✓ Frames with faces: {len(frame_data.get('face_frames', []))}")
        
        # =====================================================
        # LAYER 2A: VISUAL STREAM - Frame-Based Analysis
        # =====================================================
        print("\nLAYER 2A (Option 1): Frame-Based Analysis...")
        
        frame_results = {
            'ensemble_scores': [],
            'face_scores': [],
            'frequency_scores': [],
            'avg_ensemble': 0.0,
            'avg_face': 0.0,
            'avg_frequency': 0.0
        }
        
        for idx, frame_path in enumerate(frame_paths):
            try:
                img = Image.open(frame_path).convert('RGB')
                
                # 1. Ensemble detector
                ensemble_result = predict_ensemble(img)
                frame_results['ensemble_scores'].append(ensemble_result.get('score', 0.5))
                
                # 2. Face analysis (if face present)
                face_result = analyze_face(img)
                if face_result.get('face_detected', False):
                    frame_results['face_scores'].append(face_result.get('score', 0.5))
                
                # 3. Frequency analysis
                freq_result = analyze_frequency_domain(img)
                frame_results['frequency_scores'].append(freq_result.get('score', 0.5))
                
                if (idx + 1) % 10 == 0:
                    print(f"  ✓ Processed {idx + 1}/{len(frame_paths)} frames")
                    
            except Exception as e:
                print(f"  ✗ Frame {idx} error: {e}")
                continue
        
        # Calculate averages
        if frame_results['ensemble_scores']:
            frame_results['avg_ensemble'] = np.mean(frame_results['ensemble_scores'])
            frame_results['max_ensemble'] = np.max(frame_results['ensemble_scores'])
        
        if frame_results['face_scores']:
            frame_results['avg_face'] = np.mean(frame_results['face_scores'])
        
        if frame_results['frequency_scores']:
            frame_results['avg_frequency'] = np.mean(frame_results['frequency_scores'])
        
        results['layer2a_frame_based'] = frame_results
        
        print(f"  ✓ Avg Ensemble Score: {frame_results['avg_ensemble']:.2f}")
        print(f"  ✓ Max Ensemble Score: {frame_results.get('max_ensemble', 0):.2f}")
        
        # =====================================================
        # LAYER 2A: VISUAL STREAM - Temporal Analysis
        # =====================================================
        print("\nLAYER 2A: Temporal Consistency Analysis...")
        temporal_result = analyze_temporal_consistency(frame_paths, timestamps)
        results['layer2a_temporal'] = temporal_result
        
        print(f"  ✓ Temporal score: {temporal_result.get('score', 0):.2f}")
        print(f"  ✓ Identity shifts: {temporal_result.get('identity_shifts', 0)}")
        print(f"  ✓ Motion smoothness: {temporal_result.get('motion_smoothness', 0):.2f}")
        
        # =====================================================
        # LAYER 2A: VISUAL STREAM - 3D Video Model
        # =====================================================
        print("\nLAYER 2A (Option 2): 3D Video Model Analysis...")
        video_3d_result = analyze_with_3d_model(video_path, clip_duration=2.0)
        results['layer2a_3d_video'] = video_3d_result
        
        print(f"  ✓ 3D Model score: {video_3d_result.get('score', 0):.2f}")
        print(f"  ✓ Method: {video_3d_result.get('method', 'unknown')}")
        
        # =====================================================
        # LAYER 2B: AUDIO STREAM
        # =====================================================
        if has_audio:
            print("\nLAYER 2B: Audio Analysis...")
            audio_result = analyze_audio_stream(video_path)
            results['layer2b_audio'] = audio_result
            
            print(f"  ✓ Audio score: {audio_result.get('score', 0):.2f}")
            print(f"  ✓ Voice deepfake: {audio_result.get('voice_deepfake_score', 0):.2f}")
            print(f"  ✓ Lip-sync: {audio_result.get('lip_sync_score', 0):.2f}")
        else:
            print("\nLAYER 2B: No audio detected, skipping audio analysis")
            results['layer2b_audio'] = {'has_audio': False, 'score': 0.0}
        
        # =====================================================
        # LAYER 2C: PHYSIOLOGICAL SIGNALS
        # =====================================================
        print("\nLAYER 2C: Physiological Signal Analysis...")
        
        fps = metadata_result.get('metadata', {}).get('fps', 30)
        physio_result = analyze_physiological_signals(frame_paths, fps=fps)
        results['layer2c_physiological'] = physio_result
        
        print(f"  ✓ Physiological score: {physio_result.get('score', 0):.2f}")
        print(f"  ✓ Heartbeat detected: {physio_result.get('heartbeat_detected', False)}")
        print(f"  ✓ Natural blink pattern: {physio_result.get('blink_pattern_natural', False)}")
        
        # =====================================================
        # LAYER 2D: PHYSICS & CONSISTENCY
        # =====================================================
        print("\nLAYER 2D: Physics Consistency Analysis...")
        physics_result = analyze_physics_consistency(frame_paths)
        results['layer2d_physics'] = physics_result
        
        print(f"  ✓ Physics score: {physics_result.get('score', 0):.2f}")
        print(f"  ✓ Lighting consistent: {physics_result.get('lighting_consistent', False)}")
        
        # =====================================================
        # INTELLIGENT SCORE FUSION
        # =====================================================
        print(f"\n{'='*60}")
        print("SCORE FUSION")
        print(f"{'='*60}\n")
        
        final_score, confidence, breakdown = intelligent_fusion(results)
        
        results['final_score'] = final_score
        results['confidence'] = confidence
        results['method_breakdown'] = breakdown
        results['risk_level'] = determine_risk_level(final_score)
        
        print(f"  FINAL SCORE: {final_score:.2f}")
        print(f"  CONFIDENCE: {confidence:.2f}")
        print(f"  RISK LEVEL: {results['risk_level']}")
        
        print(f"\n{'='*60}\n")
        
        return results
        
    except Exception as e:
        print(f"Comprehensive video analysis error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'final_score': 0.5,
            'risk_level': 'Unknown'
        }


def intelligent_fusion(results):
    """
    Intelligent multi-modal score fusion with dynamic weighting
    """
    scores = []
    weights = []
    confidences = []
    breakdown = {}
    
    # Layer 1: Metadata (low weight, but useful)
    metadata = results.get('layer1_metadata')
    if metadata and 'score' in metadata:
        scores.append(metadata['score'])
        weights.append(0.05)
        confidences.append(0.6)
        breakdown['metadata'] = metadata['score']
    
    # Layer 2A: Frame-Based (high weight - your existing strong models)
    frame_based = results.get('layer2a_frame_based')
    if frame_based:
        # Use both average and max (worst frame matters)
        avg_score = (
            frame_based.get('avg_ensemble', 0.5) * 0.6 +
            frame_based.get('avg_face', 0.5) * 0.25 +
            frame_based.get('avg_frequency', 0.5) * 0.15
        )
        max_score = frame_based.get('max_ensemble', 0.5)
        
        # Combine avg and max
        frame_score = (avg_score * 0.7) + (max_score * 0.3)
        
        scores.append(frame_score)
        weights.append(0.30)  # High weight
        confidences.append(0.85)
        breakdown['frame_based'] = frame_score
    
    # Layer 2A: Temporal Consistency (very important for video)
    temporal = results.get('layer2a_temporal')
    if temporal and 'score' in temporal:
        scores.append(temporal['score'])
        weights.append(0.20)  # High weight
        confidences.append(0.75)
        breakdown['temporal'] = temporal['score']
    
    # Layer 2A: 3D Video Model
    video_3d = results.get('layer2a_3d_video')
    if video_3d and 'score' in video_3d:
        model_confidence = video_3d.get('confidence', 0.5)
        scores.append(video_3d['score'])
        weights.append(0.15)
        confidences.append(model_confidence)
        breakdown['3d_video'] = video_3d['score']
    
    # Layer 2B: Audio (if present)
    audio = results.get('layer2b_audio')
    if audio and audio.get('has_audio', False) and 'score' in audio:
        scores.append(audio['score'])
        weights.append(0.15)
        confidences.append(0.70)
        breakdown['audio'] = audio['score']
    
    # Layer 2C: Physiological (hard to fake - high weight when detected)
    physio = results.get('layer2c_physiological')
    if physio and 'score' in physio:
        # Higher weight if no heartbeat detected
        physio_weight = 0.20 if not physio.get('heartbeat_detected', True) else 0.10
        scores.append(physio['score'])
        weights.append(physio_weight)
        confidences.append(0.80)
        breakdown['physiological'] = physio['score']
    
    # Layer 2D: Physics
    physics = results.get('layer2d_physics')
    if physics and 'score' in physics:
        scores.append(physics['score'])
        weights.append(0.10)
        confidences.append(0.65)
        breakdown['physics'] = physics['score']
    
    # Normalize weights
    total_weight = sum(weights)
    if total_weight > 0:
        normalized_weights = [w / total_weight for w in weights]
    else:
        return 0.5, 0.0, {}
    
    # Calculate weighted final score
    final_score = sum(s * w for s, w in zip(scores, normalized_weights))
    
    # Calculate overall confidence
    avg_confidence = sum(c * w for c, w in zip(confidences, normalized_weights))
    
    # Boost confidence if methods agree
    if len(scores) >= 3:
        score_variance = np.var(scores)
        if score_variance < 0.05:  # Strong agreement
            avg_confidence = min(avg_confidence * 1.3, 1.0)
        elif score_variance < 0.1:  # Moderate agreement
            avg_confidence = min(avg_confidence * 1.15, 1.0)
    
    return float(final_score), float(avg_confidence), breakdown


def determine_risk_level(score):
    """Determine risk level from score"""
    if score >= 0.65:
        return "High"
    elif score >= 0.40:
        return "Medium"
    else:
        return "Low"
