import numpy as np
from PIL import Image
import cv2

def analyze_face(image):
    analyzer = get_face_analyzer()
    return analyzer.analyze_face(image)


MEDIAPIPE_AVAILABLE = False
MEDIAPIPE_VERSION = None

try:
    import mediapipe as mp
    MEDIAPIPE_VERSION = mp.__version__
    
    try:
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        MEDIAPIPE_AVAILABLE = True
        print(f"MediaPipe {MEDIAPIPE_VERSION} with Tasks API loaded")
    except Exception as e:
        print(f"MediaPipe Tasks API import failed: {e}")
        print(f"  This is often caused by WASM/memory issues in the Python environment")
        print(f"  Falling back to OpenCV DNN (reduced facial analysis accuracy)")
        MEDIAPIPE_AVAILABLE = False
        
except ImportError as e:
    print(f"MediaPipe not available: {e}")
    print(f"  Install with: pip install mediapipe")


import os
import urllib.request

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models_cache')
FACE_LANDMARKER_MODEL = os.path.join(MODEL_DIR, 'face_landmarker.task')
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'


def download_model():
    if os.path.exists(FACE_LANDMARKER_MODEL):
        return True
    
    try:
        print(f"Downloading MediaPipe face landmarker model...")
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        urllib.request.urlretrieve(MODEL_URL, FACE_LANDMARKER_MODEL)
        
        if os.path.exists(FACE_LANDMARKER_MODEL):
            size_mb = os.path.getsize(FACE_LANDMARKER_MODEL) / (1024 * 1024)
            print(f"Model downloaded successfully ({size_mb:.1f} MB)")
            return True
        else:
            print("Model download failed")
            return False
            
    except Exception as e:
        print(f"Failed to download model: {e}")
        return False


class FaceAnalyzer:
    def __init__(self):
        self.use_mediapipe = False
        self.detector = None
        
        if MEDIAPIPE_AVAILABLE:
            if download_model():
                try:
                    from mediapipe.tasks import python
                    from mediapipe.tasks.python import vision
                    
                    base_options = python.BaseOptions(
                        model_asset_path=FACE_LANDMARKER_MODEL,
                        delegate=python.BaseOptions.Delegate.CPU
                    )
                    
                    options = vision.FaceLandmarkerOptions(
                        base_options=base_options,
                        running_mode=vision.RunningMode.IMAGE,
                        output_face_blendshapes=False,
                        output_facial_transformation_matrixes=False,
                        num_faces=1,
                        min_face_detection_confidence=0.5,
                        min_face_presence_confidence=0.5,
                        min_tracking_confidence=0.5
                    )
                    
                    self.detector = vision.FaceLandmarker.create_from_options(options)
                    self.use_mediapipe = True
                    print(f"MediaPipe Face Landmarker initialized")
                    
                except Exception as e:
                    print(f"MediaPipe initialization failed: {e}")
                    print(f"  Common causes:")
                    print(f"  - WASM initialization failure (try upgrading mediapipe)")
                    print(f"  - Model file corrupted (delete face_landmarker.task and retry)")
                    print(f"  - Memory constraints (restart Python environment)")
                    print(f"  Facial analysis will use basic OpenCV detection (less accurate)")
                    self._init_opencv()
            else:
                self._init_opencv()
        else:
            self._init_opencv()
    
    def _init_opencv(self):
        self.use_mediapipe = False
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        try:
            model_dir = os.path.join(os.path.dirname(__file__), '..', 'models_cache')
            prototxt_path = os.path.join(model_dir, 'deploy.prototxt')
            caffemodel_path = os.path.join(model_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
            
            if not os.path.exists(prototxt_path) or not os.path.exists(caffemodel_path):
                os.makedirs(model_dir, exist_ok=True)
                
                prototxt_url = 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt'
                caffemodel_url = 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel'
                
                try:
                    if not os.path.exists(prototxt_path):
                        urllib.request.urlretrieve(prototxt_url, prototxt_path)
                    if not os.path.exists(caffemodel_path):
                        print("Downloading DNN face detection model (7MB)...")
                        urllib.request.urlretrieve(caffemodel_url, caffemodel_path)
                        print("DNN model downloaded")
                except:
                    pass
            
            if os.path.exists(prototxt_path) and os.path.exists(caffemodel_path):
                self.dnn_net = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
                self.use_dnn = True
                print("OpenCV DNN face detection initialized")
                return
                
        except Exception as e:
            print(f"  DNN face detector failed: {e}")
        
        self.use_dnn = False
        print("OpenCV Haar Cascade face detection initialized")
    
    def __del__(self):
        if self.use_mediapipe and self.detector:
            try:
                self.detector.close()
            except:
                pass
    
    def analyze_face(self, image):
        try:
            if isinstance(image, str):
                image = Image.open(image).convert('RGB')
            elif isinstance(image, Image.Image):
                image = image.convert('RGB')
            
            img_array = np.array(image)
            
            landmarks = self.detect_facial_landmarks(img_array)
            
            if landmarks is None:
                return {
                    'score': 0.5,
                    'face_detected': False,
                    'error': 'No face detected'
                }
            
            symmetry_score = self.check_symmetry(landmarks, img_array.shape)
            eye_score = self.analyze_eye_region(img_array, landmarks)
            texture_score = self.check_skin_texture(img_array, landmarks)
            lighting_score = self.validate_lighting(img_array, landmarks)
            
            final_score = (
                eye_score * 0.35 +
                texture_score * 0.30 +
                symmetry_score * 0.25 +
                lighting_score * 0.10
            )
            
            method_name = 'MediaPipe' if self.use_mediapipe else ('OpenCV DNN' if hasattr(self, 'use_dnn') and self.use_dnn else 'OpenCV Haar')
            
            return {
                'score': float(final_score),
                'face_detected': True,
                'symmetry_score': float(symmetry_score),
                'eye_quality_score': float(eye_score),
                'skin_texture_score': float(texture_score),
                'lighting_score': float(lighting_score),
                'symmetry_anomaly': bool(symmetry_score > 0.65),
                'eye_anomaly': bool(eye_score > 0.70),
                'texture_anomaly': bool(texture_score > 0.70),
                'method_used': method_name
            }
        
        except Exception as e:
            print(f"Face analysis error: {e}")
            return {
                'score': 0.5,
                'face_detected': False,
                'error': str(e)
            }
    
    def detect_facial_landmarks(self, image):
        if self.use_mediapipe and self.detector:
            try:
                import mediapipe as mp
                
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
                detection_result = self.detector.detect(mp_image)
                
                if not detection_result.face_landmarks:
                    return None
                
                face_landmarks = detection_result.face_landmarks[0]
                
                h, w = image.shape[:2]
                landmark_points = []
                
                for landmark in face_landmarks:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    x = max(0, min(x, w - 1))
                    y = max(0, min(y, h - 1))
                    landmark_points.append([x, y])
                
                return np.array(landmark_points)
                
            except Exception as e:
                print(f"MediaPipe detection failed: {e}")
                return self._opencv_detection(image)
        else:
            return self._opencv_detection(image)
    
    def _opencv_detection(self, image):
        if hasattr(self, 'use_dnn') and self.use_dnn:
            try:
                h, w = image.shape[:2]
                blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
                self.dnn_net.setInput(blob)
                detections = self.dnn_net.forward()
                
                best_confidence = 0
                best_box = None
                
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.5 and confidence > best_confidence:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        best_confidence = confidence
                        best_box = box.astype("int")
                
                if best_box is not None:
                    x1, y1, x2, y2 = best_box
                    x, y, fw, fh = x1, y1, x2-x1, y2-y1
                    
                    landmarks = self._create_enhanced_landmarks(x, y, fw, fh, image)
                    return landmarks
                    
            except Exception as e:
                print(f"DNN detection failed: {e}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        
        if len(faces) == 0:
            return None
        
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        
        landmarks = self._create_enhanced_landmarks(x, y, w, h, image)
        return landmarks
    
    def _create_enhanced_landmarks(self, x, y, w, h, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        landmarks = [
            [x, y], [x+w, y], [x, y+h], [x+w, y+h],
            [x+w//2, y], [x+w//2, y+h],
            [x, y+h//2], [x+w, y+h//2],
            [x+w//2, y+h//2],
        ]
        
        face_roi = gray[y:y+h, x:x+w]
        if hasattr(self, 'eye_cascade'):
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 4, minSize=(20, 20))
            
            for (ex, ey, ew, eh) in eyes[:2]:
                eye_center_x = x + ex + ew // 2
                eye_center_y = y + ey + eh // 2
                landmarks.append([eye_center_x, eye_center_y])
        
        landmarks.extend([
            [x+w//4, y+h//3],
            [x+3*w//4, y+h//3],
            [x+w//2, y+h//2],
            [x+w//2, y+2*h//3],
            [x+w//3, y+2*h//3],
            [x+2*w//3, y+2*h//3],
        ])
        
        return np.array(landmarks)
    
    def check_symmetry(self, landmarks, image_shape):
        h, w = image_shape[:2]
        center_x = w // 2
        
        left_points = landmarks[landmarks[:, 0] < center_x]
        right_points = landmarks[landmarks[:, 0] >= center_x]
        
        if len(left_points) == 0 or len(right_points) == 0:
            return 0.5
        
        left_centroid = np.mean(left_points, axis=0)
        right_centroid = np.mean(right_points, axis=0)
        right_centroid_mirrored = right_centroid.copy()
        right_centroid_mirrored[0] = w - right_centroid_mirrored[0]
        
        distance = np.linalg.norm(left_centroid - right_centroid_mirrored)
        asymmetry_ratio = distance / w
        score = min(asymmetry_ratio * 10.0, 1.0)
        
        return float(score)
    
    def analyze_eye_region(self, image, landmarks):
        try:
            h, w = image.shape[:2]
            
            eye_candidates = []
            for lm in landmarks:
                if h * 0.2 < lm[1] < h * 0.5:
                    eye_candidates.append(lm)
            
            if len(eye_candidates) < 2 and hasattr(self, 'eye_cascade'):
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                upper_half = gray[:h//2, :]
                
                eyes = self.eye_cascade.detectMultiScale(upper_half, 1.1, 3, minSize=(15, 15))
                
                if len(eyes) < 2:
                    eyes = self.eye_cascade.detectMultiScale(upper_half, 1.05, 2, minSize=(10, 10))
                
                for (ex, ey, ew, eh) in eyes[:2]:
                    eye_candidates.append([ex + ew//2, ey + eh//2])
            
            if len(eye_candidates) < 2 and len(landmarks) > 4:
                x_min, y_min = landmarks.min(axis=0)
                x_max, y_max = landmarks.max(axis=0)
                face_width = x_max - x_min
                face_height = y_max - y_min
                
                left_eye_x = int(x_min + face_width * 0.35)
                right_eye_x = int(x_min + face_width * 0.65)
                eye_y = int(y_min + face_height * 0.35)
                
                eye_candidates = [[left_eye_x, eye_y], [right_eye_x, eye_y]]
            
            if len(eye_candidates) < 2:
                return 0.55
            
            sharpness_scores = []
            texture_scores = []
            
            for eye_point in eye_candidates[:2]:
                x, y = eye_point
                x1, y1 = max(0, x-25), max(0, y-25)
                x2, y2 = min(w, x+25), min(h, y+25)
                eye_region = image[y1:y2, x1:x2]
                
                if eye_region.size > 0:
                    sharpness = self._calculate_sharpness(eye_region)
                    sharpness_scores.append(sharpness)
                    
                    if len(eye_region.shape) == 3:
                        gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_RGB2GRAY)
                    else:
                        gray_eye = eye_region
                    texture_var = np.var(gray_eye)
                    texture_scores.append(texture_var)
            
            if sharpness_scores and texture_scores:
                avg_sharpness = np.mean(sharpness_scores)
                avg_texture = np.mean(texture_scores)
                
                if avg_sharpness < 50:
                    sharpness_score = 0.8
                elif avg_sharpness < 100:
                    sharpness_score = 0.5
                elif avg_sharpness < 200:
                    sharpness_score = 0.2
                else:
                    sharpness_score = 0.0
                
                if avg_texture < 100:
                    texture_score = 0.8
                elif avg_texture < 300:
                    texture_score = 0.5
                elif avg_texture < 600:
                    texture_score = 0.2
                else:
                    texture_score = 0.0
                
                combined_score = (sharpness_score * 0.5) + (texture_score * 0.5)
                return float(combined_score)
            
            return 0.55
        except Exception as e:
            return 0.55
    
    def _calculate_sharpness(self, image_region):
        if image_region.size == 0 or image_region.shape[0] < 3 or image_region.shape[1] < 3:
            return 0.0
        
        if len(image_region.shape) == 3:
            gray = cv2.cvtColor(image_region, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_region
            
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return float(laplacian_var)
    
    def check_skin_texture(self, image, landmarks):
        x_min, y_min = landmarks.min(axis=0)
        x_max, y_max = landmarks.max(axis=0)
        
        face_region = image[y_min:y_max, x_min:x_max]
        
        if face_region.size == 0:
            return 0.5
        
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
        laplacian = cv2.Laplacian(gray_face, cv2.CV_64F)
        texture_measure = np.std(laplacian)
        local_variance = np.var(gray_face)
        
        texture_score = texture_measure + (local_variance / 100.0)
        score = 1.0 - min(texture_score / 50.0, 1.0)
        
        return float(score)
    
    def validate_lighting(self, image, landmarks):
        x_min, y_min = landmarks.min(axis=0)
        x_max, y_max = landmarks.max(axis=0)
        
        face_region = image[y_min:y_max, x_min:x_max]
        
        if face_region.size == 0:
            return 0.5
        
        lab = cv2.cvtColor(face_region, cv2.COLOR_RGB2LAB)
        l_channel = lab[:, :, 0]
        
        h, w = l_channel.shape
        
        if w < 3 or h < 2:
            return 0.5
        
        left_light = np.mean(l_channel[:, :w//3])
        center_light = np.mean(l_channel[:, w//3:2*w//3])
        right_light = np.mean(l_channel[:, 2*w//3:])
        top_light = np.mean(l_channel[:h//2, :])
        bottom_light = np.mean(l_channel[h//2:, :])
        
        horizontal_diff = max(abs(left_light - right_light), abs(left_light - center_light))
        vertical_diff = abs(top_light - bottom_light)
        total_diff = (horizontal_diff + vertical_diff) / 2
        
        score = min(total_diff / 50.0, 1.0)
        
        return float(score)


_face_analyzer = None

def get_face_analyzer():
    global _face_analyzer
    if _face_analyzer is None:
        _face_analyzer = FaceAnalyzer()
    return _face_analyzer
