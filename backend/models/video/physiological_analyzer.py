"""
Physiological Signal Analyzer - LAYER 2C
Analyzes biological signals that are hard to fake:
- Heart rate (PPG/rPPG)
- Blink patterns
- Eye movements
- Breathing patterns
"""
import cv2
import numpy as np
from scipy import signal, fftpack
from PIL import Image


def analyze_physiological_signals(frame_paths, fps=30):
    """
    Analyze physiological signals from video frames
    
    Args:
        frame_paths: List of frame paths
        fps: Frame rate of video
    
    Returns:
        dict: {
            'score': float (0-1, higher = more suspicious),
            'heartbeat_detected': bool,
            'blink_pattern_natural': bool,
            'breathing_detected': bool
        }
    """
    try:
        results = {
            'score': 0.0,
            'heartbeat_detected': False,
            'blink_pattern_natural': False,
            'breathing_detected': False,
            'anomalies': []
        }
        
        # 1. rPPG Heartbeat Detection
        heartbeat_result = detect_heartbeat_rppg(frame_paths, fps)
        results['heartbeat_detected'] = heartbeat_result['detected']
        results['heartbeat_bpm'] = heartbeat_result.get('bpm', 0)
        
        if not heartbeat_result['detected']:
            results['anomalies'].append('No heartbeat detected')
            results['score'] += 0.4
        elif heartbeat_result.get('irregular', False):
            results['anomalies'].append('Irregular heartbeat pattern')
            results['score'] += 0.25
        
        # 2. Blink Pattern Analysis
        blink_result = analyze_blink_pattern(frame_paths, fps)
        results['blink_pattern_natural'] = blink_result['natural']
        results['blink_count'] = blink_result.get('count', 0)
        
        if not blink_result['natural']:
            results['anomalies'].append('Unnatural blink pattern')
            results['score'] += 0.3
        
        # 3. Breathing Detection (if torso visible)
        breathing_result = detect_breathing(frame_paths)
        results['breathing_detected'] = breathing_result['detected']
        
        if not breathing_result['detected'] and len(frame_paths) > 30:
            # Only penalize if enough frames and no breathing
            results['anomalies'].append('No breathing motion detected')
            results['score'] += 0.2
        
        results['score'] = min(results['score'], 1.0)
        
        return results
        
    except Exception as e:
        print(f"Physiological signal analysis error: {e}")
        return {
            'score': 0.5,
            'error': str(e)
        }


def detect_heartbeat_rppg(frame_paths, fps):
    """
    Detect heartbeat using remote PPG (photoplethysmography)
    Analyzes subtle color changes in face due to blood flow
    """
    try:
        # Extract facial ROI from frames
        face_regions = extract_face_regions(frame_paths)
        
        if len(face_regions) < 30:  # Need at least ~1 second
            return {'detected': False, 'reason': 'Insufficient frames with faces'}
        
        # Extract color signal (focus on green channel - best for PPG)
        green_signals = []
        
        for face_roi in face_regions:
            if face_roi is not None:
                # Average green channel value
                green_avg = np.mean(face_roi[:, :, 1])
                green_signals.append(green_avg)
        
        if len(green_signals) < 30:
            return {'detected': False, 'reason': 'Insufficient face data'}
        
        # Detrend signal
        green_signals = np.array(green_signals)
        green_signals = signal.detrend(green_signals)
        
        # Apply bandpass filter (0.7-4 Hz = 42-240 BPM)
        nyquist = fps / 2
        low = 0.7 / nyquist
        high = 4.0 / nyquist
        
        if low >= 1.0 or high >= 1.0:
            return {'detected': False, 'reason': 'Invalid frequency range'}
        
        b, a = signal.butter(3, [low, high], btype='band')
        filtered_signal = signal.filtfilt(b, a, green_signals)
        
        # FFT to find dominant frequency
        fft_result = np.fft.fft(filtered_signal)
        frequencies = np.fft.fftfreq(len(filtered_signal), 1/fps)
        
        # Get positive frequencies only
        positive_freqs = frequencies[:len(frequencies)//2]
        positive_fft = np.abs(fft_result[:len(fft_result)//2])
        
        # Find peak in valid heart rate range
        valid_range = (positive_freqs >= 0.7) & (positive_freqs <= 4.0)
        
        if not np.any(valid_range):
            return {'detected': False, 'reason': 'No valid frequency range'}
        
        valid_fft = positive_fft[valid_range]
        valid_freqs = positive_freqs[valid_range]
        
        if len(valid_fft) == 0:
            return {'detected': False, 'reason': 'No valid frequencies'}
        
        peak_idx = np.argmax(valid_fft)
        peak_freq = valid_freqs[peak_idx]
        peak_power = valid_fft[peak_idx]
        
        # Convert to BPM
        bpm = peak_freq * 60
        
        # Check if peak is strong enough (SNR)
        noise_power = np.median(valid_fft)
        snr = peak_power / (noise_power + 1e-10)
        
        # Typical human heart rate: 60-100 BPM at rest, up to 180 during activity
        detected = (50 < bpm < 200) and (snr > 2.0)
        
        # Check regularity
        irregular = False
        if detected:
            # Check if signal is too noisy (irregular)
            signal_std = np.std(filtered_signal)
            if signal_std > np.mean(np.abs(filtered_signal)) * 2:
                irregular = True
        
        return {
            'detected': detected,
            'bpm': float(bpm) if detected else 0,
            'snr': float(snr),
            'irregular': irregular
        }
        
    except Exception as e:
        print(f"rPPG detection error: {e}")
        return {'detected': False, 'error': str(e)}


def extract_face_regions(frame_paths):
    """Extract facial regions from frames"""
    try:
        import mediapipe as mp
        
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )
        
        face_regions = []
        
        for frame_path in frame_paths:
            image = cv2.imread(frame_path)
            if image is None:
                face_regions.append(None)
                continue
            
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb)
            
            if results.detections:
                detection = results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                
                h, w, _ = image.shape
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Extract face ROI
                face_roi = image[y:y+height, x:x+width]
                face_regions.append(face_roi)
            else:
                face_regions.append(None)
        
        face_detection.close()
        return face_regions
        
    except Exception as e:
        print(f"Face region extraction error: {e}")
        return []


def analyze_blink_pattern(frame_paths, fps):
    """
    Analyze blink patterns
    Natural blinking: 15-20 times per minute, duration 100-400ms
    """
    try:
        import mediapipe as mp
        
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.5
        )
        
        # Track Eye Aspect Ratio (EAR) across frames
        ear_values = []
        
        for frame_path in frame_paths:
            image = cv2.imread(frame_path)
            if image is None:
                continue
            
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                ear = calculate_eye_aspect_ratio(landmarks)
                ear_values.append(ear)
            else:
                ear_values.append(None)
        
        face_mesh.close()
        
        if len([e for e in ear_values if e is not None]) < 10:
            return {'natural': True, 'reason': 'Insufficient data'}
        
        # Detect blinks (EAR drops below threshold)
        blink_threshold = 0.2
        blinks = detect_blinks(ear_values, blink_threshold, fps)
        
        # Check naturalness
        duration = len(frame_paths) / fps
        expected_blinks_min = int(duration / 60 * 10)  # Min 10 per minute
        expected_blinks_max = int(duration / 60 * 30)  # Max 30 per minute
        
        blink_count = len(blinks)
        
        # Check blink duration (should be 100-400ms = 3-12 frames at 30fps)
        natural_durations = []
        for blink in blinks:
            duration_frames = blink['end'] - blink['start']
            duration_ms = (duration_frames / fps) * 1000
            if 50 < duration_ms < 500:
                natural_durations.append(True)
            else:
                natural_durations.append(False)
        
        natural = (expected_blinks_min <= blink_count <= expected_blinks_max) and \
                  (len(natural_durations) == 0 or np.mean(natural_durations) > 0.7)
        
        return {
            'natural': natural,
            'count': blink_count,
            'expected_range': (expected_blinks_min, expected_blinks_max),
            'avg_duration_ms': np.mean([b['duration_ms'] for b in blinks]) if blinks else 0
        }
        
    except Exception as e:
        print(f"Blink pattern analysis error: {e}")
        return {'natural': True, 'error': str(e)}


def calculate_eye_aspect_ratio(face_landmarks):
    """Calculate Eye Aspect Ratio (EAR)"""
    # Left eye landmarks
    left_eye = [33, 160, 158, 133, 153, 144]
    # Right eye landmarks
    right_eye = [362, 385, 387, 263, 373, 380]
    
    def eye_aspect_ratio(eye_points):
        # Vertical distances
        v1 = np.linalg.norm(np.array([face_landmarks.landmark[eye_points[1]].x,
                                      face_landmarks.landmark[eye_points[1]].y]) -
                           np.array([face_landmarks.landmark[eye_points[5]].x,
                                    face_landmarks.landmark[eye_points[5]].y]))
        v2 = np.linalg.norm(np.array([face_landmarks.landmark[eye_points[2]].x,
                                      face_landmarks.landmark[eye_points[2]].y]) -
                           np.array([face_landmarks.landmark[eye_points[4]].x,
                                    face_landmarks.landmark[eye_points[4]].y]))
        # Horizontal distance
        h = np.linalg.norm(np.array([face_landmarks.landmark[eye_points[0]].x,
                                     face_landmarks.landmark[eye_points[0]].y]) -
                          np.array([face_landmarks.landmark[eye_points[3]].x,
                                   face_landmarks.landmark[eye_points[3]].y]))
        
        return (v1 + v2) / (2.0 * h)
    
    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)
    
    return (left_ear + right_ear) / 2.0


def detect_blinks(ear_values, threshold, fps):
    """Detect blinks from EAR sequence"""
    blinks = []
    in_blink = False
    blink_start = 0
    
    for i, ear in enumerate(ear_values):
        if ear is None:
            continue
        
        if ear < threshold and not in_blink:
            in_blink = True
            blink_start = i
        elif ear >= threshold and in_blink:
            in_blink = False
            blink_duration = i - blink_start
            duration_ms = (blink_duration / fps) * 1000
            
            blinks.append({
                'start': blink_start,
                'end': i,
                'duration_frames': blink_duration,
                'duration_ms': duration_ms
            })
    
    return blinks


def detect_breathing(frame_paths):
    """
    Detect breathing motion (chest/shoulder movement)
    """
    try:
        # Simple motion detection in torso region
        prev_frame = None
        motion_values = []
        
        for frame_path in frame_paths:
            frame = cv2.imread(frame_path)
            if frame is None:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Focus on lower 2/3 of frame (torso area)
            h, w = gray.shape
            torso_region = gray[h//3:, :]
            
            if prev_frame is not None:
                # Calculate frame difference in torso region
                diff = cv2.absdiff(prev_frame, torso_region)
                motion = np.mean(diff)
                motion_values.append(motion)
            
            prev_frame = torso_region
        
        if len(motion_values) < 10:
            return {'detected': False, 'reason': 'Insufficient frames'}
        
        # Look for periodic motion (breathing is periodic, 12-20 breaths/min)
        motion_array = np.array(motion_values)
        
        # Check if there's periodic motion
        has_motion = np.std(motion_array) > 2.0
        
        return {
            'detected': has_motion,
            'motion_std': float(np.std(motion_array))
        }
        
    except Exception as e:
        print(f"Breathing detection error: {e}")
        return {'detected': False, 'error': str(e)}
