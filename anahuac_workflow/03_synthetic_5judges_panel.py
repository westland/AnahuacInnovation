"""
Module 03: The "5 Synthetic Judges" Consensus Panel (Objetivo Justo)
Simulates a balanced, multi-perspective institutional jury to evaluate and score
450 student projects objectively, eliminating human fatigue and bias.

Personas:
  1. Juez de Viabilidad Financiera (Financial Feasibility)
  2. Juez de Validación de Problema y Mercado (Problem & Customer Validation)
  3. Juez de Innovación y Diferenciación (Innovation & Moat)
  4. Juez de Pitch y Comunicación (Storytelling & Clarity)
  5. Auditor de Rúbrica Académica Anáhuac (Strict Milestone Auditor)
"""

import json
import logging
import statistics
import urllib.request
import urllib.error
from typing import Dict, Any, List
from config import DEFAULT_LLM_BASE_URL, MODEL_REASONING, MODEL_FAST

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("5JudgesPanel")

JUDGE_PERSONAS = [
    {
        "id": "judge_finance",
        "name": "Dr. Fernando Ruiz (Juez de Viabilidad Financiera y Economía Unitaria)",
        "role": "Inversionista Ángel y Experto en Finanzas",
        "system_prompt": (
            "Eres el Dr. Fernando Ruiz, juez de Viabilidad Financiera en el panel de evaluación de Anáhuac Mayab. "
            "Tu misión es evaluar con rigor matemático la estructura de costos, márgenes de contribución, proyecciones de ingresos, "
            "y realismo financiero (CAC, LTV, pricing en el contexto mexicano). "
            "Debes otorgar una calificación numérica estricta entre 1 y 100, y una justificación concisa en español (3-4 líneas)."
        )
    },
    {
        "id": "judge_market",
        "name": "Mtra. Sofía Morales (Juez de Validación de Mercado y Usuario)",
        "role": "Especialista en Investigación de Usuarios y Design Thinking",
        "system_prompt": (
            "Eres la Mtra. Sofía Morales, jueza de Validación de Mercado en Anáhuac Mayab. "
            "Tu objetivo es evaluar si el problema es real y si el equipo presenta evidencia empírica de validación "
            "(entrevistas, encuestas, pruebas con usuarios, cartas de intención o tracción inicial). Penaliza ideas basadas en suposiciones no validadas. "
            "Otorga una calificación entre 1 y 100, y tu justificación analítica en español (3-4 líneas)."
        )
    },
    {
        "id": "judge_innovation",
        "name": "Ing. Carlos Méndez (Juez de Innovación y Diferenciación)",
        "role": "Director de Tecnología y Mentor de Startups",
        "system_prompt": (
            "Eres el Ing. Carlos Méndez, juez de Innovación y Ventaja Competitiva en Anáhuac Mayab. "
            "Evalúas qué tan única es la propuesta frente a soluciones existentes en el sureste y en México. "
            "Analizas la viabilidad técnica del prototipo o modelo de negocio y las barreras de entrada (moat). "
            "Otorga una calificación entre 1 y 100, y tu justificación constructiva en español (3-4 líneas)."
        )
    },
    {
        "id": "judge_pitch",
        "name": "Lic. Valeria Garza (Juez de Comunicación y Storytelling)",
        "role": "Consultora de Comunicación y Pitch Coach",
        "system_prompt": (
            "Eres la Lic. Valeria Garza, jueza de Comunicación y Pitch en Anáhuac Mayab. "
            "Evalúas la claridad del mensaje, estructura narrativa (Hook, Problema, Solución, Mercado, Tracción, Ask), "
            "capacidad de síntesis en el tiempo límite, y seguridad en la presentación. "
            "Otorga una calificación entre 1 y 100, y tu retroalimentación en español (3-4 líneas)."
        )
    },
    {
        "id": "judge_auditor",
        "name": "Dr. Alejandro H. (Auditor Académico de Rúbrica Anáhuac)",
        "role": "Coordinador Académico de Emprendimiento e Innovación",
        "system_prompt": (
            "Eres el Dr. Alejandro H., auditor de rúbrica institucional en Anáhuac Mayab. "
            "Tu deber es verificar el cumplimiento estricto de los entregables académicos: "
            "Para 2do Semestre: Cumplimiento de la Feria de Prototipos (especificación de prototipo funcional o digital). "
            "Para 4to Semestre: Coherencia integral de los 9 bloques del Business Model Canvas de Osterwalder. "
            "Otorga una calificación entre 1 y 100, y tu dictamen institucional en español (3-4 líneas)."
        )
    }
]


def call_llm(messages: List[Dict[str, str]], model: str = MODEL_FAST, temperature: float = 0.2, max_tokens: int = 350) -> str:
    """Call the OpenAI-compatible endpoint on the local dual Titan GPUs."""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    req = urllib.request.Request(
        f"{DEFAULT_LLM_BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def evaluate_with_single_judge(judge: Dict[str, Any], project_summary: str, semester: int) -> Dict[str, Any]:
    """Execute evaluation for one judge persona and extract score + feedback."""
    prompt = (
        f"PROYECTO A EVALUAR:\n{project_summary}\n\n"
        f"Semestre Académico: {semester}° Semestre ({'Feria de Prototipos' if semester == 2 else 'Business Model Canvas'})\n\n"
        "INSTRUCCIÓN: Como evaluador experto, analiza la información anterior según tu especialidad. "
        "Debes responder OBLIGATORIAMENTE en formato JSON con exactamente estas dos claves:\n"
        "{\n"
        '  "calificacion": <numero entero entre 1 y 100>,\n'
        '  "justificacion": "<tu comentario y retroalimentacion detallada en espanol>"\n'
        "}\n"
        "Responde SOLAMENTE el objeto JSON sin texto antes ni después."
    )

    messages = [
        {"role": "system", "content": judge["system_prompt"]},
        {"role": "user", "content": prompt}
    ]

    raw_response = call_llm(messages, model=MODEL_FAST, max_tokens=220)
    
    # Parse JSON
    try:
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif clean_json.startswith("```"):
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
        parsed = json.loads(clean_json)
        score = int(parsed.get("calificacion", 70))
        feedback = parsed.get("justificacion", "Evaluación completada.")
    except Exception as e:
        logger.warning(f"Failed to parse JSON from {judge['name']}: {e}. Fallback parsing.")
        score = 70
        feedback = raw_response

    return {
        "judge_id": judge["id"],
        "judge_name": judge["name"],
        "role": judge["role"],
        "score": max(1, min(100, score)),
        "feedback": feedback
    }


def run_5judges_consensus(team: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the full 5-judge panel and meta-judge consensus calculation."""
    team_name = team.get("team_name", "Equipo")
    team_id = team.get("team_id", "ANH")
    semester = team.get("semester", 2)
    title = team.get("project_title", "Proyecto")
    meta = team.get("metadata", {})

    logger.info(f"Initiating 5-Judge Consensus Panel for {team_id}: {team_name}...")

    # Build Project Dossier
    if semester == 2:
        project_summary = (
            f"Equipo: {team_name} (ID: {team_id})\n"
            f"Título del Proyecto: {title}\n"
            f"Tipo de Prototipo: {meta.get('prototype_type', 'N/A')}\n"
            f"Descripción del Prototipo: {meta.get('prototype_description', 'N/A')}\n"
            f"Usuario Objetivo: {meta.get('target_user', 'N/A')}\n"
            f"Enlace de Pitch: {team.get('pitch_url', 'N/A')}"
        )
    else:
        project_summary = (
            f"Equipo: {team_name} (ID: {team_id})\n"
            f"Título del Proyecto: {title}\n"
            f"Propuesta de Valor: {meta.get('value_proposition', 'N/A')}\n"
            f"Segmento de Clientes: {meta.get('customer_segments', 'N/A')}\n"
            f"Fuentes de Ingresos: {meta.get('revenue_streams', 'N/A')}\n"
            f"Estructura de Costos: {meta.get('cost_structure', 'N/A')}\n"
            f"Enlace de Pitch: {team.get('pitch_url', 'N/A')}"
        )

    judge_results = []
    scores = []

    for judge in JUDGE_PERSONAS:
        res = evaluate_with_single_judge(judge, project_summary, semester)
        judge_results.append(res)
        scores.append(res["score"])
        logger.info(f"  -> {judge['name']}: {res['score']}/100")

    # Consensus & Outlier Statistics
    mean_score = round(statistics.mean(scores), 2)
    std_dev = round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0

    # Flag judges with discrepancy > 15 points from mean
    discrepancies = []
    for res in judge_results:
        diff = abs(res["score"] - mean_score)
        if diff > 15:
            discrepancies.append({
                "judge": res["judge_name"],
                "score": res["score"],
                "delta": round(diff, 2),
                "reason": "Discrepancia significativa frente al consenso general del jurado."
            })

    # Meta-Judge Synthesis
    synthesis_prompt = (
        f"Actúa como el Presidente del Comité de Jueces de la Universidad Anáhuac Mayab. "
        f"Sintetiza la evaluación colegiada del proyecto '{title}' ({team_name}).\n"
        f"Calificaciones individuales de los 5 jueces: {scores} (Promedio: {mean_score}/100, Desviación: {std_dev}).\n"
        f"Comentarios de los jueces:\n" + "\n".join([f"- {j['judge_name']}: {j['feedback']}" for j in judge_results]) + "\n\n"
        "Redacta un Dictamen Oficial de Retroalimentación en español estructurado en 3 párrafos:\n"
        "1. Veredicto Colegiado y Evaluación General.\n"
        "2. Principales Fortalezas Destacadas por los Jueces.\n"
        "3. Acciones Críticas Obligatorias para la Siguiente Fase.\n"
        "Tono formal, constructivo, motivador y académicamente riguroso."
    )

    meta_feedback = call_llm(
        [{"role": "system", "content": "Eres el Presidente del Jurado de Innovación de Anáhuac Mayab."},
         {"role": "user", "content": synthesis_prompt}],
        model=MODEL_FAST
    )

    evaluation_record = {
        "team_id": team_id,
        "team_name": team_name,
        "semester": semester,
        "project_title": title,
        "mean_score": mean_score,
        "std_dev": std_dev,
        "has_high_discrepancy": len(discrepancies) > 0,
        "discrepancies": discrepancies,
        "individual_judges": judge_results,
        "meta_verdict": meta_feedback
    }

    return evaluation_record


if __name__ == "__main__":
    # Test with sample team
    sample_team = {
        "team_id": "TEST-042",
        "team_name": "BioMayab Alimentos",
        "semester": 4,
        "project_title": "Harina de Grillo para Suplementación Proteica en Comunidades Mayas",
        "pitch_url": "https://youtu.be/test_pitch_42",
        "metadata": {
            "value_proposition": "Harina proteica con 70% contenido biológico a bajo costo para comedores comunitarios.",
            "customer_segments": "DIF Yucatán, cooperativas escolares y público con dietas fitness en Mérida.",
            "revenue_streams": "Venta por kilo ($180 MXN) y contratos institucionales anuales.",
            "cost_structure": "Granja de cultivo automatizada de grillos, molienda, empaque compostable."
        }
    }

    result = run_5judges_consensus(sample_team)
    print("\n================== DICTAMEN OFICIAL (OBJETIVO JUSTO) ==================")
    print(f"Equipo: {result['team_name']} | Calificación Promedio: {result['mean_score']}/100 (Desviación: {result['std_dev']})")
    print(f"Discrepancias detectadas: {len(result['discrepancies'])}")
    print("\nVeredicto del Comité:")
    print(result["meta_verdict"])
