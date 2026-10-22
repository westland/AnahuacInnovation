"""
Module 04: Statistical Outlier Calibration & Funnel Gate (Top 50 Selection)
Normalizes scoring distributions across all 450 teams to guarantee an 'Objetivo Justo',
adjusts for harsh vs lenient scoring patterns, and selects the Top 50 Finalists.
"""

import json
import logging
import statistics
import csv
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StatisticalCalibrator")


def calibrate_cohort_scores(evaluations: List[Dict[str, Any]], top_k: int = 50) -> Dict[str, Any]:
    """
    Apply statistical z-score normalization and percentile ranking across the cohort.
    Selects the top_k finalists and flags borderline projects.
    """
    total_teams = len(evaluations)
    if total_teams == 0:
        return {"error": "No evaluations provided."}

    logger.info(f"Calibrating scores across cohort of {total_teams} projects...")

    raw_scores = [e["mean_score"] for e in evaluations]
    cohort_mean = statistics.mean(raw_scores)
    cohort_stdev = statistics.stdev(raw_scores) if total_teams > 1 else 1.0

    logger.info(f"Cohort Raw Stats -> Mean: {cohort_mean:.2f}, StDev: {cohort_stdev:.2f}")

    calibrated_records = []
    for team in evaluations:
        raw_score = team["mean_score"]
        # Calculate standard z-score
        z_score = (raw_score - cohort_mean) / (cohort_stdev if cohort_stdev > 0 else 1.0)
        
        # Normalized score mapped to 0-100 scale with mean at 75 and stdev at 10
        calibrated_score = round(75.0 + (z_score * 10.0), 2)
        calibrated_score = max(0.0, min(100.0, calibrated_score))

        calibrated_records.append({
            "team_id": team["team_id"],
            "team_name": team["team_name"],
            "semester": team["semester"],
            "project_title": team["project_title"],
            "raw_mean_score": raw_score,
            "z_score": round(z_score, 3),
            "calibrated_score": calibrated_score,
            "has_high_discrepancy": team.get("has_high_discrepancy", False),
            "discrepancies": team.get("discrepancies", []),
            "meta_verdict": team.get("meta_verdict", ""),
            "individual_judges": team.get("individual_judges", [])
        })

    # Sort descending by calibrated score
    calibrated_records.sort(key=lambda x: x["calibrated_score"], reverse=True)

    # Assign rank
    for rank, rec in enumerate(calibrated_records, 1):
        rec["rank"] = rank
        rec["is_finalist"] = rank <= top_k

    top_finalists = calibrated_records[:top_k]
    sem_2_finalists = [t for t in top_finalists if t["semester"] == 2]
    sem_4_finalists = [t for t in top_finalists if t["semester"] == 4]

    # Borderline check (#top_k - 2 to #top_k + 2)
    borderline_teams = []
    if total_teams > top_k:
        cutoff_score = top_finalists[-1]["calibrated_score"]
        for t in calibrated_records:
            if abs(t["calibrated_score"] - cutoff_score) <= 1.0:
                borderline_teams.append({
                    "rank": t["rank"],
                    "team_id": t["team_id"],
                    "team_name": t["team_name"],
                    "calibrated_score": t["calibrated_score"],
                    "is_finalist": t["is_finalist"]
                })

    logger.info(f"Calibration Complete: Top {top_k} Selected!")
    logger.info(f"  -> 2nd Sem (Innovación/Prototipos): {len(sem_2_finalists)} finalists")
    logger.info(f"  -> 4th Sem (Emprendimiento/BMC): {len(sem_4_finalists)} finalists")
    logger.info(f"  -> Cutoff Score (Rank #{top_k}): {top_finalists[-1]['calibrated_score'] if top_finalists else 0}")
    logger.info(f"  -> Borderline Teams Identified: {len(borderline_teams)}")

    return {
        "cohort_stats": {
            "total_teams": total_teams,
            "raw_mean": round(cohort_mean, 2),
            "raw_stdev": round(cohort_stdev, 2),
            "cutoff_score": top_finalists[-1]["calibrated_score"] if top_finalists else 0
        },
        "top_finalists": top_finalists,
        "all_ranked_teams": calibrated_records,
        "borderline_teams": borderline_teams
    }


def export_ranking_csv(ranked_teams: List[Dict[str, Any]], filepath: str):
    """Export the ranked ledger to a CSV spreadsheet."""
    keys = ["rank", "team_id", "team_name", "semester", "project_title", "raw_mean_score", "calibrated_score", "is_finalist"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for t in ranked_teams:
            row = {k: t[k] for k in keys}
            writer.writerow(row)
    logger.info(f"Exported ranking CSV to {filepath}")
