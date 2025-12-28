"""
Comprehensive Video Deepfake Detector - HYBRID APPROACH
Combines all Layer 1 and Layer 2 analyses
"""
import os
from PIL import Image
import numpy as np


def convert_numpy_types(obj):
    """
    Recursively convert numpy types to Python native types for JSON serialization
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

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

# Layer 3 - Specialized
from models.video.boundary_analyzer import analyze_boundaries, get_boundary_weighted_scores
from models.video.compression_analyzer import analyze_region_compression


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
            'layer3_boundary': None,
            'layer3_compression': None,
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
        # LAYER 3: SPECIALIZED DETECTION METHODS
        # =====================================================
        
        # 3A: Enhanced Boundary Analysis
        print("\nLAYER 3: Boundary/Transition Analysis...")
        scene_boundaries = frame_data.get('scene_boundaries', [])
        boundary_result = analyze_boundaries(frame_paths, scene_boundaries, timestamps)
        results['layer3_boundary'] = boundary_result
        
        print(f"  ✓ Boundary score: {boundary_result.get('score', 0):.2f}")
        print(f"  ✓ Suspicious transitions: {len(boundary_result.get('suspicious_transitions', []))}")
        print(f"  ✓ Quality drops detected: {boundary_result.get('quality_drops', 0)}")
        
        # Apply boundary weighting to frame scores
        if frame_results['ensemble_scores'] and scene_boundaries:
            weighted_ensemble = get_boundary_weighted_scores(
                frame_results['ensemble_scores'],
                scene_boundaries,
                weight_multiplier=2.0
            )
            frame_results['weighted_ensemble'] = weighted_ensemble
            print(f"  ✓ Boundary-weighted ensemble: {weighted_ensemble:.2f}")
        
        # 3B: Per-Region Compression Analysis
        print("\nLAYER 3: Per-Region Compression Analysis...")
        compression_result = analyze_region_compression(frame_paths)
        results['layer3_compression'] = compression_result
        
        print(f"  ✓ Compression score: {compression_result.get('score', 0):.2f}")
        print(f"  ✓ Compression mismatches: {compression_result.get('compression_mismatches', 0)}")
        if compression_result.get('avg_face_compression', 0) > 0:
            print(f"  ✓ Face compression: {compression_result.get('avg_face_compression', 0):.2f}")
            print(f"  ✓ Background compression: {compression_result.get('avg_background_compression', 0):.2f}")
        
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
        
        # Convert all numpy types to Python native types for JSON serialization
        results = convert_numpy_types(results)
        
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
    AGGRESSIVE MODE: Catches obvious fakes
    """
    scores = []
    weights = []
    confidences = []
    breakdown = {}
    
    # =====================================================
    # CRITICAL OVERRIDE RULES (CHECK FIRST)
    # =====================================================
    
    frame_based = results.get('layer2a_frame_based')
    temporal = results.get('layer2a_temporal')
    physio = results.get('layer2c_physiological')
    
    # RULE 1: If ANY frame is >95% fake → AUTO HIGH RISK
    if frame_based and frame_based.get('max_ensemble', 0) > 0.95:
        return 0.95, 0.99, {'override': 'single_frame_very_fake', 'max_frame': frame_based['max_ensemble']}
    
    # RULE 2: No heartbeat + high identity shifts → AUTO HIGH RISK
    if physio and not physio.get('heartbeat_detected', True):
        identity_shifts = temporal.get('identity_shifts', 0) if temporal else 0
        if identity_shifts > 20:
            return 0.90, 0.98, {'override': 'no_heartbeat_identity_shifts', 'shifts': identity_shifts}
    
    # RULE 3: Max frame >0.90 + temporal issues → HIGH RISK
    if frame_based and temporal:
        max_frame = frame_based.get('max_ensemble', 0)
        if max_frame > 0.90 and temporal.get('score', 0) > 0.5:
            combined_score = (max_frame * 0.6) + (temporal['score'] * 0.4)
            return combined_score, 0.97, {'override': 'frame_temporal_combo', 'max_frame': max_frame}
    
    # =====================================================
    # NORMAL FUSION (if no overrides triggered)
    # =====================================================
    
    # Layer 1: Metadata
    metadata = results.get('layer1_metadata')
    if metadata and 'score' in metadata:
        scores.append(metadata['score'])
        weights.append(0.05)
        confidences.append(0.6)
        breakdown['metadata'] = metadata['score']
    
    # Layer 2A: Frame-Based - USE MAX FRAME HEAVILY
    if frame_based:
        avg_score = (
            frame_based.get('avg_ensemble', 0.5) * 0.5 +
            frame_based.get('avg_face', 0.5) * 0.25 +
            frame_based.get('avg_frequency', 0.5) * 0.25
        )
        max_score = frame_based.get('max_ensemble', 0.5)
        
        # AGGRESSIVE: Weight max frame heavily (60%)
        frame_score = (avg_score * 0.4) + (max_score * 0.6)
        
        scores.append(frame_score)
        weights.append(0.35)  # Increased weight
        confidences.append(0.90)  # High confidence
        breakdown['frame_based'] = frame_score
    
    # Layer 2A: Temporal Consistency
    if temporal and 'score' in temporal:
        temp_score = temporal['score']
        
        # BOOST if identity shifts detected
        if temporal.get('identity_shifts', 0) > 10:
            temp_score = min(temp_score * 1.5, 1.0)
        
        scores.append(temp_score)
        weights.append(0.20)
        confidences.append(0.80)
        breakdown['temporal'] = temp_score
    
    # Layer 2A: 3D Video Model
    video_3d = results.get('layer2a_3d_video')
    if video_3d and 'score' in video_3d:
        model_confidence = video_3d.get('confidence', 0.5)
        scores.append(video_3d['score'])
        weights.append(0.10)  # Lower weight (not specifically trained)
        confidences.append(model_confidence)
        breakdown['3d_video'] = video_3d['score']
    
    # Layer 2B: Audio
    audio = results.get('layer2b_audio')
    if audio and audio.get('has_audio', False) and 'score' in audio:
        scores.append(audio['score'])
        weights.append(0.15)
        confidences.append(0.70)
        breakdown['audio'] = audio['score']
    
    # Layer 2C: Physiological - CRITICAL SIGNAL
    if physio and 'score' in physio:
        physio_score = physio['score']
        
        # AGGRESSIVE: No heartbeat = HUGE penalty
        if not physio.get('heartbeat_detected', True):
            physio_score = min(physio_score * 2.0, 1.0)
            physio_weight = 0.25  # Massive weight
        else:
            physio_weight = 0.10
        
        scores.append(physio_score)
        weights.append(physio_weight)
        confidences.append(0.85)
        breakdown['physiological'] = physio_score
    
    # Layer 2D: Physics
    physics = results.get('layer2d_physics')
    if physics and 'score' in physics:
        scores.append(physics['score'])
        weights.append(0.08)
        confidences.append(0.65)
        breakdown['physics'] = physics['score']
    
    # Layer 3: Boundary Analysis
    boundary = results.get('layer3_boundary')
    if boundary and 'score' in boundary:
        # Use boundary-weighted ensemble if available
        if frame_based and frame_based.get('weighted_ensemble'):
            weighted_score = frame_based['weighted_ensemble']
            # Boost frame_based score if boundaries are suspicious
            if 'frame_based' in breakdown and boundary['score'] > 0.4:
                idx = list(breakdown.keys()).index('frame_based')
                scores[idx] = (scores[idx] * 0.7) + (weighted_score * 0.3)
        
        scores.append(boundary['score'])
        weights.append(0.08)
        confidences.append(0.70)
        breakdown['boundary'] = boundary['score']
    
    # Layer 3: Compression Analysis
    compression = results.get('layer3_compression')
    if compression and 'score' in compression:
        comp_score = compression['score']
        
        # BOOST if compression mismatches found (face-swap indicator)
        if compression.get('compression_mismatches', 0) > 0:
            comp_score = min(comp_score * 2.0, 1.0)
            comp_weight = 0.15  # Higher weight
        else:
            comp_weight = 0.08
        
        scores.append(comp_score)
        weights.append(comp_weight)
        confidences.append(0.75)
        breakdown['compression'] = comp_score
    
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
    
    # AGGRESSIVE BOOST: If multiple methods show high scores
    high_score_count = sum(1 for s in scores if s > 0.6)
    if high_score_count >= 3:
        final_score = min(final_score * 1.2, 1.0)
    
    # Convert breakdown to ensure all values are Python native types
    breakdown = convert_numpy_types(breakdown)
    
    return float(final_score), float(avg_confidence), breakdown


def determine_risk_level(score):
    """Determine risk level from score"""
    if score >= 0.65:
        return "High"
    elif score >= 0.40:
        return "Medium"
    else:
        return "Low"
