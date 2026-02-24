import torch
import numpy as np
import cv2
from PIL import Image


def analyze_with_3d_model(video_path, clip_duration=2.0):
    try:
        result = analyze_with_videomae(video_path, clip_duration)
        
        if result is not None:
            return result
        
        return analyze_with_temporal_features(video_path, clip_duration)
        
    except Exception as e:
        print(f"3D model analysis error: {e}")
        return {
            'score': 0.5,
            'error': str(e),
            'method': 'error'
        }


def analyze_with_videomae(video_path, clip_duration):
    try:
        from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        processor = VideoMAEImageProcessor.from_pretrained("MCG-NJU/videomae-base")
        model = VideoMAEForVideoClassification.from_pretrained("MCG-NJU/videomae-base")
        model.to(device)
        model.eval()
        
        clips = extract_video_clips(video_path, clip_duration, num_frames=16)
        
        if not clips:
            return None
        
        clip_scores = []
        
        for clip_frames in clips:
            inputs = processor(clip_frames, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                
                probs = torch.softmax(logits, dim=-1)
                entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
                
                anomaly_score = entropy.item() / 5.0
                clip_scores.append(min(anomaly_score, 1.0))
        
        avg_score = np.mean(clip_scores)
        max_score = np.max(clip_scores)
        
        final_score = (avg_score * 0.6) + (max_score * 0.4)
        
        return {
            'score': float(final_score),
            'clip_scores': [float(s) for s in clip_scores],
            'confidence': 0.7,
            'method': 'videomae'
        }
        
    except Exception as e:
        print(f"VideoMAE error: {e}")
        return None


def analyze_with_temporal_features(video_path, clip_duration):
    try:
        clips = extract_video_clips(video_path, clip_duration, num_frames=16)
        
        if not clips:
            return {
                'score': 0.5,
                'method': 'fallback',
                'error': 'No clips extracted'
            }
        
        clip_scores = []
        
        for clip_frames in clips:
            clip_array = np.stack([np.array(f.resize((224, 224))) for f in clip_frames])
            clip_array = clip_array.astype(np.float32) / 255.0
            
            diffs = np.diff(clip_array, axis=0)
            temporal_variance = np.var(diffs)
            
            motion = np.mean(np.abs(diffs))
            
            color_var = np.var(clip_array, axis=0).mean()
            
            anomaly_score = 0.0
            
            if temporal_variance > 0.05:
                anomaly_score += 0.3
            
            if motion < 0.01:
                anomaly_score += 0.3
            
            if color_var > 0.15:
                anomaly_score += 0.4
            
            clip_scores.append(min(anomaly_score, 1.0))
        
        avg_score = np.mean(clip_scores)
        
        return {
            'score': float(avg_score),
            'clip_scores': [float(s) for s in clip_scores],
            'confidence': 0.5,
            'method': 'temporal_features'
        }
        
    except Exception as e:
        print(f"Temporal features error: {e}")
        return {
            'score': 0.5,
            'error': str(e),
            'method': 'error'
        }


def extract_video_clips(video_path, clip_duration, num_frames=16):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps <= 0 or total_frames <= 0:
            cap.release()
            return []
        
        frames_per_clip = int(fps * clip_duration)
        
        clip_step = max(1, frames_per_clip // num_frames)
        
        clips = []
        current_frame = 0
        
        while current_frame + frames_per_clip < total_frames:
            clip_frames = []
            
            for i in range(num_frames):
                frame_idx = current_frame + (i * clip_step)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    clip_frames.append(pil_image)
            
            if len(clip_frames) == num_frames:
                clips.append(clip_frames)
            
            current_frame += frames_per_clip
            
            if len(clips) >= 10:
                break
        
        cap.release()
        
        return clips
        
    except Exception as e:
        print(f"Clip extraction error: {e}")
        return []
