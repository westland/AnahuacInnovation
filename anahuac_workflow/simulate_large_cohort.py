"""
Simulate Full 450-Team Cohort for Anáhuac Mayab
Generates a full 450-team synthetic submission cohort, simulates the 5 Synthetic Judge scoring distributions
(incorporating realistic variance, strict vs lenient judges, and edge cases), runs the Statistical Calibrator,
selects the Top 50 Finalists, and exports the full audit ledger.
"""

import json
import random
import os
from typing import List
from importlib import import_module

calibrator_module = import_module("04_statistical_calibrator")

# Regional and theme keywords for realistic project generation
DOMAINS_2ND_SEM = [
    ("Sargazo y Biomateriales", "Prototipo de biomaterial / biopolímero compostable para envases y construcción."),
    ("IoT y Sensores Agrícolas", "Dispositivo mecatrónico de monitoreo de suelo y humedad en cítricos y hortalizas."),
    ("Energía Solar y Termodinámica", "Desalinizador / concentrador solar pasivo para zonas costeras."),
    ("Robótica y Automatización", "Vehículo robótico autónomo para limpieza de cenotes o clasificación de residuos."),
    ("Biotecnología Melipona", "Monitoreo acústico y térmico de colmenas de abeja melipona maya."),
    ("Biofiltro de Aguas Residuales", "Filtro biológico con macroalgas y carbón activado de coco para cenotes.")
]

DOMAINS_4TH_SEM = [
    ("Agtech & Trazabilidad SaaS", "Plataforma SaaS con visión artificial para detección de plagas cítricas."),
    ("Logística de Frío para Pesca", "Red compartida de contenedores refrigerados solares para cooperativas pulperas."),
    ("Fintech & Microcréditos Mayas", "Scoring crediticio alternativo y microcréditos para artesanas por WhatsApp."),
    ("Economía Circular & Empaques", "Sustitución de plásticos de un solo uso por hojas de plátano termoformadas."),
    ("HealthTech Preventivo", "Kioscos de triaje metabólico infantil y gamificación nutricional escolar."),
    ("Turismo Regenerativo", "Plataforma de experiencias ecoturísticas comunitarias con reparto justo de ingresos.")
]


def generate_450_cohort(output_file: str = "cohort_450_teams.json") -> str:
    """Generate 450 synthetic student projects with 2nd and 4th semester distribution."""
    random.seed(42)
    cohort = []

    # ~225 teams 2nd Sem, ~225 teams 4th Sem
    for i in range(1, 451):
        semester = 2 if i <= 225 else 4
        track_prefix = "SEM2" if semester == 2 else "SEM4"
        team_id = f"ANH-{track_prefix}-{i:03d}"

        if semester == 2:
            domain, proto_desc = random.choice(DOMAINS_2ND_SEM)
            project_title = f"{domain} - Prototipo Fase {random.choice(['Alpha', 'Beta', 'TRL 3', 'TRL 4'])}"
            team = {
                "team_id": team_id,
                "team_name": f"Equipo {i:03d} ({domain.split()[0]})",
                "semester": 2,
                "project_title": project_title,
                "video_pitch_url": f"https://youtu.be/anahuac_{team_id.lower()}",
                "prototype_type": f"Prototipo Funcional TRL {random.choice([3, 4])}",
                "prototype_description": proto_desc,
                "target_user": "Comunidades rurales, cooperativas y empresas de la Península de Yucatán."
            }
        else:
            domain, val_prop = random.choice(DOMAINS_4TH_SEM)
            project_title = f"{domain} - Modelo Escalable"
            team = {
                "team_id": team_id,
                "team_name": f"Venture {i:03d} ({domain.split()[0]})",
                "semester": 4,
                "project_title": project_title,
                "video_pitch_url": f"https://youtu.be/anahuac_{team_id.lower()}",
                "value_proposition": val_prop,
                "customer_segments": "Mercado B2B y cooperativas regionales del sureste mexicano.",
                "revenue_streams": "Suscripción mensual recurrente ($350-$1,200 MXN) + comisión por transacción.",
                "cost_structure": "Desarrollo tecnológico, operaciones de campo, compliance y marketing digital."
            }
        cohort.append(team)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cohort, f, ensure_ascii=False, indent=2)

    return output_file


def simulate_450_evaluations(cohort_file: str) -> List[dict]:
    """Simulate 5-judge consensus scores for all 450 projects with realistic grading distributions."""
    random.seed(1337)
    with open(cohort_file, "r", encoding="utf-8") as f:
        cohort = json.load(f)

    evaluations = []
    judge_names = [
        "Dr. Fernando Ruiz (Finanzas)",
        "Mtra. Sofía Morales (Mercado)",
        "Ing. Carlos Méndez (Innovación)",
        "Lic. Valeria Garza (Pitch)",
        "Dr. Alejandro H. (Auditor)"
    ]

    for team in cohort:
        # Base venture quality score (Normal distribution centered at 72, std 11)
        base_quality = random.gauss(72, 11)
        base_quality = max(35.0, min(97.0, base_quality))

        individual_scores = []
        individual_judges = []

        for j_name in judge_names:
            # Different judge biases:
            # Finance judge is typically harsher (-3)
            # Innovation judge rewards novelty (+2)
            bias = -3.0 if "Finanzas" in j_name else (2.0 if "Innovación" in j_name else 0.0)
            noise = random.gauss(0, 4.5)
            j_score = round(max(20, min(100, base_quality + bias + noise)))
            individual_scores.append(j_score)
            individual_judges.append({
                "judge_name": j_name,
                "score": j_score,
                "feedback": f"Evaluación de rigor para {team['team_name']}. Calificación: {j_score}/100."
            })

        mean_s = round(sum(individual_scores) / len(individual_scores), 2)
        discrepancies = [
            {"judge": j["judge_name"], "score": j["score"], "delta": round(abs(j["score"] - mean_s), 2)}
            for j in individual_judges if abs(j["score"] - mean_s) > 15
        ]

        evaluations.append({
            "team_id": team["team_id"],
            "team_name": team["team_name"],
            "semester": team["semester"],
            "project_title": team["project_title"],
            "mean_score": mean_s,
            "has_high_discrepancy": len(discrepancies) > 0,
            "discrepancies": discrepancies,
            "individual_judges": individual_judges,
            "meta_verdict": f"Dictamen oficial colegiado para {team['team_name']} emitido por el jurado Anáhuac Mayab."
        })

    return evaluations


if __name__ == "__main__":
    print("="*80)
    print(" SIMULADOR DE COHORTE COMPLETA DE 450 EQUIPOS - ANÁHUAC MAYAB")
    print("="*80)

    # 1. Generate 450 teams
    cohort_path = generate_450_cohort()
    print(f"[1] Generado archivo de 450 equipos: {cohort_path}")

    # 2. Simulate 5-Judge Evaluations
    evals = simulate_450_evaluations(cohort_path)
    print(f"[2] Simuladas evaluaciones de 5 Jueces Sintéticos para los {len(evals)} proyectos.")

    # 3. Run Statistical Calibrator & Select Top 50
    calib = calibrator_module.calibrate_cohort_scores(evals, top_k=50)

    # 4. Export CSV & JSON
    json_out = "cohort_450_calibrated_ranking.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(calib, f, ensure_ascii=False, indent=2)
    print(f"[3] Exportado ranking JSON a: {json_out}")

    csv_out = "cohort_450_calibrated_ranking.csv"
    calibrator_module.export_ranking_csv(calib["all_ranked_teams"], csv_out)
    print(f"[4] Exportado ranking CSV a: {csv_out}")

    print("\n--- ESTADÍSTICAS DEL EMBUDO (450 -> 50 MEJORES) ---")
    print(f"Total Proyectos Evaluados:   {calib['cohort_stats']['total_teams']}")
    print(f"Media Cruda del Jurado:      {calib['cohort_stats']['raw_mean']:.2f}/100")
    print(f"Desviación Estándar Cruda:   {calib['cohort_stats']['raw_stdev']:.2f}")
    print(f"Puntaje de Corte (Rank #50): {calib['cohort_stats']['cutoff_score']:.2f}/100")
    print(f"Finalistas 2do Semestre:     {len([t for t in calib['top_finalists'] if t['semester'] == 2])}")
    print(f"Finalistas 4to Semestre:     {len([t for t in calib['top_finalists'] if t['semester'] == 4])}")
    print(f"Equipos en Zona Fronteriza:  {len(calib['borderline_teams'])}")

    print("\n--- TOP 10 FINALISTAS SELECCIONADOS ---")
    for t in calib["top_finalists"][:10]:
        track = "2° Sem (Prototipos)" if t["semester"] == 2 else "4° Sem (BMC)"
        print(f"Rank #{t['rank']:02d} | Calibrado: {t['calibrated_score']:.1f} | Raw: {t['raw_mean_score']:.1f} | [{track}] {t['team_name']}")
