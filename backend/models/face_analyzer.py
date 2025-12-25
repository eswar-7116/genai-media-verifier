import numpy as np
from PIL import Image
import cv2
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except:
    MEDIAPIPE_AVAILABLE = False


class FaceAnalyzer:
    def __init__(self):
        if not MEDIAPIPE_AVAILABLE:
            print("Warning: MediaPipe not available, using OpenCV for face detection")
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.use_mediapipe = False
        else:
            try:
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
                self.use_mediapipe = True
            except Exception as e:
                print(f"MediaPipe initialization failed: {e}, falling back to OpenCV")
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                self.use_mediapipe = False
    
    def analyze_face(self, image):
        """
        Main entry point for facial analysis.
        
        Returns:
            dict: {
                'score': float (0-1, higher = more likely fake),
                'face_detected': bool,
                'symmetry_score': float,
                'eye_quality_score': float,
                'skin_texture_score': float,
                'lighting_score': float
            }
        """
        try:
            if isinstance(image, str):
                image = Image.open(image).convert('RGB')
            elif isinstance(image, Image.Image):
                image = image.convert('RGB')
            
            img_array = np.array(image)
            
            # Detect facial landmarks
            landmarks = self.detect_facial_landmarks(img_array)
            
            if landmarks is None:
                return {
                    'score': 0.5,
                    'face_detected': False,
                    'error': 'No face detected'
                }
            
            # Run all facial checks
            symmetry_score = self.check_symmetry(landmarks, img_array.shape)
            eye_score = self.analyze_eye_region(img_array, landmarks)
            texture_score = self.check_skin_texture(img_array, landmarks)
            lighting_score = self.validate_lighting(img_array, landmarks)
            
            # Combine scores
            final_score = (
                symmetry_score * 0.30 +
                eye_score * 0.30 +
                texture_score * 0.25 +
                lighting_score * 0.15
            )
            
            return {
                'score': float(final_score),
                'face_detected': True,
                'symmetry_score': float(symmetry_score),
                'eye_quality_score': float(eye_score),
                'skin_texture_score': float(texture_score),
                'lighting_score': float(lighting_score),
                'symmetry_anomaly': bool(symmetry_score > 0.6),
                'eye_anomaly': bool(eye_score > 0.6),
                'texture_anomaly': bool(texture_score > 0.6)
            }
        
        except Exception as e:
            print(f"Face analysis error: {e}")
            return {
                'score': 0.5,
                'face_detected': False,
                'error': str(e)
            }
    
    def detect_facial_landmarks(self, image):
        """Detect facial landmarks using MediaPipe or OpenCV fallback"""
        if self.use_mediapipe:
            results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            
            if not results.multi_face_landmarks:
                return None
            
            landmarks = results.multi_face_landmarks[0]
            
            # Convert to numpy array
            h, w = image.shape[:2]
            landmark_points = []
            
            for landmark in landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                landmark_points.append([x, y])
            
            return np.array(landmark_points)
        else:
            # OpenCV fallback - just detect face region
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return None
            
            # Return simple landmarks (face corners and center)
            x, y, w, h = faces[0]
            landmarks = np.array([
                [x, y], [x+w, y], [x, y+h], [x+w, y+h],
                [x+w//2, y+h//2]  # center
            ])
            return landmarks
    
    def check_symmetry(self, landmarks, image_shape):
        """
        Check facial symmetry.
        Deepfakes often have asymmetric artifacts.
        """
        h, w = image_shape[:2]
        center_x = w // 2
        
        # Get left and right side landmarks
        left_points = landmarks[landmarks[:, 0] < center_x]
        right_points = landmarks[landmarks[:, 0] >= center_x]
        
        if len(left_points) == 0 or len(right_points) == 0:
            return 0.5
        
        # Mirror right side to left
        right_mirrored = right_points.copy()
        right_mirrored[:, 0] = w - right_mirrored[:, 0]
        
        # Calculate distances between corresponding points
        # For simplicity, use centroids
        left_centroid = np.mean(left_points, axis=0)
        right_centroid = np.mean(right_points, axis=0)
        right_centroid[0] = w - right_centroid[0]
        
        distance = np.linalg.norm(left_centroid - right_centroid)
        
        # Normalize by image width
        asymmetry_ratio = distance / w
        
        # Higher ratio = more asymmetric = more likely fake
        score = min(asymmetry_ratio * 10.0, 1.0)
        
        return float(score)
    
    def analyze_eye_region(self, image, landmarks):
        """
        Analyze eye region quality.
        Deepfakes struggle with realistic eyes.
        """
        if not self.use_mediapipe or len(landmarks) < 10:
            # Simplified analysis for OpenCV mode
            return 0.5
        
        # Eye landmark indices (approximate - MediaPipe has 468 points)
        # Left eye: points around 33, 133, 160, 159, 158, 157, 173
        # Right eye: points around 362, 263, 387, 386, 385, 384, 398
        
        left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        right_eye_indices = [362, 263, 387, 386, 385, 384, 398]
        
        try:
            left_eye_points = landmarks[left_eye_indices]
            right_eye_points = landmarks[right_eye_indices]
            
            # Extract eye regions
            left_x_min, left_y_min = left_eye_points.min(axis=0)
            left_x_max, left_y_max = left_eye_points.max(axis=0)
            
            right_x_min, right_y_min = right_eye_points.min(axis=0)
            right_x_max, right_y_max = right_eye_points.max(axis=0)
            
            # Add padding
            padding = 10
            left_eye_region = image[
                max(0, left_y_min-padding):min(image.shape[0], left_y_max+padding),
                max(0, left_x_min-padding):min(image.shape[1], left_x_max+padding)
            ]
            
            right_eye_region = image[
                max(0, right_y_min-padding):min(image.shape[0], right_y_max+padding),
                max(0, right_x_min-padding):min(image.shape[1], right_x_max+padding)
            ]
            
            # Analyze sharpness and detail
            left_sharpness = self._calculate_sharpness(left_eye_region)
            right_sharpness = self._calculate_sharpness(right_eye_region)
            
            avg_sharpness = (left_sharpness + right_sharpness) / 2
            
            # Low sharpness = likely fake (blurry/soft eyes)
            # Normalize: lower sharpness = higher fake score
            score = 1.0 - min(avg_sharpness / 100.0, 1.0)
            
            return float(score)
        
        except Exception as e:
            return 0.5
    
    def _calculate_sharpness(self, image_region):
        """Calculate image sharpness using Laplacian variance"""
        if image_region.size == 0:
            return 0.0
        
        gray = cv2.cvtColor(image_region, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return float(laplacian_var)
    
    def check_skin_texture(self, image, landmarks):
        """
        Analyze skin texture.
        Deepfakes often have unnaturally smooth skin.
        """
        # Extract face region
        x_min, y_min = landmarks.min(axis=0)
        x_max, y_max = landmarks.max(axis=0)
        
        face_region = image[y_min:y_max, x_min:x_max]
        
        if face_region.size == 0:
            return 0.5
        
        # Convert to grayscale
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
        
        # Calculate texture using standard deviation of Laplacian
        laplacian = cv2.Laplacian(gray_face, cv2.CV_64F)
        texture_measure = np.std(laplacian)
        
        # Also check local variance (skin pores create variance)
        local_variance = np.var(gray_face)
        
        # Real skin has texture (higher variance and laplacian std)
        # Fake skin is smooth (lower variance)
        
        texture_score = texture_measure + (local_variance / 100.0)
        
        # Lower texture = more likely fake
        score = 1.0 - min(texture_score / 50.0, 1.0)
        
        return float(score)
    
    def validate_lighting(self, image, landmarks):
        """
        Check lighting consistency on face.
        Deepfakes often have inconsistent lighting.
        """
        # Extract face region
        x_min, y_min = landmarks.min(axis=0)
        x_max, y_max = landmarks.max(axis=0)
        
        face_region = image[y_min:y_max, x_min:x_max]
        
        if face_region.size == 0:
            return 0.5
        
        # Convert to LAB color space for better luminance analysis
        lab = cv2.cvtColor(face_region, cv2.COLOR_RGB2LAB)
        l_channel = lab[:, :, 0]
        
        # Divide face into regions (left, center, right, top, bottom)
        h, w = l_channel.shape
        
        left_light = np.mean(l_channel[:, :w//3])
        center_light = np.mean(l_channel[:, w//3:2*w//3])
        right_light = np.mean(l_channel[:, 2*w//3:])
        
        top_light = np.mean(l_channel[:h//2, :])
        bottom_light = np.mean(l_channel[h//2:, :])
        
        # Check consistency
        horizontal_diff = max(abs(left_light - right_light), abs(left_light - center_light))
        vertical_diff = abs(top_light - bottom_light)
        
        # High difference = inconsistent lighting = likely fake
        total_diff = (horizontal_diff + vertical_diff) / 2
        
        score = min(total_diff / 50.0, 1.0)
        
        return float(score)


# Global instance
_face_analyzer = None

def get_face_analyzer():
    global _face_analyzer
    if _face_analyzer is None:
        _face_analyzer = FaceAnalyzer()
    return _face_analyzer


def analyze_face(image):
    """Convenience function"""
    analyzer = get_face_analyzer()
    return analyzer.analyze_face(image)
