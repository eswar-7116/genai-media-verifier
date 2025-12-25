import numpy as np
from PIL import Image
import cv2
from scipy import fftpack
from utils.forensics_utils import convert_to_frequency_domain, apply_dct


def analyze_frequency_domain(image):
    """
    Main entry point for frequency domain analysis.
    Detects manipulation using FFT and DCT analysis with RGB channels.
    
    Returns:
        dict: {
            'score': float (0-1, higher = more likely fake),
            'fft_score': float,
            'dct_score': float,
            'high_freq_anomaly': bool
        }
    """
    try:
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            image = image.convert('RGB')
        
        fft_score = compute_fft_score_rgb(image)
        dct_score = compute_dct_score(image)
        high_freq_score = detect_high_frequency_anomalies(image)
        
        # Combine scores (boosted high_freq weight - it's most reliable)
        final_score = (fft_score * 0.35) + (dct_score * 0.35) + (high_freq_score * 0.30)
        
        return {
            'score': float(final_score),
            'fft_score': float(fft_score),
            'dct_score': float(dct_score),
            'high_freq_score': float(high_freq_score),
            'fft_anomaly': bool(fft_score > 0.6),
            'dct_anomaly': bool(dct_score > 0.6)
        }
    
    except Exception as e:
        print(f"Frequency analysis error: {e}")
        return {
            'score': 0.5,
            'fft_score': 0.5,
            'dct_score': 0.5,
            'high_freq_score': 0.5,
            'fft_anomaly': False,
            'dct_anomaly': False,
            'error': str(e)
        }


def compute_fft_score_rgb(image):
    """
    Analyze image using Fast Fourier Transform on RGB channels separately.
    AI-generated images have distinct frequency patterns in color channels.
    """
    img_array = np.array(image)
    
    channel_scores = []
    channel_patterns = []
    
    # Analyze each RGB channel separately
    for channel_idx in range(3):
        channel = img_array[:, :, channel_idx]
        magnitude_spectrum = convert_to_frequency_domain(channel)
        
        h, w = magnitude_spectrum.shape
        center_h, center_w = h // 2, w // 2
        
        # Analyze frequency rings at multiple radii
        ring_energies = []
        radii = [10, 30, 50, 70, 90]
        
        for radius in radii:
            ring_mask = create_ring_mask(h, w, center_h, center_w, radius, thickness=10)
            ring_energy = np.sum(magnitude_spectrum * ring_mask)
            ring_energies.append(ring_energy)
        
        # Check for unnatural frequency patterns
        # Real images have smooth energy falloff, AI images have irregular patterns
        if len(ring_energies) > 1:
            energy_gradient = np.diff(ring_energies)
            energy_variance = np.std(energy_gradient) / (np.mean(ring_energies) + 1e-10)
            channel_score = min(energy_variance * 3.0, 1.0)
        else:
            channel_score = 0.5
        
        channel_scores.append(channel_score)
        
        # Store pattern for cross-channel analysis
        channel_patterns.append(ring_energies)
    
    # Analyze inter-channel consistency
    # Real photos have correlated RGB frequency patterns
    # AI images often have inconsistent patterns across channels
    channel_correlation = np.corrcoef(channel_patterns)
    avg_correlation = np.mean([channel_correlation[0,1], channel_correlation[0,2], channel_correlation[1,2]])
    
    # Low correlation = suspicious
    correlation_score = 1.0 - avg_correlation if avg_correlation > 0 else 0.7
    
    # Combine channel scores
    avg_channel_score = np.mean(channel_scores)
    channel_variance = np.var(channel_scores)
    
    # High variance between channels = suspicious
    final_score = (avg_channel_score * 0.5) + (correlation_score * 0.3) + (channel_variance * 5.0 * 0.2)
    
    return min(final_score, 1.0)


def create_ring_mask(h, w, center_h, center_w, radius, thickness=10):
    """Create ring mask for frequency analysis"""
    y, x = np.ogrid[:h, :w]
    dist = np.sqrt((x - center_w)**2 + (y - center_h)**2)
    mask = ((dist >= radius) & (dist < radius + thickness)).astype(float)
    return mask


def compute_fft_score(image):
    """
    Legacy grayscale FFT analysis (kept for compatibility)
    """
    img_array = np.array(image.convert('L'))
    magnitude_spectrum = convert_to_frequency_domain(img_array)
    
    h, w = magnitude_spectrum.shape
    center_h, center_w = h // 2, w // 2
    
    center_region = magnitude_spectrum[
        center_h-30:center_h+30,
        center_w-30:center_w+30
    ]
    
    outer_region = magnitude_spectrum.copy()
    outer_region[center_h-30:center_h+30, center_w-30:center_w+30] = 0
    
    center_energy = np.sum(center_region)
    outer_energy = np.sum(outer_region)
    
    ratio = outer_energy / (center_energy + 1e-10)
    score = min(ratio / 10.0, 1.0)
    
    return score


def compute_dct_score(image):
    """
    Analyze using Discrete Cosine Transform.
    Detects JPEG compression artifacts that differ in manipulated images.
    """
    img_array = np.array(image.convert('L'))
    
    # Apply DCT
    dct_coeffs = apply_dct(img_array)
    
    # Calculate statistics on DCT coefficients
    mean_coeff = np.mean(np.abs(dct_coeffs))
    std_coeff = np.std(dct_coeffs)
    
    # High-frequency DCT components
    h, w = dct_coeffs.shape
    high_freq_region = dct_coeffs[h//2:, w//2:]
    high_freq_energy = np.sum(np.abs(high_freq_region))
    
    total_energy = np.sum(np.abs(dct_coeffs))
    high_freq_ratio = high_freq_energy / (total_energy + 1e-10)
    
    # FIXED: Deepfakes have LESS high-frequency DCT energy (they're smoother)
    # Low high-freq ratio = suspicious (inverted from before)
    score = 1.0 - min(high_freq_ratio * 5.0, 1.0)
    
    return score


def detect_high_frequency_anomalies(image):
    """
    Detect abnormal high-frequency noise patterns.
    AI-generated images have characteristic noise signatures.
    """
    img_array = np.array(image.convert('L'))
    
    # Apply high-pass filter
    kernel = np.array([[-1, -1, -1],
                       [-1,  8, -1],
                       [-1, -1, -1]])
    
    high_pass = cv2.filter2D(img_array, -1, kernel)
    
    # Analyze high-frequency content
    high_freq_std = np.std(high_pass)
    high_freq_mean = np.mean(np.abs(high_pass))
    
    # Calculate noise statistics
    noise_level = high_freq_std / (high_freq_mean + 1e-10)
    
    # Fake images often have lower or inconsistent high-frequency noise
    score = 1.0 - min(noise_level / 50.0, 1.0)
    
    return score


def detect_compression_artifacts(image):
    """
    Detect inconsistent JPEG compression artifacts.
    Manipulated regions show different compression levels.
    """
    img_array = np.array(image.convert('L'))
    
    # Divide image into blocks (8x8 like JPEG)
    h, w = img_array.shape
    block_size = 8
    
    block_variances = []
    
    for i in range(0, h - block_size, block_size):
        for j in range(0, w - block_size, block_size):
            block = img_array[i:i+block_size, j:j+block_size]
            block_var = np.var(block)
            block_variances.append(block_var)
    
    # Check consistency of block variances
    variance_std = np.std(block_variances)
    variance_mean = np.mean(block_variances)
    
    inconsistency = variance_std / (variance_mean + 1e-10)
    
    score = min(inconsistency / 2.0, 1.0)
    
    return score
