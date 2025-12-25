from services.video_analyzer import analyze_video
from services.report_generator import generate_report, generate_comprehensive_report
from services.comprehensive_analyzer import analyze_image_comprehensive
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil

from utils.image_utils import preprocess_image
from models.deepfake_detector import predict_image
import config


app = FastAPI(title="Deepfake Detection API", version="2.0")

UPLOAD_DIR = "uploads"
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
            "video_analysis": "/analyze/video"
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
        
        path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run comprehensive analysis
        results = analyze_image_comprehensive(path)
        
        # Generate detailed report
        report = generate_comprehensive_report(results)
        
        # Cleanup
        try:
            os.remove(path)
        except:
            pass
        
        # Build response
        response = {
            "final_score": round(results['final_score'], 3),
            "risk_level": results['risk_level'],
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
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")


@app.post("/analyze/video")
async def analyze_video_endpoint(file: UploadFile = File(...)):
    """
    Video analysis endpoint.
    Extracts frames and analyzes each frame.
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
    
    # Preload models
    if config.NEURAL_ENSEMBLE_ENABLED:
        from models.ensemble_detector import get_ensemble_detector
        get_ensemble_detector()
    
    if config.FACE_ANALYSIS_ENABLED:
        from models.face_analyzer import get_face_analyzer
        get_face_analyzer()
    
    print("System ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
