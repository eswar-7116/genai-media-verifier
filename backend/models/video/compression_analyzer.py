import cv2
import numpy as np
from scipy import fftpack


def analyze_region_compression(frame_paths):
    try:
        results = {
            'score': 0.0,
            'compression_mismatches': 0,
            'avg_face_compression': 0.0,
            'avg_background_compression': 0.0,
            'compression_differences': [],
            'suspicious_frames': []
        }
        
        face_compressions = []
        bg_compressions = []
        
        sample_indices = range(0, len(frame_paths), max(1, len(frame_paths) // 20))
        
        for idx in sample_indices:
            if idx >= len(frame_paths):
                break
            
            frame_path = frame_paths[idx]
            
            face_region, bg_region = extract_face_and_background(frame_path)
            
            if face_region is None or bg_region is None:
                continue
            
            face_comp = analyze_compression_artifacts(face_region)
            bg_comp = analyze_compression_artifacts(bg_region)
            
            face_compressions.append(face_comp)
            bg_compressions.append(bg_comp)
            
            comp_diff = abs(face_comp - bg_comp)
            results['compression_differences'].append(comp_diff)
            
            if comp_diff > 0.25:
                results['compression_mismatches'] += 1
                results['suspicious_frames'].append({
                    'frame_index': idx,
                    'face_compression': float(face_comp),
                    'bg_compression': float(bg_comp),
                    'difference': float(comp_diff)
                })
        
        if face_compressions:
            results['avg_face_compression'] = float(np.mean(face_compressions))
            results['avg_background_compression'] = float(np.mean(bg_compressions))
            
            avg_diff = np.mean(results['compression_differences'])
            mismatch_rate = results['compression_mismatches'] / len(face_compressions)
            
            results['score'] = min((avg_diff * 2.0) + (mismatch_rate * 0.5), 1.0)
        
        return results
        
    except Exception as e:
        print(f"Region compression analysis error: {e}")
        return {
            'score': 0.0,
            'error': str(e)
        }


def extract_face_and_background(frame_path):
    try:
        image = cv2.imread(frame_path)
        if image is None:
            return None, None
        
        h, w = image.shape[:2]
        
        return extract_face_opencv(image)
        
    except Exception as e:
        print(f"Face/background extraction error: {e}")
        try:
            image = cv2.imread(frame_path)
            h, w = image.shape[:2]
            face_region = image[h//4:3*h//4, w//4:3*w//4]
            bg_region = np.vstack([image[:h//4, :], image[3*h//4:, :]])
            return face_region, bg_region
        except:
            return None, None


def extract_face_opencv(image):
    try:
        h, w = image.shape[:2]
        
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        
        if len(faces) == 0:
            face_region = image[h//4:3*h//4, w//4:3*w//4]
            bg_region = np.vstack([image[:h//4, :], image[3*h//4:, :]])
            return face_region, bg_region
        
        x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        
        x = max(0, x)
        y = max(0, y)
        x2 = min(w, x + fw)
        y2 = min(h, y + fh)
        
        face_region = image[y:y2, x:x2]
        
        top_bg = image[:y, :] if y > 0 else None
        bottom_bg = image[y2:, :] if y2 < h else None
        left_bg = image[y:y2, :x] if x > 0 else None
        right_bg = image[y:y2, x2:] if x2 < w else None
        
        bg_parts = [bg for bg in [top_bg, bottom_bg, left_bg, right_bg] if bg is not None and bg.size > 0]
        
        if not bg_parts:
            return face_region, None
        
        if len(bg_parts) >= 2:
            bg_region = np.vstack(bg_parts[:2])
        else:
            bg_region = bg_parts[0]
        
        return face_region, bg_region
        
    except Exception as e:
        h, w = image.shape[:2]
        face_region = image[h//4:3*h//4, w//4:3*w//4]
        bg_region = np.vstack([image[:h//4, :], image[3*h//4:, :]])
        return face_region, bg_region


def analyze_compression_artifacts(region):
    try:
        if region is None or region.size == 0:
            return 0.5
        
        region = cv2.resize(region, (128, 128))
        
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        
        dct = fftpack.dct(fftpack.dct(gray.T, norm='ortho').T, norm='ortho')
        
        h, w = dct.shape
        
        block_size = 8
        block_variances = []
        
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = dct[i:i+block_size, j:j+block_size]
                
                high_freq = block[block_size//2:, block_size//2:]
                
                hf_energy = np.sum(np.abs(high_freq))
                block_variances.append(hf_energy)
        
        if not block_variances:
            return 0.5
        
        mean_energy = np.mean(block_variances)
        std_energy = np.std(block_variances)
        
        compression_score = (std_energy / (mean_energy + 1.0)) / 10.0
        compression_score = min(compression_score, 1.0)
        
        return float(compression_score)
        
    except Exception as e:
        print(f"Compression artifact analysis error: {e}")
        return 0.5


def detect_blocking_artifacts(region):
    try:
        if region is None or region.size == 0:
            return 0.5
        
        region = cv2.resize(region, (128, 128))
        
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        
        edges = cv2.Canny(gray, 50, 150)
        
        horizontal_kernel = np.ones((1, 8), np.uint8)
        vertical_kernel = np.ones((8, 1), np.uint8)
        
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        h_count = np.sum(horizontal_lines > 0)
        v_count = np.sum(vertical_lines > 0)
        
        blocking_score = (h_count + v_count) / edges.size
        
        return float(blocking_score)
        
    except Exception as e:
        return 0.5
