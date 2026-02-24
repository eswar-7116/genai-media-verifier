import cv2
import numpy as np


def analyze_boundaries(frame_paths, scene_boundaries, timestamps):
    try:
        results = {
            'score': 0.0,
            'boundary_anomalies': 0,
            'quality_drops': 0,
            'suspicious_transitions': [],
            'analyzed_boundaries': 0
        }
        
        if len(frame_paths) < 2:
            return results
        
        boundary_indices = set(scene_boundaries) if scene_boundaries else set()
        
        boundary_indices.update(range(min(5, len(frame_paths))))
        boundary_indices.update(range(max(0, len(frame_paths) - 5), len(frame_paths)))
        
        boundary_indices = sorted(list(boundary_indices))
        
        for idx in boundary_indices:
            if idx >= len(frame_paths) - 1:
                continue
            
            current_frame = cv2.imread(frame_paths[idx])
            next_frame = cv2.imread(frame_paths[idx + 1])
            
            if current_frame is None or next_frame is None:
                continue
            
            results['analyzed_boundaries'] += 1
            
            quality_change = check_quality_drop(current_frame, next_frame)
            if quality_change > 0.3:
                results['quality_drops'] += 1
                results['suspicious_transitions'].append({
                    'frame_index': idx,
                    'timestamp': timestamps[idx] if idx < len(timestamps) else 0,
                    'type': 'quality_drop',
                    'severity': float(quality_change)
                })
            
            color_shift = check_color_shift(current_frame, next_frame)
            if color_shift > 0.35:
                results['boundary_anomalies'] += 1
                results['suspicious_transitions'].append({
                    'frame_index': idx,
                    'timestamp': timestamps[idx] if idx < len(timestamps) else 0,
                    'type': 'color_shift',
                    'severity': float(color_shift)
                })
            
            structural_change = check_structural_change(current_frame, next_frame)
            if structural_change > 0.4:
                results['boundary_anomalies'] += 1
                results['suspicious_transitions'].append({
                    'frame_index': idx,
                    'timestamp': timestamps[idx] if idx < len(timestamps) else 0,
                    'type': 'structural_anomaly',
                    'severity': float(structural_change)
                })
        
        if results['analyzed_boundaries'] > 0:
            anomaly_rate = (results['quality_drops'] + results['boundary_anomalies']) / results['analyzed_boundaries']
            results['score'] = min(anomaly_rate * 2.0, 1.0)
        
        return results
        
    except Exception as e:
        print(f"Boundary analysis error: {e}")
        return {
            'score': 0.0,
            'error': str(e)
        }


def check_quality_drop(frame1, frame2):
    try:
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        sharp1 = cv2.Laplacian(gray1, cv2.CV_64F).var()
        sharp2 = cv2.Laplacian(gray2, cv2.CV_64F).var()
        
        sharp1 = max(sharp1, 1.0)
        sharp2 = max(sharp2, 1.0)
        
        quality_change = abs(sharp1 - sharp2) / max(sharp1, sharp2)
        
        return quality_change
        
    except Exception as e:
        return 0.0


def check_color_shift(frame1, frame2):
    try:
        lab1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2LAB)
        lab2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2LAB)
        
        mean1 = np.mean(lab1, axis=(0, 1))
        mean2 = np.mean(lab2, axis=(0, 1))
        
        color_diff = np.linalg.norm(mean1 - mean2) / 100.0
        
        return float(color_diff)
        
    except Exception as e:
        return 0.0


def check_structural_change(frame1, frame2):
    try:
        small1 = cv2.resize(frame1, (128, 128))
        small2 = cv2.resize(frame2, (128, 128))
        
        gray1 = cv2.cvtColor(small1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(small2, cv2.COLOR_BGR2GRAY)
        
        diff = cv2.absdiff(gray1, gray2)
        
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        change_ratio = np.sum(thresh > 0) / thresh.size
        
        return float(change_ratio)
        
    except Exception as e:
        return 0.0


def get_boundary_weighted_scores(frame_scores, boundary_indices, weight_multiplier=2.0):
    if not frame_scores:
        return 0.5
    
    weighted_scores = []
    weights = []
    
    boundary_set = set(boundary_indices) if boundary_indices else set()
    
    for idx, score in enumerate(frame_scores):
        if idx in boundary_set:
            weights.append(weight_multiplier)
        else:
            weights.append(1.0)
        
        weighted_scores.append(score)
    
    total_weight = sum(weights)
    if total_weight == 0:
        return np.mean(frame_scores)
    
    weighted_avg = sum(s * w for s, w in zip(weighted_scores, weights)) / total_weight
    
    return float(weighted_avg)
