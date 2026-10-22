"""
Pipeline Orchestrator: End-to-End Autonomous AI Workflow
Universidad Anáhuac Mayab - Innovación (2° Sem) & Emprendimiento (4° Sem)

Orchestrates:
  1. Intake Validation & Track Segmentation
  2. Tavus Realtime Avatar Pitch Sparring
  3. The "5 Synthetic Judges" Consensus Panel (Objetivo Justo)
  4. Statistical Outlier Calibration & Top 50 Funnel Selection
  5. Phase 2 Executive Briefing Dossiers (1-Page Memos for Human Panels)
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, List

from config import (
    DEFAULT_LLM_BASE_URL,
    PUBLIC_LLM_URL,
    MODEL_FAST,
    MODEL_REASONING,
    TOP_FINALISTS_COUNT
)
from importlib import import_module

# Dynamically import the pipeline modules
intake_module = import_module("01_intake_validator")
sparring_module = import_module("02_tavus_sparring_manager")
panel_module = import_module("03_synthetic_5judges_panel")
calibrator_module = import_module("04_statistical_calibrator")
dossier_module = import_module("05_phase2_dossier_generator")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PipelineOrchestrator")


def run_pipeline(
    input_file: str,
    output_dir: str,
    top_k: int = TOP_FINALISTS_COUNT,
    generate_tavus_room: bool = False,
    generate_dossiers: bool = True
) -> Dict[str, Any]:
    """Execute the full end-to-end evaluation and triage pipeline."""
    os.makedirs(output_dir, exist_ok=True)
    dossiers_dir = os.path.join(output_dir, "phase2_dossiers")
    os.makedirs(dossiers_dir, exist_ok=True)

    print("\n" + "="*80)
    print(" ANÁHUAC MAYAB - SISTEMA AUTOMATIZADO DE EVALUACIÓN Y TRIAGE IA")
    print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" LLM Endpoint: {DEFAULT_LLM_BASE_URL} (Público SSL: {PUBLIC_LLM_URL})")
    print(f" Modelos: Rápido ({MODEL_FAST}) | Razonamiento ({MODEL_REASONING})")
    print("="*80 + "\n")

    # -------------------------------------------------------------------------
    # PASO 1: Ingesta y Validación de Equipos (Top of Funnel)
    # -------------------------------------------------------------------------
    logger.info(">>> PASO 1: INGESTA Y SEGMENTACIÓN POR TRACK ACADÉMICO...")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input cohort file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        raw_submissions = json.load(f)

    intake_result = intake_module.process_cohort_intake(raw_submissions)
    all_valid_teams = intake_result["track_2nd_sem"] + intake_result["track_4th_sem"]
    logger.info(f"Equipos Validados: {len(all_valid_teams)} | Rechazados: {len(intake_result['rejected'])}")

    # -------------------------------------------------------------------------
    # PASO 2: Tavus Sparring Rehearsal (Opcional / Demostración)
    # -------------------------------------------------------------------------
    sparring_demo_results = []
    if generate_tavus_room and all_valid_teams:
        logger.info(">>> PASO 2: GENERANDO SALA DE SPARRING EN VIVO CON AVATAR MATEO...")
        demo_team = all_valid_teams[0]
        room = sparring_module.create_avatar_sparring_session(demo_team)
        if room:
            sparring_demo_results.append(room)
            logger.info(f"Sala de Práctica Generada para {demo_team['team_name']}: {room['conversation_url']}")
    else:
        logger.info(">>> PASO 2: Sparring interactivo disponible bajo demanda vía 02_tavus_sparring_manager.py")

    # -------------------------------------------------------------------------
    # PASO 3: Panel de 5 Jueces Sintéticos (Objetivo Justo)
    # -------------------------------------------------------------------------
    logger.info(">>> PASO 3: EJECUTANDO PANEL DE 5 JUECES SINTÉTICOS EN DUAL TITAN GPUS...")
    raw_eval_path = os.path.join(output_dir, "01_raw_5judges_evaluations.json")
    
    # Cargar caché existente si existe para reanudar sin re-evaluar
    evaluations_by_id = {}
    if os.path.exists(raw_eval_path):
        try:
            with open(raw_eval_path, "r", encoding="utf-8") as f:
                cached_list = json.load(f)
                evaluations_by_id = {e["team_id"]: e for e in cached_list}
            logger.info(f"Reanudación activa: {len(evaluations_by_id)} evaluaciones encontradas en caché.")
        except Exception as e:
            logger.warning(f"No se pudo leer caché de evaluaciones previas: {e}")

    evaluations = []
    for idx, team in enumerate(all_valid_teams, 1):
        team_id = team["team_id"]
        if team_id in evaluations_by_id:
            logger.info(f"[{idx}/{len(all_valid_teams)}] {team_id} ('{team['team_name']}') ya evaluado en caché. Omitiendo llamadas LLM.")
            evaluations.append(evaluations_by_id[team_id])
            continue

        logger.info(f"[{idx}/{len(all_valid_teams)}] Evaluando {team_id} - '{team['team_name']}'...")
        eval_record = panel_module.run_5judges_consensus(team)
        evaluations.append(eval_record)
        evaluations_by_id[team_id] = eval_record

        # Guardado incremental inmediato
        with open(raw_eval_path, "w", encoding="utf-8") as f:
            json.dump(list(evaluations_by_id.values()), f, ensure_ascii=False, indent=2)

    logger.info(f"Evaluaciones crudas completadas ({len(evaluations)} equipos) guardadas en {raw_eval_path}")

    # -------------------------------------------------------------------------
    # PASO 4: Calibración Estadística y Selección de Finalistas (Top 50)
    # -------------------------------------------------------------------------
    logger.info(">>> PASO 4: CALIBRACIÓN ESTADÍSTICA (Z-SCORE) Y EMBUDO DE FINALISTAS...")
    calibration_result = calibrator_module.calibrate_cohort_scores(evaluations, top_k=top_k)

    # Exportar CSV de ranking completo
    csv_path = os.path.join(output_dir, "02_cohort_calibrated_ranking.csv")
    calibrator_module.export_ranking_csv(calibration_result["all_ranked_teams"], csv_path)

    # Guardar JSON de calibración
    calib_json_path = os.path.join(output_dir, "02_cohort_calibrated_ranking.json")
    with open(calib_json_path, "w", encoding="utf-8") as f:
        json.dump(calibration_result, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------------------------------
    # PASO 5: Generación de Fichas Técnicas / Dossiers para Jueces Humanos
    # -------------------------------------------------------------------------
    dossier_files = []
    if generate_dossiers:
        logger.info(f">>> PASO 5: GENERANDO FICHAS EJECUTIVAS DE 1 PÁGINA PARA TOP {len(calibration_result['top_finalists'])} FINALISTAS...")
        for finalist in calibration_result["top_finalists"]:
            d_file = dossier_module.save_dossier_to_file(finalist, dossiers_dir)
            dossier_files.append(d_file)

    # -------------------------------------------------------------------------
    # RESUMEN EJECUTIVO FINAL
    # -------------------------------------------------------------------------
    print("\n" + "="*80)
    print(" RESUMEN FINAL DEL PROCESAMIENTO - ANÁHUAC MAYAB")
    print("="*80)
    print(f"Total Proyectos Procesados: {len(all_valid_teams)}")
    print(f"Media Cohorte (Cruda):      {calibration_result['cohort_stats']['raw_mean']:.2f}/100")
    print(f"Desviación Estándar:        {calibration_result['cohort_stats']['raw_stdev']:.2f}")
    print(f"Puntaje de Corte (Top {top_k}):    {calibration_result['cohort_stats']['cutoff_score']:.2f}/100")
    print(f"Finalistas Clasificados:    {len(calibration_result['top_finalists'])}")
    print(f"Dossiers Generados:         {len(dossier_files)}")
    print(f"Archivo CSV de Ranking:     {csv_path}")
    print(f"Directorio de Dossiers:     {dossiers_dir}")
    print("="*80)

    print("\n--- TOP FINALISTAS SELECCIONADOS ---")
    for fin in calibration_result["top_finalists"]:
        track_name = "2° Sem (Prototipos)" if fin["semester"] == 2 else "4° Sem (BMC)"
        discrepancy_flag = " [!] DISCREPANCIA" if fin.get("has_high_discrepancy") else ""
        print(f"Rank #{fin['rank']:02d} | Score: {fin['calibrated_score']:.1f} | [{track_name}] {fin['team_name']} - {fin['project_title'][:40]}...{discrepancy_flag}")

    return {
        "intake": intake_result,
        "calibration": calibration_result,
        "sparring_rooms": sparring_demo_results,
        "dossier_files": dossier_files
    }


def main():
    parser = argparse.ArgumentParser(description="Anahuac Mayab Autonomous AI Evaluation Pipeline")
    parser.add_argument("--input", default="sample_cohort.json", help="Path to input cohort JSON file")
    parser.add_argument("--output-dir", default="output", help="Directory to save evaluations and dossiers")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top finalists to qualify")
    parser.add_argument("--sparring-demo", action="store_true", help="Generate live Tavus avatar room for test team")
    parser.add_argument("--skip-dossiers", action="store_true", help="Skip generating 1-page dossiers")

    args = parser.parse_args()

    run_pipeline(
        input_file=args.input,
        output_dir=args.output_dir,
        top_k=args.top_k,
        generate_tavus_room=args.sparring_demo,
        generate_dossiers=not args.skip_dossiers
    )


if __name__ == "__main__":
    main()
