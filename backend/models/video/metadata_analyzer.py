import cv2
import json
import subprocess
import os
from datetime import datetime


def analyze_video_metadata(video_path):
    try:
        results = {
            'score': 0.0,
            'suspicious_indicators': [],
            'metadata': {},
            'has_audio': False,
            'encoding_history': [],
            'frame_rate_consistent': True,
            'resolution_changes': False
        }
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {'score': 0.5, 'error': 'Cannot open video'}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec_str = "".join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])
        
        results['metadata'] = {
            'fps': fps,
            'frame_count': frame_count,
            'resolution': f"{width}x{height}",
            'codec': codec_str,
            'duration_seconds': frame_count / fps if fps > 0 else 0
        }
        
        cap.release()
        
        ffprobe_data = get_ffprobe_metadata(video_path)
        
        if ffprobe_data:
            results['metadata'].update(ffprobe_data)
            
            results['has_audio'] = ffprobe_data.get('has_audio', False)
            
            encoding_indicators = check_encoding_history(ffprobe_data)
            results['encoding_history'] = encoding_indicators
            
            if len(encoding_indicators) > 0:
                results['suspicious_indicators'].append('Multiple encoding passes detected')
                results['score'] += 0.3
            
            if 'variable_frame_rate' in ffprobe_data and ffprobe_data['variable_frame_rate']:
                results['suspicious_indicators'].append('Variable frame rate detected')
                results['frame_rate_consistent'] = False
                results['score'] += 0.2
            
            if 'resolution_changes' in ffprobe_data and ffprobe_data['resolution_changes']:
                results['suspicious_indicators'].append('Resolution changes mid-video')
                results['resolution_changes'] = True
                results['score'] += 0.4
            
            file_stats = os.stat(video_path)
            created_time = datetime.fromtimestamp(file_stats.st_ctime)
            modified_time = datetime.fromtimestamp(file_stats.st_mtime)
            
            if 'creation_time' in ffprobe_data:
                meta_creation = ffprobe_data['creation_time']
            
            if not ffprobe_data.get('encoder'):
                results['suspicious_indicators'].append('No encoder information')
                results['score'] += 0.15
        
        results['score'] = min(results['score'], 1.0)
        
        return results
        
    except Exception as e:
        print(f"Metadata analysis error: {e}")
        return {
            'score': 0.5,
            'error': str(e),
            'has_audio': False
        }


def get_ffprobe_metadata(video_path):
    try:
        ffprobe_path = None
        
        ffmpeg_path = os.getenv("FFMPEG_PATH")
        if ffmpeg_path:
            ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe")
        
        if not ffprobe_path or not os.path.exists(ffprobe_path):
            common_paths = [
                "ffprobe",
                "ffprobe.exe",
                r"C:\ffmpeg\bin\ffprobe.exe",
                r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
                r"C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe",
            ]
            
            for path in common_paths:
                try:
                    result = subprocess.run(
                        [path, "-version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=True
                    )
                    if result.returncode == 0:
                        ffprobe_path = path
                        break
                except:
                    continue
        
        if not ffprobe_path:
            print("FFprobe not found. Please install FFmpeg and add to PATH.")
            return None
        
        cmd = [
            ffprobe_path,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,
            shell=True
        )
        
        if result.returncode != 0:
            return None
        
        data = json.loads(result.stdout)
        
        metadata = {}
        
        if 'format' in data:
            fmt = data['format']
            metadata['duration'] = float(fmt.get('duration', 0))
            metadata['bit_rate'] = int(fmt.get('bit_rate', 0))
            metadata['format_name'] = fmt.get('format_name', '')
            
            if 'tags' in fmt:
                tags = fmt['tags']
                metadata['encoder'] = tags.get('encoder', '')
                metadata['creation_time'] = tags.get('creation_time', '')
        
        if 'streams' in data:
            video_streams = [s for s in data['streams'] if s['codec_type'] == 'video']
            audio_streams = [s for s in data['streams'] if s['codec_type'] == 'audio']
            
            metadata['has_audio'] = len(audio_streams) > 0
            metadata['num_audio_streams'] = len(audio_streams)
            metadata['num_video_streams'] = len(video_streams)
            
            if video_streams:
                vs = video_streams[0]
                metadata['video_codec'] = vs.get('codec_name', '')
                metadata['pix_fmt'] = vs.get('pix_fmt', '')
                
                avg_fps = vs.get('avg_frame_rate', '0/0')
                r_fps = vs.get('r_frame_rate', '0/0')
                
                if avg_fps != r_fps:
                    metadata['variable_frame_rate'] = True
        
        return metadata
        
    except Exception as e:
        print(f"FFprobe error: {e}")
        return None


def check_encoding_history(metadata):
    indicators = []
    
    bit_rate = metadata.get('bit_rate', 0)
    
    encoder = metadata.get('encoder', '').lower()
    
    if 'handbrake' in encoder or 'x264' in encoder:
        indicators.append('Re-encoded with video software')
    
    if metadata.get('num_video_streams', 1) > 1:
        indicators.append('Multiple video streams detected')
    
    return indicators


def check_audio_presence(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        cap.release()
        
        metadata = get_ffprobe_metadata(video_path)
        if metadata:
            return metadata.get('has_audio', False)
        
        return False
    except:
        return False
