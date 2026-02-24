import os
from PIL import Image
import numpy as np
from models.progress_tracker import get_progress_tracker

from models.video.metadata_analyzer import analyze_video_metadata
from models.video.frame_extractor import smart_frame_extraction

from models.ensemble_detector import predict_ensemble
from models.face_analyzer import analyze_face
from models.frequency_analyzer import analyze_frequency_domain
from models.video.temporal_analyzer import analyze_temporal_consistency
from models.video.video_3d_model import analyze_with_3d_model

from models.video.audio_analyzer import analyze_audio_stream


def convert_numpy_types(obj):
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


def analyze_video_quick(video_path, output_dir="temp_frames"):
    tracker = get_progress_tracker()
    
    try:
        print(f"\n{'='*60}")
        print(f"QUICK VIDEO DEEPFAKE DETECTION")
        print(f"{'='*60}\n")
        tracker.update("Starting quick video analysis...")
        tracker.update(f"Video: {os.path.basename(video_path)}")
        
        results = {
            'layer1_metadata': None,
            'layer2a_frame_based': None,
            'layer2a_3d_video': None,
            'layer2a_temporal': None,
            'layer2b_audio': None,
            'final_score': 0.0,
            'risk_level': 'Unknown',
            'confidence': 0.0,
            'method_breakdown': {}
        }
        
        print("LAYER 1: Metadata Analysis...")
        tracker.update("LAYER 1: Analyzing metadata...")
        metadata_result = analyze_video_metadata(video_path)
        results['layer1_metadata'] = metadata_result
        
        has_audio = metadata_result.get('has_audio', False)
        print(f"LAYER 1: Metadata Analysis")
        print(f"  Score: {metadata_result.get('score', 0):.2f}")
        print(f"  Audio: {has_audio}")
        tracker.update(f"Metadata score: {metadata_result.get('score', 0):.2f}")
        
        print(f"\nLAYER 2A: Smart Frame Extraction")
        tracker.update("LAYER 2A: Extracting key frames...")
        frame_data = smart_frame_extraction(video_path, output_dir, target_frames=50)
        
        if not frame_data or len(frame_data['frames']) == 0:
            tracker.update("Failed to extract frames")
            return {
                'error': 'Failed to extract frames',
                'final_score': 0.5
            }
        
        frame_paths = frame_data['frames']
        timestamps = frame_data['timestamps']
        print(f"  Extracted {len(frame_paths)} frames")
        print(f"  Faces: {len(frame_data.get('face_frames', []))}")
        tracker.update(f"Extracted {len(frame_paths)} frames")
        
        print(f"\nLAYER 2A: Frame-Based Analysis")
        tracker.update("Analyzing frames with AI models...")
        
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
                
                ensemble_result = predict_ensemble(img, silent=True)
                frame_results['ensemble_scores'].append(ensemble_result.get('score', 0.5))
                
                face_result = analyze_face(img)
                if face_result.get('face_detected', False):
                    frame_results['face_scores'].append(face_result.get('score', 0.5))
                
                freq_result = analyze_frequency_domain(img)
                frame_results['frequency_scores'].append(freq_result.get('score', 0.5))
                
                if (idx + 1) % 10 == 0:
                    print(f"  Processed {idx + 1}/{len(frame_paths)} frames")
                    tracker.update(f"Processed {idx + 1}/{len(frame_paths)} frames")
                    
            except Exception:
                continue
        
        if frame_results['ensemble_scores']:
            frame_results['avg_ensemble'] = np.mean(frame_results['ensemble_scores'])
            frame_results['max_ensemble'] = np.max(frame_results['ensemble_scores'])
        
        if frame_results['face_scores']:
            frame_results['avg_face'] = np.mean(frame_results['face_scores'])
        
        if frame_results['frequency_scores']:
            frame_results['avg_frequency'] = np.mean(frame_results['frequency_scores'])
        
        results['layer2a_frame_based'] = frame_results
        
        print(f"  Avg: {frame_results['avg_ensemble']:.2f}, Max: {frame_results.get('max_ensemble', 0):.2f}")
        tracker.update(f"Average score: {frame_results['avg_ensemble']:.2f}")
        tracker.update(f"Highest frame score: {frame_results.get('max_ensemble', 0):.2f}")
        
        print(f"\nLAYER 2A: Temporal Consistency")
        tracker.update("Temporal: Analyzing consistency...")
        temporal_result = analyze_temporal_consistency(frame_paths, timestamps)
        results['layer2a_temporal'] = temporal_result
        
        print(f"  Score: {temporal_result.get('score', 0):.2f}")
        print(f"  Identity shifts: {temporal_result.get('identity_shifts', 0)}")
        tracker.update(f"Temporal: Score {temporal_result.get('score', 0):.2f}")
        
        print(f"\nLAYER 2A: 3D Video Model")
        tracker.update("3D Model: Running video analysis...")
        video_3d_result = analyze_with_3d_model(video_path, clip_duration=2.0)
        results['layer2a_3d_video'] = video_3d_result
        
        print(f"  Score: {video_3d_result.get('score', 0):.2f}")
        tracker.update(f"3D Model: Score {video_3d_result.get('score', 0):.2f}")
        
        if has_audio:
            print(f"\nLAYER 2B: Audio Analysis")
            tracker.update("LAYER 2B: Analyzing audio...")
            audio_result = analyze_audio_stream(video_path)
            results['layer2b_audio'] = audio_result
            
            print(f"  Score: {audio_result.get('score', 0):.2f}")
            tracker.update(f"Audio: Score {audio_result.get('score', 0):.2f}")
        else:
            print(f"\nLAYER 2B: No audio")
            tracker.update("LAYER 2B: No audio detected")
            results['layer2b_audio'] = {'has_audio': False, 'score': 0.0}
        
        print(f"\nFINAL FUSION (Quick Mode)")
        tracker.update("Combining quick analysis results...")
        
        final_score, confidence, breakdown = quick_fusion(results)
        
        results['final_score'] = final_score
        results['confidence'] = confidence
        results['method_breakdown'] = breakdown
        results['risk_level'] = determine_risk_level(final_score)
        
        print(f"  FINAL: {final_score:.2f} | {results['risk_level']} | Confidence: {confidence:.2f}")
        print(f"  NOTE: Quick analysis - some layers skipped")
        print(f"{'='*60}\n")
        tracker.update("Quick analysis complete!")
        tracker.update(f"Final Score: {final_score:.2f}")
        
        results = convert_numpy_types(results)
        
        return results
        
    except Exception as e:
        tracker = get_progress_tracker()
        tracker.update(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'final_score': 0.5,
            'risk_level': 'Unknown'
        }


def quick_fusion(results):
    scores = []
    weights = []
    confidences = []
    breakdown = {}
    
    metadata = results.get('layer1_metadata')
    if metadata and 'score' in metadata:
        scores.append(metadata['score'])
        weights.append(0.10)
        confidences.append(0.6)
        breakdown['metadata'] = metadata['score']
    
    frame_based = results.get('layer2a_frame_based')
    if frame_based:
        avg_score = (
            frame_based.get('avg_ensemble', 0.5) * 0.5 +
            frame_based.get('avg_face', 0.5) * 0.25 +
            frame_based.get('avg_frequency', 0.5) * 0.25
        )
        max_score = frame_based.get('max_ensemble', 0.5)
        
        frame_score = (avg_score * 0.4) + (max_score * 0.6)
        
        scores.append(frame_score)
        weights.append(0.40)
        confidences.append(0.85)
        breakdown['frame_based'] = frame_score
    
    temporal = results.get('layer2a_temporal')
    if temporal and 'score' in temporal:
        temp_score = temporal['score']
        
        if temporal.get('identity_shifts', 0) > 10:
            temp_score = min(temp_score * 1.5, 1.0)
        
        scores.append(temp_score)
        weights.append(0.25)
        confidences.append(0.75)
        breakdown['temporal'] = temp_score
    
    video_3d = results.get('layer2a_3d_video')
    if video_3d and 'score' in video_3d:
        model_confidence = video_3d.get('confidence', 0.5)
        scores.append(video_3d['score'])
        weights.append(0.10)
        confidences.append(model_confidence)
        breakdown['3d_video'] = video_3d['score']
    
    audio = results.get('layer2b_audio')
    if audio and audio.get('has_audio', False) and 'score' in audio:
        scores.append(audio['score'])
        weights.append(0.15)
        confidences.append(0.70)
        breakdown['audio'] = audio['score']
    
    total_weight = sum(weights)
    if total_weight > 0:
        normalized_weights = [w / total_weight for w in weights]
    else:
        return 0.5, 0.0, {}
    
    final_score = sum(s * w for s, w in zip(scores, normalized_weights))
    
    avg_confidence = sum(c * w for c, w in zip(confidences, normalized_weights))
    
    avg_confidence = avg_confidence * 0.8
    
    breakdown = convert_numpy_types(breakdown)
    
    return float(final_score), float(avg_confidence), breakdown


def determine_risk_level(score):
    if score >= 0.65:
        return "High"
    elif score >= 0.40:
        return "Medium"
    else:
        return "Low"
