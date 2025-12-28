"""
Smart Frame Extractor - LAYER 2A
Intelligently extracts frames from video based on:
- Scene changes
- Face presence
- Video boundaries (first/last frames)
- Motion intensity
"""
import cv2
import numpy as np
import os
from scenedetect import detect, ContentDetector, AdaptiveDetector


def smart_frame_extraction(video_path, output_dir="temp_frames", target_frames=50):
    """
    Extract frames intelligently from video
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        target_frames: Target number of frames to extract
    
    Returns:
        dict: {
            'frames': list of frame paths,
            'timestamps': list of timestamps,
            'scene_boundaries': list of scene change timestamps,
            'face_frames': list of frames with faces
        }
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Clear previous frames
        for f in os.listdir(output_dir):
            if f.endswith('.jpg'):
                os.remove(os.path.join(output_dir, f))
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        cap.release()
        
        # Strategy for frame extraction
        frame_indices = set()
        
        # 1. Scene boundaries (high priority)
        scene_frames = detect_scene_changes(video_path, fps, total_frames)
        frame_indices.update(scene_frames)
        
        # 2. First and last 10 frames (boundaries often show artifacts)
        boundary_frames = list(range(0, min(10, total_frames)))
        boundary_frames.extend(range(max(0, total_frames - 10), total_frames))
        frame_indices.update(boundary_frames)
        
        # 3. Regular sampling to fill remaining slots
        current_count = len(frame_indices)
        if current_count < target_frames:
            remaining = target_frames - current_count
            step = max(1, total_frames // remaining)
            regular_samples = list(range(0, total_frames, step))[:remaining]
            frame_indices.update(regular_samples)
        
        # Sort frame indices
        frame_indices = sorted(list(frame_indices))[:target_frames]
        
        # Extract frames
        extracted_frames = []
        timestamps = []
        
        cap = cv2.VideoCapture(video_path)
        
        for idx, frame_idx in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                frame_path = os.path.join(output_dir, f"frame_{idx:04d}.jpg")
                cv2.imwrite(frame_path, frame)
                extracted_frames.append(frame_path)
                timestamps.append(frame_idx / fps if fps > 0 else frame_idx)
        
        cap.release()
        
        # Detect which frames have faces
        face_frames = detect_face_frames(extracted_frames)
        
        return {
            'frames': extracted_frames,
            'timestamps': timestamps,
            'scene_boundaries': [idx for idx in scene_frames if idx in frame_indices],
            'face_frames': face_frames,
            'total_extracted': len(extracted_frames)
        }
        
    except Exception as e:
        print(f"Smart frame extraction error: {e}")
        # Fallback to simple extraction
        return simple_frame_extraction(video_path, output_dir, target_frames)


def detect_scene_changes(video_path, fps, total_frames, threshold=27.0):
    """Detect scene changes using PySceneDetect"""
    try:
        # Use PySceneDetect
        scene_list = detect(video_path, ContentDetector(threshold=threshold))
        
        # Convert to frame indices
        scene_frames = []
        for scene in scene_list:
            # Get frame number of scene start
            start_frame = int(scene[0].get_frames())
            scene_frames.append(start_frame)
        
        return scene_frames
        
    except Exception as e:
        print(f"Scene detection error: {e}, using fallback")
        # Fallback: simple motion-based detection
        return detect_scene_changes_fallback(video_path, fps, total_frames)


def detect_scene_changes_fallback(video_path, fps, total_frames):
    """Fallback scene detection using frame differences"""
    try:
        cap = cv2.VideoCapture(video_path)
        scene_frames = []
        
        prev_frame = None
        frame_idx = 0
        sample_rate = max(1, int(fps))  # Sample at 1 fps
        
        while frame_idx < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 240))
            
            if prev_frame is not None:
                diff = cv2.absdiff(prev_frame, gray)
                mean_diff = np.mean(diff)
                
                # If large difference, likely scene change
                if mean_diff > 30:
                    scene_frames.append(frame_idx)
            
            prev_frame = gray
            frame_idx += sample_rate
        
        cap.release()
        return scene_frames
        
    except Exception as e:
        print(f"Fallback scene detection error: {e}")
        return []


def detect_face_frames(frame_paths):
    """Detect which frames contain faces"""
    try:
        import mediapipe as mp
        
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )
        
        face_frames = []
        
        for frame_path in frame_paths:
            image = cv2.imread(frame_path)
            if image is None:
                continue
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.detect(rgb_image)
            
            if results.detections:
                face_frames.append(frame_path)
        
        face_detection.close()
        return face_frames
        
    except Exception as e:
        print(f"Face detection in frames error: {e}")
        # Fallback: use OpenCV Haar Cascade
        return detect_face_frames_opencv(frame_paths)


def detect_face_frames_opencv(frame_paths):
    """Fallback face detection using OpenCV"""
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        face_frames = []
        
        for frame_path in frame_paths:
            image = cv2.imread(frame_path)
            if image is None:
                continue
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
            
            if len(faces) > 0:
                face_frames.append(frame_path)
        
        return face_frames
        
    except Exception as e:
        print(f"OpenCV face detection error: {e}")
        return []


def simple_frame_extraction(video_path, output_dir, target_frames):
    """Simple fallback frame extraction"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        step = max(1, total_frames // target_frames)
        
        extracted_frames = []
        timestamps = []
        frame_idx = 0
        count = 0
        
        while count < target_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_path = os.path.join(output_dir, f"frame_{count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            extracted_frames.append(frame_path)
            timestamps.append(frame_idx / fps if fps > 0 else frame_idx)
            
            frame_idx += step
            count += 1
        
        cap.release()
        
        return {
            'frames': extracted_frames,
            'timestamps': timestamps,
            'scene_boundaries': [],
            'face_frames': [],
            'total_extracted': len(extracted_frames)
        }
        
    except Exception as e:
        print(f"Simple frame extraction error: {e}")
        return None
