import cv2
import numpy as np
import librosa
import subprocess
import os
import tempfile

FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
FFPROBE_PATH = FFMPEG_PATH.replace("ffmpeg", "ffprobe") if "ffmpeg" in FFMPEG_PATH else "ffprobe"

MODELS_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models_cache')


def analyze_audio_stream(video_path):
    try:
        has_audio = check_audio_presence(video_path)
        
        if not has_audio:
            return {
                'has_audio': False,
                'score': 0.0,
                'message': 'No audio stream detected'
            }
        
        results = {
            'has_audio': True,
            'score': 0.0,
            'voice_deepfake_score': 0.0,
            'lip_sync_score': 0.0,
            'audio_consistency': 0.0,
            'anomalies': []
        }
        
        audio_path = extract_audio(video_path)
        
        if not audio_path:
            return {
                'has_audio': True,
                'score': 0.0,
                'voice_deepfake_score': 0.0,
                'lip_sync_score': 0.0,
                'audio_consistency': 0.0,
                'message': 'FFmpeg not found - audio analysis skipped. Install FFmpeg for audio analysis.',
                'anomalies': ['Audio extraction failed - FFmpeg required']
            }
        
        voice_result = detect_voice_deepfake(audio_path)
        results['voice_deepfake_score'] = voice_result.get('score', 0.5)
        
        if voice_result.get('suspicious', False):
            results['anomalies'].append('Suspicious voice patterns detected')
        
        lip_sync_result = analyze_lip_sync(video_path, audio_path)
        results['lip_sync_score'] = lip_sync_result.get('score', 0.0)
        
        if lip_sync_result.get('out_of_sync', False):
            results['anomalies'].append('Audio-video desynchronization detected')
        
        consistency_result = check_audio_consistency(audio_path)
        results['audio_consistency'] = consistency_result.get('score', 0.0)
        
        if consistency_result.get('inconsistent', False):
            results['anomalies'].append('Audio quality inconsistencies')
        
        results['score'] = (
            results['voice_deepfake_score'] * 0.5 +
            results['lip_sync_score'] * 0.3 +
            results['audio_consistency'] * 0.2
        )
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return results
        
    except Exception as e:
        print(f"Audio analysis error: {e}")
        return {
            'has_audio': False,
            'score': 0.5,
            'error': str(e)
        }


def check_audio_presence(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        has_audio = cap.get(cv2.CAP_PROP_AUDIO_STREAM) >= 0
        
        cap.release()
        
        if not has_audio:
            has_audio = check_audio_with_ffprobe(video_path)
        
        return has_audio
        
    except Exception as e:
        return check_audio_with_ffprobe(video_path)


def check_audio_with_ffprobe(video_path):
    try:
        cmd = [
            FFPROBE_PATH,
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_type',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=10, 
            check=False,
            shell=True
        )
        return 'audio' in result.stdout.lower()
        
    except Exception as e:
        print(f"Audio presence check error: {e}")
        return False


def extract_audio(video_path):
    try:
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        audio_path = temp_audio.name
        temp_audio.close()
        
        cmd = [
            FFMPEG_PATH,
            '-i', video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',
            audio_path
        ]
        
        result = subprocess.run(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            timeout=60,
            check=False,
            shell=True
        )
        
        if result.returncode == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            return audio_path
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return None
        
    except Exception as e:
        print(f"Audio extraction error: {e}")
        if 'audio_path' in locals() and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass
        return None


def detect_voice_deepfake(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        
        if len(y) < sr:
            return {'score': 0.5, 'reason': 'Audio too short'}
        
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        
        mel_variance = np.var(mel_spec_db)
        mfcc_variance = np.var(mfccs)
        
        suspicious = False
        score = 0.0
        
        if mel_variance < 100:
            suspicious = True
            score += 0.3
        
        if mfcc_variance < 5:
            suspicious = True
            score += 0.3
        
        high_freq_energy = np.mean(mel_spec_db[-20:, :])
        if high_freq_energy > -10:
            suspicious = True
            score += 0.2
        
        zcr_std = np.std(zero_crossing_rate)
        if zcr_std < 0.01:
            suspicious = True
            score += 0.2
        
        return {
            'score': min(score, 1.0),
            'suspicious': suspicious,
            'mel_variance': float(mel_variance),
            'mfcc_variance': float(mfcc_variance)
        }
        
    except Exception as e:
        print(f"Voice deepfake detection error: {e}")
        return {'score': 0.5, 'error': str(e)}


def analyze_lip_sync(video_path, audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        
        audio_envelope = np.abs(librosa.stft(y))
        audio_envelope = np.mean(audio_envelope, axis=0)
        
        mouth_movements = extract_mouth_movements(video_path)
        
        if mouth_movements is None or len(mouth_movements) == 0:
            return {'score': 0.0, 'reason': 'Could not track mouth'}
        
        from scipy import signal as scipy_signal
        
        target_len = min(len(audio_envelope), len(mouth_movements))
        
        audio_resampled = scipy_signal.resample(audio_envelope, target_len)
        mouth_resampled = scipy_signal.resample(mouth_movements, target_len)
        
        correlation = np.correlate(audio_resampled, mouth_resampled, mode='same')
        max_corr = np.max(np.abs(correlation))
        
        lag = np.argmax(np.abs(correlation)) - len(correlation) // 2
        lag_ms = (lag / sr) * 1000
        
        out_of_sync = abs(lag_ms) > 200 or max_corr < 0.3
        score = 0.0
        
        if abs(lag_ms) > 200:
            score += 0.5
        elif abs(lag_ms) > 100:
            score += 0.3
        
        if max_corr < 0.3:
            score += 0.5
        
        return {
            'score': min(score, 1.0),
            'out_of_sync': out_of_sync,
            'lag_ms': float(lag_ms),
            'correlation': float(max_corr)
        }
        
    except Exception as e:
        print(f"Lip sync analysis error: {e}")
        return {'score': 0.0, 'error': str(e)}


def extract_mouth_movements(video_path):
    try:
        return extract_mouth_movements_opencv(video_path)
        
    except Exception as e:
        print(f"Mouth movement extraction error: {e}")
        return []


def extract_mouth_movements_opencv(video_path):
    try:
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(face_cascade_path):
            print("Face cascade file not found")
            return extract_mouth_movements_simple(video_path)
        
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        
        mouth_cascade_path = os.path.join(MODELS_CACHE_DIR, 'haarcascade_mcs_mouth.xml')
        if not os.path.exists(mouth_cascade_path):
            mouth_cascade_path = cv2.data.haarcascades + 'haarcascade_mcs_mouth.xml'
        
        use_mouth_cascade = os.path.exists(mouth_cascade_path)
        
        if use_mouth_cascade:
            mouth_cascade = cv2.CascadeClassifier(mouth_cascade_path)
            if mouth_cascade.empty():
                use_mouth_cascade = False
        
        cap = cv2.VideoCapture(video_path)
        mouth_openness = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(100, 100))
            
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                
                if use_mouth_cascade:
                    face_roi = gray[y+h//2:y+h, x:x+w]
                    
                    mouths = mouth_cascade.detectMultiScale(face_roi, 1.3, 5, minSize=(30, 20))
                    
                    if len(mouths) > 0:
                        mx, my, mw, mh = max(mouths, key=lambda m: m[2] * m[3])
                        openness = mh / h
                        mouth_openness.append(openness)
                    else:
                        mouth_openness.append(0)
                else:
                    mouth_roi = gray[y+int(h*0.6):y+h, x+int(w*0.25):x+int(w*0.75)]
                    if mouth_roi.size > 0:
                        variance = np.var(mouth_roi)
                        mouth_openness.append(float(variance) / 1000.0)
                    else:
                        mouth_openness.append(0)
            else:
                mouth_openness.append(0)
        
        cap.release()
        
        if len(mouth_openness) > 0:
            return np.array(mouth_openness)
        else:
            return extract_mouth_movements_simple(video_path)
        
    except Exception as e:
        print(f"OpenCV mouth movement extraction error: {e}")
        return extract_mouth_movements_simple(video_path)


def extract_mouth_movements_simple(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        movements = []
        prev_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            h, w = gray.shape
            mouth_region = gray[int(h*0.5):int(h*0.8), int(w*0.3):int(w*0.7)]
            
            if prev_frame is not None:
                diff = cv2.absdiff(prev_frame, mouth_region)
                movement = np.mean(diff)
                movements.append(movement)
            
            prev_frame = mouth_region.copy()
        
        cap.release()
        return np.array(movements) if movements else np.array([])
        
    except Exception as e:
        print(f"Simple mouth movement extraction error: {e}")
        return np.array([])


def check_audio_consistency(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        
        segment_duration = 2.0
        segment_samples = int(segment_duration * sr)
        
        num_segments = len(y) // segment_samples
        
        if num_segments < 2:
            return {'score': 0.0, 'reason': 'Audio too short'}
        
        segment_features = []
        
        for i in range(num_segments):
            start = i * segment_samples
            end = start + segment_samples
            segment = y[start:end]
            
            rms = librosa.feature.rms(y=segment)[0]
            spectral_centroid = librosa.feature.spectral_centroid(y=segment, sr=sr)[0]
            
            segment_features.append({
                'rms_mean': np.mean(rms),
                'spectral_centroid_mean': np.mean(spectral_centroid)
            })
        
        rms_values = [s['rms_mean'] for s in segment_features]
        spectral_values = [s['spectral_centroid_mean'] for s in segment_features]
        
        rms_variance = np.var(rms_values)
        spectral_variance = np.var(spectral_values)
        
        inconsistent = rms_variance > 0.01 or spectral_variance > 500000
        
        score = 0.0
        if rms_variance > 0.01:
            score += 0.5
        if spectral_variance > 500000:
            score += 0.5
        
        return {
            'score': min(score, 1.0),
            'inconsistent': inconsistent,
            'rms_variance': float(rms_variance),
            'spectral_variance': float(spectral_variance)
        }
        
    except Exception as e:
        print(f"Audio consistency check error: {e}")
        return {'score': 0.0, 'error': str(e)}
