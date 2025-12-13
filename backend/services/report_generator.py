def generate_report(
    media_type,
    fake_probability,
    risk_level,
    frames_analyzed=None
):
    """
    Deterministic, rule-based credibility report.
    No LLMs. No APIs. Fully explainable.
    """

    intro = (
        f"This {media_type} was analyzed using automated forensic techniques "
        f"designed to identify potential signs of digital manipulation."
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
            "synthetically generated media were detected. These indicators may "
            "include unnatural visual patterns, facial inconsistencies, or "
            "artifacts introduced during content generation or editing."
        )
    elif risk_level == "Medium":
        interpretation = (
            "Some indicators of potential manipulation were observed, "
            "but the evidence is not conclusive. The content should be treated "
            "with caution and verified using additional sources."
        )
    else:
        interpretation = (
            "No strong indicators of manipulation were detected during the analysis. "
            "However, this does not guarantee authenticity, as some sophisticated "
            "manipulations may evade automated detection."
        )

    limitation = (
        "This assessment is probabilistic in nature and should not be considered "
        "definitive proof of authenticity or manipulation. The results are intended "
        "to support journalistic and legal workflows and should be used alongside "
        "contextual analysis, source verification, and human judgment."
    )

    report = "\n\n".join([
        intro,
        findings,
        interpretation,
        limitation
    ])

    return report
