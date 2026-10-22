"""
Module 01: Cohort Intake & Segmentation (Top of Funnel)
Automates ingestion, data validation, and academic track segmentation for ~450 student teams.
Tracks:
  - 2nd Semester: Innovación (Feria de Prototipos)
  - 4th Semester: Emprendimiento (Business Model Canvas - BMC)
"""

import json
import logging
from typing import List, Dict, Any, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("IntakeValidator")

REQUIRED_BASE_FIELDS = ["team_id", "team_name", "semester", "project_title", "video_pitch_url"]
REQUIRED_2ND_SEM_FIELDS = ["prototype_type", "prototype_description", "target_user"]
REQUIRED_4TH_SEM_FIELDS = ["value_proposition", "customer_segments", "revenue_streams", "cost_structure"]


def validate_team_submission(team: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a single team submission against required schema based on semester track."""
    errors = []
    
    # Check base fields
    for field in REQUIRED_BASE_FIELDS:
        val = team.get(field)
        if not val or (isinstance(val, str) and not val.strip()):
            errors.append(f"Missing required base field: '{field}'")
            
    semester = team.get("semester")
    if semester not in [2, 4]:
        errors.append(f"Invalid semester: {semester}. Must be 2 (Innovación) or 4 (Emprendimiento).")
        return False, errors

    # Check track-specific fields
    if semester == 2:
        for field in REQUIRED_2ND_SEM_FIELDS:
            if not team.get(field):
                errors.append(f"2nd Sem Track Missing Field: '{field}' (Required for Feria de Prototipos)")
    elif semester == 4:
        for field in REQUIRED_4TH_SEM_FIELDS:
            if not team.get(field):
                errors.append(f"4th Sem Track Missing Field: '{field}' (Required for Business Model Canvas)")

    # Video pitch check (basic URL validation)
    pitch_url = team.get("video_pitch_url", "")
    if not (pitch_url.startswith("http://") or pitch_url.startswith("https://")):
        errors.append("Invalid 'video_pitch_url': Must be a valid HTTP/HTTPS link (e.g., YouTube/Loom/Drive).")

    is_valid = len(errors) == 0
    return is_valid, errors


def process_cohort_intake(raw_teams_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ingest and segment a raw cohort of student submissions."""
    logger.info(f"Processing intake for {len(raw_teams_data)} submitted teams...")

    track_2nd_sem = []
    track_4th_sem = []
    rejected_submissions = []

    for team in raw_teams_data:
        is_valid, errors = validate_team_submission(team)
        if not is_valid:
            rejected_submissions.append({
                "team_id": team.get("team_id", "UNKNOWN"),
                "team_name": team.get("team_name", "UNKNOWN"),
                "errors": errors,
                "raw_data": team
            })
            continue

        semester = team.get("semester")
        normalized_team = {
            "team_id": team["team_id"],
            "team_name": team["team_name"],
            "semester": semester,
            "track": "Innovación (Prototipos)" if semester == 2 else "Emprendimiento (BMC)",
            "project_title": team["project_title"],
            "pitch_url": team["video_pitch_url"],
            "members": team.get("members", []),
            "metadata": team
        }

        if semester == 2:
            track_2nd_sem.append(normalized_team)
        else:
            track_4th_sem.append(normalized_team)

    total_valid = len(track_2nd_sem) + len(track_4th_sem)
    logger.info(f"Intake Completed:")
    logger.info(f"  -> Total Validated: {total_valid}")
    logger.info(f"  -> 2nd Sem (Innovación/Prototipos): {len(track_2nd_sem)} teams")
    logger.info(f"  -> 4th Sem (Emprendimiento/BMC): {len(track_4th_sem)} teams")
    logger.info(f"  -> Rejected / Incomplete Submissions: {len(rejected_submissions)}")

    return {
        "valid_count": total_valid,
        "track_2nd_sem": track_2nd_sem,
        "track_4th_sem": track_4th_sem,
        "rejected": rejected_submissions
    }


if __name__ == "__main__":
    # Self-test with sample mock payload
    test_teams = [
        {
            "team_id": "ANH-001",
            "team_name": "AgroYucatán",
            "semester": 4,
            "project_title": "Optimización de Riego con IoT para Productores Cítricos",
            "video_pitch_url": "https://youtu.be/sample_pitch_1",
            "value_proposition": "Ahorro del 40% de agua mediante sensores de humedad accesibles.",
            "customer_segments": "Agricultores medianos en la zona sur de Yucatán.",
            "revenue_streams": "Venta de kit IoT ($3,500 MXN) + suscripción mensual de alertas ($250 MXN).",
            "cost_structure": "Fabricación de hardware, soporte en campo, hosting AWS."
        },
        {
            "team_id": "ANH-002",
            "team_name": "EcoBlock Mayab",
            "semester": 2,
            "project_title": "Ladrillos Ecológicos a partir de Sargazo y Cal Yucateca",
            "video_pitch_url": "https://youtu.be/sample_pitch_2",
            "prototype_type": "Prototipo Físico (Nivel TRL 3)",
            "prototype_description": "Bloque de construcción comprimido con 30% biomasa de sargazo tratado.",
            "target_user": "Constructoras sustentables y vivienda social en Quintana Roo y Yucatán."
        }
    ]

    result = process_cohort_intake(test_teams)
    print("\nSample Output Summary:")
    print(json.dumps({
        "valid_count": result["valid_count"],
        "2nd_sem_count": len(result["track_2nd_sem"]),
        "4th_sem_count": len(result["track_4th_sem"])
    }, indent=2))
