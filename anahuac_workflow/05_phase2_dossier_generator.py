"""
Module 05: Phase 2 Executive Briefing Agent (1-Page Investor Memo / Prototype Dossier)
For the Top 50 Finalist teams advancing to human panels, this module generates a concise,
1-page executive dossier so senior judges can evaluate the venture in 2 minutes instead of 20.
"""

import json
import logging
import urllib.request
import os
from typing import Dict, Any
from config import DEFAULT_LLM_BASE_URL, MODEL_REASONING, MODEL_FAST

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DossierGenerator")


def call_llm(messages, model: str = MODEL_FAST, temperature: float = 0.3) -> str:
    """Call the OpenAI-compatible endpoint on the local dual Titan GPUs."""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1200
    }
    req = urllib.request.Request(
        f"{DEFAULT_LLM_BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def generate_executive_dossier(finalist_team: Dict[str, Any]) -> str:
    """Generate a clean, high-density 1-page executive memo for human judges."""
    team_name = finalist_team["team_name"]
    team_id = finalist_team["team_id"]
    rank = finalist_team.get("rank", 1)
    semester = finalist_team["semester"]
    title = finalist_team["project_title"]
    score = finalist_team.get("calibrated_score", 85)

    logger.info(f"Generating 1-Page Executive Dossier for Rank #{rank}: {team_name}...")

    judges_summary = "\n".join([
        f"- **{j['role']} ({j['score']}/100):** {j['feedback']}"
        for j in finalist_team.get("individual_judges", [])
    ])

    prompt = (
        f"Genera una FICHA TÉCNICA EJECUTIVA (Investor Dossier de 1 Página) para el jurado humano final de Anáhuac Mayab.\n"
        f"Datos del Proyecto:\n"
        f"- Equipo: {team_name} (ID: {team_id}) | Posición: #{rank} de 450 | Calificación Calibrada: {score}/100\n"
        f"- Track: {'2do Semestre - Feria de Prototipos' if semester == 2 else '4to Semestre - Business Model Canvas'}\n"
        f"- Título: {title}\n\n"
        f"Dictamen Colegiado de los 5 Jueces Sintéticos:\n{judges_summary}\n\n"
        "ESTRUCTURA EXACTA REQUERIDA (Formato Markdown Profesional):\n"
        "1. RESUMEN EJECUTIVO (30 Segundos): Problema, Solución y Propuesta de Valor central.\n"
        f"2. {'ESPECIFICACIONES TÉCNICAS DEL PROTOTIPO Y FACTIBILIDAD' if semester == 2 else 'ECONOMÍA UNITARIA Y MODELO DE NEGOCIO (CAC, LTV, Monetización)'}.\n"
        "3. DESGLOSE DEL PANEL DE 5 JUECES: Matriz de fortalezas clave y advertencias detectadas.\n"
        "4. 3 PREGUNTAS CRÍTICAS RECOMENDADAS PARA EL JUEZ HUMANO: Tres preguntas directas y desafiantes para hacerle al equipo en la sesión en vivo.\n\n"
        "Tono: Estilo Memo de Venture Capital / Aceleradora Universitaria de Alto Rendimiento. Denso en datos, sin rodeos ni texto de relleno."
    )

    messages = [
        {"role": "system", "content": "Eres el Director Técnico del Fondo de Inversión y Comité de Evaluación de Anáhuac Mayab."},
        {"role": "user", "content": prompt}
    ]

    dossier_md = call_llm(messages, model=MODEL_FAST)
    return dossier_md


def save_dossier_to_file(finalist_team: Dict[str, Any], output_dir: str) -> str:
    """Generate and save the dossier to a markdown file."""
    os.makedirs(output_dir, exist_ok=True)
    dossier_content = generate_executive_dossier(finalist_team)
    filename = f"Dossier_Rank{finalist_team.get('rank', 1):02d}_{finalist_team['team_id']}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(dossier_content)
    logger.info(f"Dossier saved to {filepath}")
    return filepath
