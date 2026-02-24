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

executor = ThreadPoolExecutor(max_workers=2)

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
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    return True


@app.get("/")
async def root():
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
    try:
        validate_file(file, config.ALLOWED_IMAGE_EXTENSIONS)
        
        reset_progress_tracker()
        tracker = get_progress_tracker()
        
        path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        tracker.update("File uploaded successfully")
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            executor,
            analyze_image_comprehensive,
            path
        )
        
        if results is None or 'error' in results:
            error_msg = results.get('error', 'Analysis failed') if results else 'Analysis returned no results'
            raise HTTPException(status_code=500, detail=error_msg)
        
        report = generate_comprehensive_report(results)
        
        try:
            os.remove(path)
        except:
            pass
        
        response = {
            "final_score": round(results.get('final_score', 0.5), 3),
            "risk_level": results.get('risk_level', 'Unknown'),
            "confidence": round(results.get('confidence', 0.0), 3),
            "analysis_type": "comprehensive",
            "report": report
        }
        
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
    async def event_generator():
        tracker = get_progress_tracker()
        message_queue = Queue()
        last_heartbeat = time.time()
        max_idle_time = 30
        
        def callback(message):
            try:
                message_queue.put(message)
            except Exception as e:
                print(f"Callback error: {e}")
        
        tracker.add_callback(callback)
        
        try:
            while True:
                try:
                    if not message_queue.empty():
                        message = message_queue.get_nowait()
                        data = json.dumps({'message': message})
                        yield f"data: {data}\n\n"
                        last_heartbeat = time.time()
                    else:
                        current_time = time.time()
                        if current_time - last_heartbeat > max_idle_time:
                            print(f"SSE connection idle for {max_idle_time}s, closing...")
                            break
                        
                        if current_time - last_heartbeat > 15:
                            yield f": heartbeat\n\n"
                            last_heartbeat = current_time
                        
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    print(f"SSE error: {e}")
                    await asyncio.sleep(0.1)
                    
        except (asyncio.CancelledError, GeneratorExit) as e:
            print(f"SSE connection closed: {type(e).__name__}")
        finally:
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
    try:
        validate_file(file, config.ALLOWED_VIDEO_EXTENSIONS)
        
        video_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = analyze_video(video_path)
        
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


@app.post("/analyze/video/quick")
async def analyze_video_quick_endpoint(file: UploadFile = File(...)):
    try:
        validate_file(file, config.ALLOWED_VIDEO_EXTENSIONS)
        
        reset_progress_tracker()
        tracker = get_progress_tracker()
        
        video_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        tracker.update("File uploaded successfully")
        
        from models.video.quick_detector import analyze_video_quick
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            executor,
            analyze_video_quick,
            video_path
        )
        
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
        
        if results is None:
            raise HTTPException(status_code=500, detail="Analysis returned no results")
            
        if 'error' in results:
            raise HTTPException(status_code=500, detail=results['error'])
        
        response = {
            "final_score": round(results.get('final_score', 0.5), 3),
            "risk_level": results.get('risk_level', 'Unknown'),
            "confidence": round(results.get('confidence', 0.0), 3),
            "analysis_type": "quick",
            "method_breakdown": results.get('method_breakdown', {}),
            "warning": "Quick analysis - some detection layers were skipped for speed"
        }
        
        response["layer_summaries"] = {}
        
        if results.get('layer1_metadata'):
            meta = results['layer1_metadata']
            response["layer_summaries"]["metadata"] = {
                "score": round(meta.get('score', 0), 3),
                "has_audio": meta.get('has_audio', False)
            }
        
        response["layer_summaries"]["visual"] = {}
        
        if results.get('layer2a_frame_based'):
            frame = results['layer2a_frame_based']
            response["layer_summaries"]["visual"]["frame_based"] = {
                "ensemble_avg": round(frame.get('avg_ensemble', 0), 3),
                "ensemble_max": round(frame.get('max_ensemble', 0), 3),
                "face_avg": round(frame.get('avg_face', 0), 3)
            }
        
        if results.get('layer2a_temporal'):
            temp = results['layer2a_temporal']
            response["layer_summaries"]["visual"]["temporal"] = {
                "score": round(temp.get('score', 0), 3),
                "identity_shifts": temp.get('identity_shifts', 0)
            }
        
        if results.get('layer2a_3d_video'):
            video3d = results['layer2a_3d_video']
            response["layer_summaries"]["visual"]["3d_model"] = {
                "score": round(video3d.get('score', 0), 3)
            }
        
        if results.get('layer2b_audio'):
            audio = results['layer2b_audio']
            if audio.get('has_audio'):
                response["layer_summaries"]["audio"] = {
                    "score": round(audio.get('score', 0), 3)
                }
            else:
                response["layer_summaries"]["audio"] = {"present": False}
        
        tracker.update("Quick analysis complete!")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quick video analysis failed: {str(e)}")


@app.post("/analyze/video/comprehensive")
async def analyze_video_comprehensive_endpoint(file: UploadFile = File(...)):
    try:
        validate_file(file, config.ALLOWED_VIDEO_EXTENSIONS)
        
        reset_progress_tracker()
        tracker = get_progress_tracker()
        
        video_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        tracker.update("File uploaded successfully")
        
        from models.video.comprehensive_detector import analyze_video_comprehensive
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            executor,
            analyze_video_comprehensive,
            video_path
        )
        
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
        
        if results is None:
            raise HTTPException(status_code=500, detail="Analysis returned no results")
            
        if 'error' in results:
            raise HTTPException(status_code=500, detail=results['error'])
        
        response = {
            "final_score": round(results.get('final_score', 0.5), 3),
            "risk_level": results.get('risk_level', 'Unknown'),
            "confidence": round(results.get('confidence', 0.0), 3),
            "analysis_type": "comprehensive_hybrid",
            "method_breakdown": results.get('method_breakdown', {})
        }
        
        response["layer_summaries"] = {}
        
        if results.get('layer1_metadata'):
            meta = results['layer1_metadata']
            response["layer_summaries"]["metadata"] = {
                "score": round(meta.get('score', 0), 3),
                "has_audio": meta.get('has_audio', False),
                "suspicious_indicators": meta.get('suspicious_indicators', [])
            }
        
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
        
        if results.get('layer2d_physics'):
            physics = results['layer2d_physics']
            response["layer_summaries"]["physics"] = {
                "score": round(physics.get('score', 0), 3),
                "lighting_consistent": physics.get('lighting_consistent', True),
                "depth_plausible": physics.get('depth_plausible', True),
                "anomalies": physics.get('anomalies', [])
            }
        
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
    print("Initializing deepfake detection system...")
    print(f"Device: {config.MODEL_CONFIG['device']}")
    print(f"Features enabled:")
    print(f"  - Neural Ensemble: {config.NEURAL_ENSEMBLE_ENABLED}")
    print(f"  - Frequency Analysis: {config.FREQUENCY_ANALYSIS_ENABLED}")
    print(f"  - Face Analysis: {config.FACE_ANALYSIS_ENABLED}")
    print(f"  - Metadata Analysis: {config.METADATA_ANALYSIS_ENABLED}")
    print(f"  - Hybrid Video Detection: Available (Layer 1 + 2)")
    
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
    
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    uvicorn.run(
        app, 
        host=host, 
        port=port, 
        reload=reload,
        reload_excludes=["models_cache/*", "uploads/*", "temp/*", "__pycache__/*"]
    )
