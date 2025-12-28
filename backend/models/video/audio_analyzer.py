"""
Audio Deepfake Analyzer - LAYER 2B
Analyzes audio stream for voice deepfakes and lip-sync issues
"""
import cv2
import numpy as np
import librosa
import subprocess
import os
import tempfile


def analyze_audio_stream(video_path):
    """
    Comprehensive audio analysis
    
    Returns:
        dict: {
            'has_audio': bool,
            'score': float (0-1, higher = more suspicious),
            'voice_deepfake_score': float,
            'lip_sync_score': float,
            'audio_consistency': float
        }
    """
    try:
        # Check if video has audio
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
        
        # Extract audio
        audio_path = extract_audio(video_path)
        
        if not audio_path:
            return {
                'has_audio': True,
                'score': 0.5,
                'error': 'Could not extract audio'
            }
        
        # 1. Voice Deepfake Detection
        voice_result = detect_voice_deepfake(audio_path)
        results['voice_deepfake_score'] = voice_result.get('score', 0.5)
        
        if voice_result.get('suspicious', False):
            results['anomalies'].append('Suspicious voice patterns detected')
        
        # 2. Lip-Sync Analysis
        lip_sync_result = analyze_lip_sync(video_path, audio_path)
        results['lip_sync_score'] = lip_sync_result.get('score', 0.0)
        
        if lip_sync_result.get('out_of_sync', False):
            results['anomalies'].append('Audio-video desynchronization detected')
        
        # 3. Audio Consistency
        consistency_result = check_audio_consistency(audio_path)
        results['audio_consistency'] = consistency_result.get('score', 0.0)
        
        if consistency_result.get('inconsistent', False):
            results['anomalies'].append('Audio quality inconsistencies')
        
        # Calculate overall score
        results['score'] = (
            results['voice_deepfake_score'] * 0.5 +
            results['lip_sync_score'] * 0.3 +
            results['audio_consistency'] * 0.2
        )
        
        # Cleanup
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
    """Check if video has audio track"""
    try:
        ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
        ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe")
        
        cmd = [
            ffprobe_path,
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_type',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return 'audio' in result.stdout.lower()
        
    except Exception as e:
        print(f"Audio presence check error: {e}")
        return False


def extract_audio(video_path):
    """Extract audio from video"""
    try:
        ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
        
        # Create temp audio file
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        audio_path = temp_audio.name
        temp_audio.close()
        
        cmd = [
            ffmpeg_path,
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM audio
            '-ar', '16000',  # Sample rate
            '-ac', '1',  # Mono
            audio_path
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60, check=True)
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            return audio_path
        
        return None
        
    except Exception as e:
        print(f"Audio extraction error: {e}")
        return None


def detect_voice_deepfake(audio_path):
    """
    Detect voice deepfakes using spectrogram analysis
    (Simplified version - full implementation would use RawNet2/AASIST)
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=16000)
        
        if len(y) < sr:  # Less than 1 second
            return {'score': 0.5, 'reason': 'Audio too short'}
        
        # Extract features
        # 1. Mel-spectrogram
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # 2. MFCC (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        
        # 3. Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        
        # Analyze patterns
        # AI-generated voices often have:
        # - More uniform spectral distribution
        # - Lower variance in features
        # - Unusual frequency artifacts
        
        # Check spectral consistency (too uniform = suspicious)
        mel_variance = np.var(mel_spec_db)
        mfcc_variance = np.var(mfccs)
        
        # Real voice: higher variance, AI voice: lower variance
        suspicious = False
        score = 0.0
        
        if mel_variance < 100:  # Too uniform
            suspicious = True
            score += 0.3
        
        if mfcc_variance < 5:  # Too consistent
            suspicious = True
            score += 0.3
        
        # Check for high-frequency artifacts
        high_freq_energy = np.mean(mel_spec_db[-20:, :])  # Top 20 mel bands
        if high_freq_energy > -10:  # Unusual high-frequency content
            suspicious = True
            score += 0.2
        
        # Check zero-crossing rate consistency
        zcr_std = np.std(zero_crossing_rate)
        if zcr_std < 0.01:  # Too consistent
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
    """
    Analyze lip-sync (correlation between mouth movement and audio)
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Get audio envelope (amplitude over time)
        audio_envelope = np.abs(librosa.stft(y))
        audio_envelope = np.mean(audio_envelope, axis=0)
        
        # Extract mouth movement from video
        mouth_movements = extract_mouth_movements(video_path)
        
        if not mouth_movements:
            return {'score': 0.0, 'reason': 'Could not track mouth'}
        
        # Resample to match lengths
        from scipy import signal as scipy_signal
        
        target_len = min(len(audio_envelope), len(mouth_movements))
        
        audio_resampled = scipy_signal.resample(audio_envelope, target_len)
        mouth_resampled = scipy_signal.resample(mouth_movements, target_len)
        
        # Calculate cross-correlation
        correlation = np.correlate(audio_resampled, mouth_resampled, mode='same')
        max_corr = np.max(np.abs(correlation))
        
        # Find time lag
        lag = np.argmax(np.abs(correlation)) - len(correlation) // 2
        lag_ms = (lag / sr) * 1000
        
        # Good sync: lag < 100ms, high correlation
        # Bad sync: lag > 200ms, low correlation
        
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
    """Extract mouth movement signal from video"""
    try:
        import mediapipe as mp
        
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5
        )
        
        cap = cv2.VideoCapture(video_path)
        
        mouth_openness = []
        
        # Mouth landmarks (upper and lower lip)
        upper_lip = 13
        lower_lip = 14
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                
                # Calculate mouth openness
                upper = landmarks.landmark[upper_lip]
                lower = landmarks.landmark[lower_lip]
                
                openness = abs(upper.y - lower.y)
                mouth_openness.append(openness)
            else:
                mouth_openness.append(0)
        
        cap.release()
        face_mesh.close()
        
        return np.array(mouth_openness)
        
    except Exception as e:
        print(f"Mouth movement extraction error: {e}")
        return []


def check_audio_consistency(audio_path):
    """Check audio quality consistency across time"""
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Split into segments
        segment_duration = 2.0  # 2 seconds
        segment_samples = int(segment_duration * sr)
        
        num_segments = len(y) // segment_samples
        
        if num_segments < 2:
            return {'score': 0.0, 'reason': 'Audio too short'}
        
        segment_features = []
        
        for i in range(num_segments):
            start = i * segment_samples
            end = start + segment_samples
            segment = y[start:end]
            
            # Extract features from segment
            rms = librosa.feature.rms(y=segment)[0]
            spectral_centroid = librosa.feature.spectral_centroid(y=segment, sr=sr)[0]
            
            segment_features.append({
                'rms_mean': np.mean(rms),
                'spectral_centroid_mean': np.mean(spectral_centroid)
            })
        
        # Check consistency
        rms_values = [s['rms_mean'] for s in segment_features]
        spectral_values = [s['spectral_centroid_mean'] for s in segment_features]
        
        rms_variance = np.var(rms_values)
        spectral_variance = np.var(spectral_values)
        
        # High variance = inconsistent quality (suspicious)
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
