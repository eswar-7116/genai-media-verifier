from services.video_analyzer import analyze_video
from services.report_generator import generate_report, generate_comprehensive_report
from services.comprehensive_analyzer import analyze_image_comprehensive
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import asyncio
import json
from queue import Queue
import threading
from concurrent.futures import ThreadPoolExecutor
import time

from utils.image_utils import preprocess_image
from models.deepfake_detector import predict_image
from models.progress_tracker import get_progress_tracker, reset_progress_tracker
import config


app = FastAPI(title="Deepfake Detection API", version="2.0")

# Thread pool for running heavy analysis without blocking SSE
executor = ThreadPoolExecutor(max_workers=2)

# Enable CORS for frontend - using config from environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

UPLOAD_DIR = config.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_file(file: UploadFile, allowed_extensions: set):
    """Validate file type and size"""
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    return True


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Deepfake Detection API",
        "version": "2.0",
        "endpoints": {
            "health": "/health",
            "quick_image_analysis": "/analyze/image",
            "comprehensive_image_analysis": "/analyze/image/comprehensive",
            "simple_video_analysis": "/analyze/video",
            "comprehensive_video_analysis": "/analyze/video/comprehensive"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "features": {
            "neural_ensemble": config.NEURAL_ENSEMBLE_ENABLED,
            "frequency_analysis": config.FREQUENCY_ANALYSIS_ENABLED,
            "face_analysis": config.FACE_ANALYSIS_ENABLED,
            "metadata_analysis": config.METADATA_ANALYSIS_ENABLED
        }
    }


@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Quick image analysis using single neural network.
    Faster but less comprehensive than /analyze/image/comprehensive
    """
    try:
        validate_file(file, config.ALLOWED_IMAGE_EXTENSIONS)
        
        path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        image = preprocess_image(path)
        fake_prob = predict_image(image)
        
        if fake_prob > config.RISK_THRESHOLDS['high']:
            risk = "High"
        elif fake_prob > config.RISK_THRESHOLDS['medium']:
            risk = "Medium"
        else:
            risk = "Low"
        
        report = generate_report(
            media_type="image",
            fake_probability=fake_prob,
            risk_level=risk
        )
        
        # Cleanup
        try:
            os.remove(path)
        except:
            pass
        
        return {
            "fake_probability": round(fake_prob, 2),
            "risk_level": risk,
            "report": report,
            "analysis_type": "quick"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/image/comprehensive")
async def analyze_image_comprehensive_endpoint(file: UploadFile = File(...)):
    """
    Comprehensive image analysis using all detection methods:
    - Neural network ensemble (multiple models)
    - Frequency domain analysis (FFT/DCT)
    - Facial analysis (landmarks, symmetry, texture)
    - Metadata forensics (EXIF, ELA)
    
    Slower but more accurate and robust.
    """
    try:
        validate_file(file, config.ALLOWED_IMAGE_EXTENSIONS)
        
        # Reset progress tracker for new analysis
        reset_progress_tracker()
        tracker = get_progress_tracker()
        
        path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        tracker.update("File uploaded successfully")
        
        # Run comprehensive analysis in background thread to not block SSE
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            executor,
            analyze_image_comprehensive,
            path
        )
        
        # Check for errors
        if results is None or 'error' in results:
            error_msg = results.get('error', 'Analysis failed') if results else 'Analysis returned no results'
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Generate detailed report
        report = generate_comprehensive_report(results)
        
        # Cleanup
        try:
            os.remove(path)
        except:
            pass
        
        # Build response with safe defaults
        response = {
            "final_score": round(results.get('final_score', 0.5), 3),
            "risk_level": results.get('risk_level', 'Unknown'),
            "confidence": round(results.get('confidence', 0.0), 3),
            "analysis_type": "comprehensive",
            "report": report
        }
        
        # Add detailed breakdown if enabled
        if config.ENABLE_DETAILED_BREAKDOWN:
            response["analysis_breakdown"] = {
                "neural_network": results.get('neural_network'),
                "frequency_domain": results.get('frequency_domain'),
                "facial_analysis": results.get('facial_analysis'),
                "metadata_forensics": results.get('metadata_forensics')
            }
        
        tracker.update("Complete!")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")


@app.get("/analyze/progress")
async def get_analysis_progress():
    """
    Server-Sent Events endpoint for real-time progress updates
    IMPROVED: Better error handling and connection stability
    """
    async def event_generator():
        tracker = get_progress_tracker()
        message_queue = Queue()
        last_heartbeat = time.time()
        
        def callback(message):
            try:
                message_queue.put(message)
            except Exception as e:
                print(f"Callback error: {e}")
        
        tracker.add_callback(callback)
        
        try:
            while True:
                try:
                    # Check for new messages with timeout
                    if not message_queue.empty():
                        message = message_queue.get_nowait()
                        data = json.dumps({'message': message})
                        yield f"data: {data}\n\n"
                        last_heartbeat = time.time()
                    else:
                        # Send heartbeat every 15 seconds to keep connection alive
                        current_time = time.time()
                        if current_time - last_heartbeat > 15:
                            yield f": heartbeat\n\n"
                            last_heartbeat = current_time
                        
                        # Small sleep to prevent CPU spinning
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    print(f"SSE error: {e}")
                    await asyncio.sleep(0.1)
                    
        except (asyncio.CancelledError, GeneratorExit) as e:
            # Client disconnected - clean up gracefully
            print(f"SSE connection closed: {type(e).__name__}")
        finally:
            # Always try to remove callback on exit
            try:
                if callback in tracker.callbacks:
                    tracker.callbacks.remove(callback)
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


@app.post("/analyze/video")
async def analyze_video_endpoint(file: UploadFile = File(...)):
    """
    OLD Simple video analysis (frame-by-frame only).
    Use /analyze/video/comprehensive for full hybrid detection.
    """
    try:
        validate_file(file, config.ALLOWED_VIDEO_EXTENSIONS)
        
        video_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = analyze_video(video_path)
        
        # Cleanup
        try:
            os.remove(video_path)
        except:
            pass
        
        if result is None:
            raise HTTPException(status_code=400, detail="No frames could be analyzed")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")


@app.post("/analyze/video/comprehensive")
async def analyze_video_comprehensive_endpoint(file: UploadFile = File(...)):
    """
    Comprehensive HYBRID video deepfake detection:
    
    LAYER 1 - Pre-Analysis:
    - Metadata forensics (encoding, frame rate, resolution)
    - Audio presence check
    
    LAYER 2 - Multi-Modal Analysis:
    A. VISUAL STREAM (Hybrid):
       - Smart frame extraction (scene detection, faces, boundaries)
       - Frame-based ensemble analysis
       - Temporal consistency (landmark tracking, identity persistence)
       - 3D video model analysis (VideoMAE)
    
    B. AUDIO STREAM (if present):
       - Voice deepfake detection
       - Lip-sync analysis
       - Audio consistency checks
    
    C. PHYSIOLOGICAL SIGNALS:
       - Heartbeat detection (rPPG)
       - Blink pattern analysis
       - Breathing detection
    
    D. PHYSICS & CONSISTENCY:
       - Lighting consistency
       - Depth estimation (MiDaS)
       - Shadow analysis
    
    Returns detailed multi-modal analysis with high confidence scoring.
    """
    try:
        validate_file(file, config.ALLOWED_VIDEO_EXTENSIONS)
        
        # Reset progress tracker for new analysis
        reset_progress_tracker()
        tracker = get_progress_tracker()
        
        video_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Save uploaded file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        tracker.update("File uploaded successfully")
        
        # Import comprehensive detector
        from models.video.comprehensive_detector import analyze_video_comprehensive
        
        # Run full hybrid analysis in background thread to not block SSE
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            executor,
            analyze_video_comprehensive,
            video_path
        )
        
        # Cleanup uploaded file and temp frames
        try:
            os.remove(video_path)
        except:
            pass
        
        try:
            import shutil as sh
            if os.path.exists("temp_frames"):
                sh.rmtree("temp_frames")
        except:
            pass
        
        # Check for errors
        if results is None:
            raise HTTPException(status_code=500, detail="Analysis returned no results")
            
        if 'error' in results:
            raise HTTPException(status_code=500, detail=results['error'])
        
        # Build response with safe defaults
        response = {
            "final_score": round(results.get('final_score', 0.5), 3),
            "risk_level": results.get('risk_level', 'Unknown'),
            "confidence": round(results.get('confidence', 0.0), 3),
            "analysis_type": "comprehensive_hybrid",
            "method_breakdown": results.get('method_breakdown', {})
        }
        
        # Add layer summaries with safe gets
        response["layer_summaries"] = {}
        
        # Layer 1: Metadata
        if results.get('layer1_metadata'):
            meta = results['layer1_metadata']
            response["layer_summaries"]["metadata"] = {
                "score": round(meta.get('score', 0), 3),
                "has_audio": meta.get('has_audio', False),
                "suspicious_indicators": meta.get('suspicious_indicators', [])
            }
        
        # Layer 2A: Visual
        response["layer_summaries"]["visual"] = {}
        
        if results.get('layer2a_frame_based'):
            frame = results['layer2a_frame_based']
            response["layer_summaries"]["visual"]["frame_based"] = {
                "ensemble_avg": round(frame.get('avg_ensemble', 0), 3),
                "ensemble_max": round(frame.get('max_ensemble', 0), 3),
                "face_avg": round(frame.get('avg_face', 0), 3),
                "frequency_avg": round(frame.get('avg_frequency', 0), 3)
            }
        
        if results.get('layer2a_temporal'):
            temp = results['layer2a_temporal']
            response["layer_summaries"]["visual"]["temporal"] = {
                "score": round(temp.get('score', 0), 3),
                "identity_shifts": temp.get('identity_shifts', 0),
                "motion_smoothness": round(temp.get('motion_smoothness', 0), 3),
                "anomalies": temp.get('inconsistencies', [])
            }
        
        if results.get('layer2a_3d_video'):
            video3d = results['layer2a_3d_video']
            response["layer_summaries"]["visual"]["3d_model"] = {
                "score": round(video3d.get('score', 0), 3),
                "method": video3d.get('method', 'unknown')
            }
        
        # Layer 2B: Audio
        if results.get('layer2b_audio'):
            audio = results['layer2b_audio']
            if audio.get('has_audio'):
                response["layer_summaries"]["audio"] = {
                    "score": round(audio.get('score', 0), 3),
                    "voice_deepfake": round(audio.get('voice_deepfake_score', 0), 3),
                    "lip_sync": round(audio.get('lip_sync_score', 0), 3),
                    "anomalies": audio.get('anomalies', [])
                }
            else:
                response["layer_summaries"]["audio"] = {"present": False}
        
        # Layer 2C: Physiological
        if results.get('layer2c_physiological'):
            physio = results['layer2c_physiological']
            response["layer_summaries"]["physiological"] = {
                "score": round(physio.get('score', 0), 3),
                "heartbeat_detected": physio.get('heartbeat_detected', False),
                "heartbeat_bpm": physio.get('heartbeat_bpm', 0),
                "natural_blink_pattern": physio.get('blink_pattern_natural', False),
                "blink_count": physio.get('blink_count', 0),
                "anomalies": physio.get('anomalies', [])
            }
        
        # Layer 2D: Physics
        if results.get('layer2d_physics'):
            physics = results['layer2d_physics']
            response["layer_summaries"]["physics"] = {
                "score": round(physics.get('score', 0), 3),
                "lighting_consistent": physics.get('lighting_consistent', True),
                "depth_plausible": physics.get('depth_plausible', True),
                "anomalies": physics.get('anomalies', [])
            }
        
        # Layer 3: Specialized
        response["layer_summaries"]["specialized"] = {}
        
        if results.get('layer3_boundary'):
            boundary = results['layer3_boundary']
            response["layer_summaries"]["specialized"]["boundary"] = {
                "score": round(boundary.get('score', 0), 3),
                "suspicious_transitions": len(boundary.get('suspicious_transitions', [])),
                "quality_drops": boundary.get('quality_drops', 0)
            }
        
        if results.get('layer3_compression'):
            compression = results['layer3_compression']
            response["layer_summaries"]["specialized"]["compression"] = {
                "score": round(compression.get('score', 0), 3),
                "mismatches": compression.get('compression_mismatches', 0),
                "face_compression": round(compression.get('avg_face_compression', 0), 3),
                "background_compression": round(compression.get('avg_background_compression', 0), 3)
            }
        
        tracker.update("Analysis complete!")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Comprehensive video analysis failed: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    print("Initializing deepfake detection system...")
    print(f"Device: {config.MODEL_CONFIG['device']}")
    print(f"Features enabled:")
    print(f"  - Neural Ensemble: {config.NEURAL_ENSEMBLE_ENABLED}")
    print(f"  - Frequency Analysis: {config.FREQUENCY_ANALYSIS_ENABLED}")
    print(f"  - Face Analysis: {config.FACE_ANALYSIS_ENABLED}")
    print(f"  - Metadata Analysis: {config.METADATA_ANALYSIS_ENABLED}")
    print(f"  - Hybrid Video Detection: Available (Layer 1 + 2)")
    
    # Preload models
    if config.NEURAL_ENSEMBLE_ENABLED:
        from models.ensemble_detector import get_ensemble_detector
        get_ensemble_detector()
    
    if config.FACE_ANALYSIS_ENABLED:
        from models.face_analyzer import get_face_analyzer
        get_face_analyzer()
    
    print("\nVideo Detection Capabilities:")
    print("  - Smart frame extraction")
    print("  - Temporal consistency analysis")
    print("  - 3D video models (VideoMAE)")
    print("  - Audio deepfake detection")
    print("  - Physiological signals (heartbeat, blinks)")
    print("  - Physics consistency checks")
    
    print("\nSystem ready!")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
