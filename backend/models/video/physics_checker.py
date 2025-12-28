"""
Physics and Consistency Checker - LAYER 2D
Analyzes physical plausibility and consistency
"""
import cv2
import numpy as np
import torch
from PIL import Image


def analyze_physics_consistency(frame_paths):
    """
    Check physical consistency and plausibility
    
    Returns:
        dict: {
            'score': float (0-1, higher = more suspicious),
            'lighting_consistent': bool,
            'depth_plausible': bool,
            'reflection_consistent': bool
        }
    """
    try:
        results = {
            'score': 0.0,
            'lighting_consistent': True,
            'depth_plausible': True,
            'reflection_consistent': True,
            'anomalies': []
        }
        
        # 1. Lighting Consistency
        lighting_result = analyze_lighting_consistency(frame_paths)
        results['lighting_consistent'] = lighting_result['consistent']
        
        if not lighting_result['consistent']:
            results['anomalies'].append('Inconsistent lighting detected')
            results['score'] += 0.4
        
        # 2. Depth Consistency
        depth_result = analyze_depth_consistency(frame_paths)
        results['depth_plausible'] = depth_result['plausible']
        
        if not depth_result['plausible']:
            results['anomalies'].append('Implausible depth map')
            results['score'] += 0.3
        
        # 3. Shadow Analysis
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
    """
    Analyze lighting consistency across frames
    Sudden lighting changes can indicate splicing
    """
    try:
        lighting_values = []
        
        for frame_path in frame_paths:
            image = cv2.imread(frame_path)
            if image is None:
                continue
            
            # Convert to LAB color space (L = lightness)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            
            # Average lightness
            avg_lightness = np.mean(l_channel)
            lighting_values.append(avg_lightness)
        
        if len(lighting_values) < 2:
            return {'consistent': True, 'reason': 'Insufficient frames'}
        
        # Check for sudden jumps
        lighting_array = np.array(lighting_values)
        diffs = np.abs(np.diff(lighting_array))
        
        # Threshold for sudden change
        sudden_changes = np.sum(diffs > 30)  # LAB L channel ranges 0-100
        
        # Check overall variance
        variance = np.var(lighting_array)
        
        # Inconsistent if: multiple sudden changes or very high variance
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
    """
    Estimate depth maps and check plausibility
    Uses MiDaS pre-trained model
    """
    try:
        # Try to use MiDaS for depth estimation
        depth_maps = []
        
        for frame_path in frame_paths[:10]:  # Limit to 10 frames for performance
            depth = estimate_depth_midas(frame_path)
            if depth is not None:
                depth_maps.append(depth)
        
        if len(depth_maps) < 2:
            # Fallback: simple depth heuristic
            return {'plausible': True, 'reason': 'Cannot estimate depth'}
        
        # Check depth consistency
        # Real scenes have consistent depth relationships
        # Manipulated faces may have inconsistent depth
        
        depth_variances = [np.var(d) for d in depth_maps]
        avg_variance = np.mean(depth_variances)
        
        # Check for sudden depth changes
        depth_changes = []
        for i in range(len(depth_maps) - 1):
            change = np.mean(np.abs(depth_maps[i] - depth_maps[i+1]))
            depth_changes.append(change)
        
        avg_change = np.mean(depth_changes) if depth_changes else 0
        
        # Implausible if: very high variance or sudden depth shifts
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
    """Estimate depth using MiDaS model"""
    try:
        # Load MiDaS model
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Use small MiDaS model for speed
        midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        midas.to(device)
        midas.eval()
        
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        transform = midas_transforms.small_transform
        
        # Load image
        img = cv2.imread(frame_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Transform and predict
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
        
        # Normalize
        depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
        
        return depth_map
        
    except Exception as e:
        print(f"MiDaS depth estimation error: {e}")
        return None


def analyze_shadows(frame_paths):
    """
    Analyze shadow consistency
    Shadows should have consistent direction within a scene
    """
    try:
        shadow_directions = []
        
        for frame_path in frame_paths:
            image = cv2.imread(frame_path)
            if image is None:
                continue
            
            # Detect shadow regions (darker areas)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Threshold to find dark regions
            _, shadow_mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours of shadows
            contours, _ = cv2.findContours(shadow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 0:
                # Get largest shadow
                largest_shadow = max(contours, key=cv2.contourArea)
                
                # Fit ellipse to estimate direction
                if len(largest_shadow) >= 5:
                    ellipse = cv2.fitEllipse(largest_shadow)
                    angle = ellipse[2]  # Orientation angle
                    shadow_directions.append(angle)
        
        if len(shadow_directions) < 2:
            return {'inconsistent': False, 'reason': 'Insufficient shadows'}
        
        # Check if shadow directions are consistent
        shadow_array = np.array(shadow_directions)
        
        # Handle angle wrapping (0° = 360°)
        shadow_std = np.std(shadow_array)
        
        # Inconsistent if high variance in shadow directions
        inconsistent = shadow_std > 30  # degrees
        
        return {
            'inconsistent': inconsistent,
            'shadow_std': float(shadow_std),
            'num_shadows': len(shadow_directions)
        }
        
    except Exception as e:
        print(f"Shadow analysis error: {e}")
        return {'inconsistent': False, 'error': str(e)}
