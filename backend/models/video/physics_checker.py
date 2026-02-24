import cv2
import numpy as np
import torch
from PIL import Image
import os


_midas_model = None
_midas_transform = None
_midas_device = None


def get_midas_model():
    global _midas_model, _midas_transform, _midas_device
    
    if _midas_model is None:
        try:
            print("Loading MiDaS model (one-time initialization)...")
            _midas_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            
            _midas_model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small", verbose=False)
            _midas_model.to(_midas_device)
            _midas_model.eval()
            
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", verbose=False)
            _midas_transform = midas_transforms.small_transform
            
            print(f"MiDaS model loaded on {_midas_device}")
        except Exception as e:
            print(f"Failed to load MiDaS model: {e}")
            return None, None, None
    
    return _midas_model, _midas_transform, _midas_device


def analyze_physics_consistency(frame_paths):
    try:
        results = {
            'score': 0.0,
            'lighting_consistent': True,
            'depth_plausible': True,
            'reflection_consistent': True,
            'anomalies': []
        }
        
        lighting_result = analyze_lighting_consistency(frame_paths)
        results['lighting_consistent'] = lighting_result['consistent']
        
        if not lighting_result['consistent']:
            results['anomalies'].append('Inconsistent lighting detected')
            results['score'] += 0.4
        
        depth_result = analyze_depth_consistency(frame_paths)
        results['depth_plausible'] = depth_result['plausible']
        
        if not depth_result['plausible']:
            results['anomalies'].append('Implausible depth map')
            results['score'] += 0.3
        
        shadow_result = analyze_shadows(frame_paths)
        
        if shadow_result.get('inconsistent', False):
            results['anomalies'].append('Inconsistent shadow directions')
            results['score'] += 0.3
        
        results['score'] = min(results['score'], 1.0)
        
        return results
        
    except Exception as e:
        print(f"Physics consistency analysis error: {e}")
        return {
            'score': 0.5,
            'error': str(e)
        }


def analyze_lighting_consistency(frame_paths):
    try:
        lighting_values = []
        
        for frame_path in frame_paths:
            if not os.path.exists(frame_path):
                continue
            
            image = cv2.imread(frame_path)
            if image is None or image.size == 0:
                continue
            
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            
            avg_lightness = np.mean(l_channel)
            lighting_values.append(avg_lightness)
        
        if len(lighting_values) < 2:
            return {'consistent': True, 'reason': 'Insufficient frames'}
        
        lighting_array = np.array(lighting_values)
        diffs = np.abs(np.diff(lighting_array))
        
        sudden_changes = np.sum(diffs > 30)
        
        variance = np.var(lighting_array)
        
        inconsistent = (sudden_changes > len(frame_paths) * 0.2) or (variance > 500)
        
        return {
            'consistent': not inconsistent,
            'sudden_changes': int(sudden_changes),
            'variance': float(variance),
            'avg_lighting': float(np.mean(lighting_array))
        }
        
    except Exception as e:
        print(f"Lighting analysis error: {e}")
        return {'consistent': True, 'error': str(e)}


def analyze_depth_consistency(frame_paths):
    try:
        depth_maps = []
        
        for frame_path in frame_paths[:10]:
            if not os.path.exists(frame_path):
                continue
            
            depth = estimate_depth_midas(frame_path)
            if depth is not None:
                depth_maps.append(depth)
        
        if len(depth_maps) < 2:
            return {'plausible': True, 'reason': 'Cannot estimate depth'}
        
        depth_variances = [np.var(d) for d in depth_maps]
        avg_variance = np.mean(depth_variances)
        
        depth_changes = []
        for i in range(len(depth_maps) - 1):
            change = np.mean(np.abs(depth_maps[i] - depth_maps[i+1]))
            depth_changes.append(change)
        
        avg_change = np.mean(depth_changes) if depth_changes else 0
        
        implausible = avg_variance > 0.3 or avg_change > 0.2
        
        return {
            'plausible': not implausible,
            'avg_variance': float(avg_variance),
            'avg_change': float(avg_change)
        }
        
    except Exception as e:
        print(f"Depth analysis error: {e}")
        return {'plausible': True, 'error': str(e)}


def estimate_depth_midas(frame_path):
    try:
        midas, transform, device = get_midas_model()
        
        if midas is None:
            return None
        
        if not os.path.exists(frame_path):
            print(f"Frame path does not exist: {frame_path}")
            return None
        
        img = cv2.imread(frame_path)
        
        if img is None:
            print(f"Failed to load image: {frame_path}")
            return None
        
        if img.size == 0 or len(img.shape) < 2:
            print(f"Invalid image: {frame_path}")
            return None
        
        if img.shape[0] == 0 or img.shape[1] == 0:
            print(f"Empty image dimensions: {img.shape}")
            return None
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        input_batch = transform(img_rgb).to(device)
        
        with torch.no_grad():
            prediction = midas(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img_rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
        
        depth_map = prediction.cpu().numpy()
        
        depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
        
        return depth_map
        
    except Exception as e:
        print(f"MiDaS depth estimation error: {e}")
        return None


def analyze_shadows(frame_paths):
    try:
        shadow_directions = []
        
        for frame_path in frame_paths:
            if not os.path.exists(frame_path):
                continue
            
            image = cv2.imread(frame_path)
            if image is None or image.size == 0:
                continue
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            _, shadow_mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
            
            contours, _ = cv2.findContours(shadow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 0:
                largest_shadow = max(contours, key=cv2.contourArea)
                
                if len(largest_shadow) >= 5:
                    ellipse = cv2.fitEllipse(largest_shadow)
                    angle = ellipse[2]
                    shadow_directions.append(angle)
        
        if len(shadow_directions) < 2:
            return {'inconsistent': False, 'reason': 'Insufficient shadows'}
        
        shadow_array = np.array(shadow_directions)
        
        shadow_std = np.std(shadow_array)
        
        inconsistent = shadow_std > 30
        
        return {
            'inconsistent': inconsistent,
            'shadow_std': float(shadow_std),
            'num_shadows': len(shadow_directions)
        }
        
    except Exception as e:
        print(f"Shadow analysis error: {e}")
        return {'inconsistent': False, 'error': str(e)}
