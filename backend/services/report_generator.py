def generate_report(
    media_type,
    fake_probability,
    risk_level,
    frames_analyzed=None,
    detailed_breakdown=None
):
    """
    Enhanced deterministic, rule-based credibility report.
    No LLMs. No APIs. Fully explainable.
    """

    intro = (
        f"This {media_type} was analyzed using a comprehensive multi-method "
        f"forensic analysis system designed to identify potential signs of "
        f"digital manipulation through neural networks, frequency domain analysis, "
        f"facial feature examination, and metadata forensics."
    )

    findings = (
        f"The system estimated a manipulation probability of "
        f"{round(fake_probability * 100, 1)}%, which corresponds to a "
        f"{risk_level.lower()} risk classification."
    )

    if media_type == "video" and frames_analyzed is not None:
        findings += (
            f" A total of {frames_analyzed} frames were examined to assess "
            f"visual consistency over time."
        )

    if risk_level == "High":
        interpretation = (
            "Multiple indicators commonly associated with manipulated or "
            "synthetically generated media were detected across different analysis methods. "
            "These indicators may include unnatural visual patterns, facial inconsistencies, "
            "frequency domain anomalies, metadata irregularities, or artifacts introduced "
            "during content generation or editing. The convergence of multiple detection "
            "methods increases confidence in this assessment."
        )
    elif risk_level == "Medium":
        interpretation = (
            "Some indicators of potential manipulation were observed in one or more "
            "analysis methods, but the evidence is not conclusive across all techniques. "
            "The content should be treated with caution and verified using additional "
            "sources. Further investigation is recommended, particularly focusing on "
            "contextual verification and source validation."
        )
    else:
        interpretation = (
            "No strong indicators of manipulation were detected during the multi-method analysis. "
            "The content passed checks across neural network detection, frequency analysis, "
            "facial examination, and metadata validation. However, this does not provide "
            "absolute guarantee of authenticity, as some sophisticated manipulations may "
            "evade automated detection systems."
        )

    # Add detailed breakdown if provided
    if detailed_breakdown:
        breakdown_section = (
            "\n\nDetailed Analysis Breakdown:\n"
            f"{detailed_breakdown}"
        )
    else:
        breakdown_section = ""

    limitation = (
        "This assessment is probabilistic in nature and should not be considered "
        "definitive proof of authenticity or manipulation. The multi-method approach "
        "increases detection accuracy but cannot guarantee perfect results. The findings "
        "are intended to support journalistic and legal workflows and should be used "
        "alongside contextual analysis, source verification, chain of custody validation, "
        "and human expert judgment."
    )

    report = "\n\n".join([
        intro,
        findings,
        interpretation,
        breakdown_section,
        limitation
    ])

    return report


def generate_comprehensive_report(analysis_results):
    """
    Generate report from comprehensive analysis results.
    
    Args:
        analysis_results: Dict containing all analysis results
    
    Returns:
        str: Formatted report
    """
    from services.comprehensive_analyzer import generate_detailed_breakdown
    
    final_score = analysis_results.get('final_score', 0.5)
    risk_level = analysis_results.get('risk_level', 'Unknown')
    
    breakdown = generate_detailed_breakdown(analysis_results)
    
    return generate_report(
        media_type="image",
        fake_probability=final_score,
        risk_level=risk_level,
        detailed_breakdown=breakdown
    )
