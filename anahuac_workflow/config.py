"""
Central Configuration for Anáhuac Mayab AI Innovation & Entrepreneurship Pipeline
Supports 2nd Semester (Innovación / Prototipos) and 4th Semester (Emprendimiento / BMC)
"""
import os

# --- LLM Endpoint Configuration ---
# Internal Tailscale URL (fastest if running on local mesh)
LOCAL_OLLAMA_URL = os.getenv("LOCAL_OLLAMA_URL", "http://100.77.93.2:11434")

# Public SSL Gateway (Hetzner CX23 -> Tailscale)
PUBLIC_LLM_URL = os.getenv("PUBLIC_LLM_URL", "https://89.167.22.10.sslip.io/v1")

# Default Base URL for OpenAI-compatible clients
DEFAULT_LLM_BASE_URL = LOCAL_OLLAMA_URL + "/v1"

# --- Models on Dual Titan GPUs (24GB VRAM) ---
MODEL_FAST = "qwen2.5:14b"       # 14.7B Q4_K_M (~2.5s latency, ideal for real-time triage & Tavus)
MODEL_REASONING = "qwen3:32b"    # 32.8B Q4_K_M (Deep analysis, 5-judge panel & investor memos)
MODEL_LIGHT = "gemma4:latest"    # 8.0B Q4_K_M (~1.0s latency)

# --- Tavus CVI Configuration (westland@uic.edu - Builder Account) ---
TAVUS_API_KEY = os.getenv("TAVUS_API_KEY", "5946393e01674a92a0e17f2c3231278c")
TAVUS_API_BASE = "https://tavusapi.com/v2"

# Replicas (Builder Tier)
REPLICA_MATEO = "rbb3d627a705"       # Mateo (Phoenix-4.5) Spanish
REPLICA_LUNA = "r983d5889432"        # Luna (Phoenix-4.5) English

# Personas / PAL IDs
PAL_MATEO_SPANISH = "p270626e4080"
PAL_PROFESSOR_ENGLISH = "p10847d10581"

# Session Timeout Standards (in seconds)
PARTICIPANT_ABSENT_TIMEOUT = 3600  # 1 hour wait before closing room
PARTICIPANT_LEFT_TIMEOUT = 300     # 5 minutes tolerance for browser reconnects
MAX_CALL_DURATION = 3600           # 1 hour maximum duration

# --- Cohort Target Constants ---
TARGET_COHORT_SIZE = 450
TOP_FINALISTS_COUNT = 50
