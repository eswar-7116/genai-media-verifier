import warnings

def predict_image(image):
    warnings.warn(
        "predict_image from image_detector.py is deprecated. "
        "Use predict_ensemble from ensemble_detector.py instead.",
        DeprecationWarning
    )
    from models.ensemble_detector import predict_ensemble
    result = predict_ensemble(image)
    return result.get('score', 0.5)
