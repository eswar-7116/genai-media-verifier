"""
Example usage of the comprehensive video deepfake detector
"""
from models.video.comprehensive_detector import analyze_video_comprehensive
import json


def test_video_analysis(video_path):
    """Test the comprehensive video analysis"""
    
    print("Starting comprehensive video deepfake detection...")
    print(f"Video: {video_path}\n")
    
    # Run analysis
    results = analyze_video_comprehensive(video_path)
    
    # Print summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    print(f"\nFinal Score: {results['final_score']:.2f}")
    print(f"Risk Level: {results['risk_level']}")
    print(f"Confidence: {results['confidence']:.2f}")
    
    print("\nMethod Breakdown:")
    for method, score in results.get('method_breakdown', {}).items():
        print(f"  {method}: {score:.2f}")
    
    # Detailed results
    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60)
    
    # Layer 1: Metadata
    if results.get('layer1_metadata'):
        meta = results['layer1_metadata']
        print("\n[LAYER 1] Metadata:")
        print(f"  Score: {meta.get('score', 0):.2f}")
        print(f"  Has Audio: {meta.get('has_audio', False)}")
        if meta.get('suspicious_indicators'):
            print(f"  Indicators: {', '.join(meta['suspicious_indicators'])}")
    
    # Layer 2A: Frame-Based
    if results.get('layer2a_frame_based'):
        frame = results['layer2a_frame_based']
        print("\n[LAYER 2A] Frame-Based:")
        print(f"  Ensemble Avg: {frame.get('avg_ensemble', 0):.2f}")
        print(f"  Ensemble Max: {frame.get('max_ensemble', 0):.2f}")
        print(f"  Face Avg: {frame.get('avg_face', 0):.2f}")
        print(f"  Frequency Avg: {frame.get('avg_frequency', 0):.2f}")
    
    # Layer 2A: Temporal
    if results.get('layer2a_temporal'):
        temp = results['layer2a_temporal']
        print("\n[LAYER 2A] Temporal:")
        print(f"  Score: {temp.get('score', 0):.2f}")
        print(f"  Identity Shifts: {temp.get('identity_shifts', 0)}")
        print(f"  Motion Smoothness: {temp.get('motion_smoothness', 0):.2f}")
        print(f"  Landmark Jitter: {temp.get('landmark_jitter', 0):.2f}")
    
    # Layer 2A: 3D Video
    if results.get('layer2a_3d_video'):
        video3d = results['layer2a_3d_video']
        print("\n[LAYER 2A] 3D Video Model:")
        print(f"  Score: {video3d.get('score', 0):.2f}")
        print(f"  Method: {video3d.get('method', 'unknown')}")
    
    # Layer 2B: Audio
    if results.get('layer2b_audio'):
        audio = results['layer2b_audio']
        if audio.get('has_audio'):
            print("\n[LAYER 2B] Audio:")
            print(f"  Score: {audio.get('score', 0):.2f}")
            print(f"  Voice Deepfake: {audio.get('voice_deepfake_score', 0):.2f}")
            print(f"  Lip Sync: {audio.get('lip_sync_score', 0):.2f}")
            if audio.get('anomalies'):
                print(f"  Anomalies: {', '.join(audio['anomalies'])}")
        else:
            print("\n[LAYER 2B] Audio: Not present")
    
    # Layer 2C: Physiological
    if results.get('layer2c_physiological'):
        physio = results['layer2c_physiological']
        print("\n[LAYER 2C] Physiological:")
        print(f"  Score: {physio.get('score', 0):.2f}")
        print(f"  Heartbeat Detected: {physio.get('heartbeat_detected', False)}")
        if physio.get('heartbeat_bpm'):
            print(f"  Heart Rate: {physio.get('heartbeat_bpm', 0):.0f} BPM")
        print(f"  Natural Blink Pattern: {physio.get('blink_pattern_natural', False)}")
        if physio.get('anomalies'):
            print(f"  Anomalies: {', '.join(physio['anomalies'])}")
    
    # Layer 2D: Physics
    if results.get('layer2d_physics'):
        physics = results['layer2d_physics']
        print("\n[LAYER 2D] Physics:")
        print(f"  Score: {physics.get('score', 0):.2f}")
        print(f"  Lighting Consistent: {physics.get('lighting_consistent', True)}")
        print(f"  Depth Plausible: {physics.get('depth_plausible', True)}")
        if physics.get('anomalies'):
            print(f"  Anomalies: {', '.join(physics['anomalies'])}")
    
    print("\n" + "="*60)
    
    # Save full results to JSON
    output_file = "video_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to: {output_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Default test video
        video_path = "uploads/will smith ai video.mp4"
    
    test_video_analysis(video_path)
