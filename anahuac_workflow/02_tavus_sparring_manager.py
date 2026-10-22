"""
Module 02: Tavus AI Sparring Partner & Avatar Rehearsal
Manages on-demand interactive pitch practice sessions for student teams before submission.
Connects directly to the live Spanish Avatar (Mateo) powered by local Qwen 2.5 on dual Titans.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from config import (
    TAVUS_API_KEY,
    TAVUS_API_BASE,
    REPLICA_MATEO,
    PARTICIPANT_ABSENT_TIMEOUT,
    PARTICIPANT_LEFT_TIMEOUT,
    MAX_CALL_DURATION
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TavusSparring")


def generate_sparring_context(team: Dict[str, Any]) -> str:
    """Generate track-specific Socratic coaching instructions for the avatar."""
    semester = team.get("semester", 2)
    title = team.get("project_title", "Proyecto Estudiantil")
    team_name = team.get("team_name", "Equipo")

    if semester == 2:
        # 2nd Semester: Innovación / Feria de Prototipos
        proto_desc = team.get("metadata", {}).get("prototype_description", "Prototipo en desarrollo")
        target_user = team.get("metadata", {}).get("target_user", "Usuarios objetivo")
        
        context = (
            f"El equipo '{team_name}' está practicando su pitch para la 'Feria de Prototipos' de 2do Semestre de Anáhuac Mayab. "
            f"Proyecto: '{title}'. Descripción del prototipo: '{proto_desc}'. Usuario objetivo: '{target_user}'. "
            "INSTRUCCIONES DE COACHING SOCRÁTICO: Escucha atentamente la presentación del alumno. "
            "Luego, interrumpe amablemente y haz 1 pregunta inquisitiva de Design Thinking sobre validación empírica: "
            "1. ¿Cómo probaron este prototipo físico/digital con usuarios reales? "
            "2. ¿Qué falló en la primera iteración y qué aprendieron? "
            "3. ¿Qué métrica de deseabilidad técnica demostró que funciona? "
            "Mantén tus respuestas breves (1 o 2 oraciones), en español natural y motivador."
        )
    else:
        # 4th Semester: Emprendimiento / Business Model Canvas
        val_prop = team.get("metadata", {}).get("value_proposition", "Propuesta de valor")
        rev = team.get("metadata", {}).get("revenue_streams", "Flujo de ingresos")
        costs = team.get("metadata", {}).get("cost_structure", "Costos operativos")
        
        context = (
            f"El equipo '{team_name}' está practicando su pitch de Business Model Canvas (BMC) de 4to Semestre de Anáhuac Mayab. "
            f"Proyecto: '{title}'. Propuesta de valor: '{val_prop}'. Ingresos: '{rev}'. Costos: '{costs}'. "
            "INSTRUCCIONES DE COACHING SOCRÁTICO DE NEGOCIOS: Escucha el pitch y haz preguntas tipo inversionista/VC: "
            "1. ¿Cuál es su Costo de Adquisición de Clientes (CAC) y cómo se compara con el LTV proyectado? "
            "2. ¿Por qué el canal de distribución seleccionado es el más escalable en el mercado mexicano? "
            "3. ¿Cuál es su margen de contribución unitario inicial? "
            "Habla en español profesional, conciso (máximo 2 oraciones por intervención) y exigente pero pedagógico."
        )

    return context


def create_avatar_sparring_session(
    team: Dict[str, Any],
    replica_id: str = REPLICA_MATEO
) -> Optional[Dict[str, Any]]:
    """Create a live Tavus Daily.co room for team pitch sparring with 1-hour timeout."""
    conversational_context = generate_sparring_context(team)
    team_name = team.get("team_name", "Equipo")
    team_id = team.get("team_id", "ANH")

    payload = {
        "replica_id": replica_id,
        "conversation_name": f"Sparring - {team_id} ({team_name})",
        "conversational_context": conversational_context,
        "properties": {
            "participant_absent_timeout": PARTICIPANT_ABSENT_TIMEOUT,  # 3600 seconds (1 hour)
            "participant_left_timeout": PARTICIPANT_LEFT_TIMEOUT,      # 300 seconds
            "max_call_duration": MAX_CALL_DURATION                     # 3600 seconds
        }
    }

    headers = {
        "x-api-key": TAVUS_API_KEY,
        "Content-Type": "application/json"
    }

    url = f"{TAVUS_API_BASE}/conversations"
    logger.info(f"Creating sparring session for {team_id} ({team_name}) with Mateo Avatar...")

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            room_url = data.get("conversation_url")
            conv_id = data.get("conversation_id")
            logger.info(f"Successfully generated sparring room for {team_name}!")
            logger.info(f"  -> Room URL: {room_url}")
            return {
                "team_id": team_id,
                "team_name": team_name,
                "conversation_id": conv_id,
                "conversation_url": room_url,
                "context_injected": conversational_context
            }
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP Error creating Tavus session: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        logger.error(f"Failed to create Tavus session: {e}")

    return None


if __name__ == "__main__":
    # Test generation with sample team
    sample_team = {
        "team_id": "DEMO-001",
        "team_name": "SargazoTech",
        "semester": 2,
        "project_title": "Biotextiles a base de macroalgas",
        "metadata": {
            "prototype_description": "Muestra textil impermeable de 20x20cm elaborada con biopolímero de sargazo.",
            "target_user": "Industria hotelera y moda sustentable de la Riviera Maya."
        }
    }

    session = create_avatar_sparring_session(sample_team)
    if session:
        print("\n=== Live Sparring Room Created ===")
        print(f"Join URL: {session['conversation_url']}")
