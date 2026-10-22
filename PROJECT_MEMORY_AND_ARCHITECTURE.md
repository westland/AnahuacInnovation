# System Memory & Infrastructure State: Anáhuac Mayab AI Pipeline

This document records the exact configuration, network routes, credentials, and hardware states established across the local GPU node (`clawinc`), the Hetzner CX23 gateway server, and Tavus.

---

## 1. Hardware Node: `clawinc` (Local Titan Rig)
* **Tailscale Hostname**: `clawinc`
* **Tailscale IP**: `100.77.93.2`
* **Local User**: `openclaw`
* **Password**: `4182`
* **OS / Kernel**: Linux `7.0.0-38-generic` (Ubuntu 24.04 LTS HWE)
* **Motherboard / CPU**: ASRock motherboard, Intel Core i9, 94 GB DDR4 DRAM
* **GPUs**: **2x NVIDIA GeForce GTX TITAN X (GM200 Maxwell)**
  * GPU 0: PCIe `65:00.0`, 12,288 MiB VRAM
  * GPU 1: PCIe `b3:00.0`, 12,288 MiB VRAM
  * **Combined VRAM**: **24,576 MiB (24.0 GiB)**
* **NVIDIA Driver**: `580.178.04` (official legacy Maxwell branch with CUDA 13.0)
* **Kernel Module**: `linux-modules-nvidia-580-generic-hwe-24.04` compiled and verified under `7.0.0-38-generic`
* **Boot Services**: `tailscaled.service` and `ssh.service` are permanently enabled on boot.

---

## 2. LLM Engine (Ollama on `clawinc`)
* **Service**: Systemd user service (`/home/openclaw/.config/systemd/user/ollama.service`)
* **Bind Address**: `0.0.0.0:11434` (listens on all interfaces including Tailscale)
* **CORS / Origins**: `OLLAMA_ORIGINS=*`
* **GPU Allocation**: Ollama detects both Titan GPUs automatically (`CUDA0` 12GB + `CUDA1` 12GB, total 24GB pooled VRAM).
* **Available Models**:
  * `qwen2.5:14b` (14.7B params, Q4_K_M, ~9.0GB) — *Primary low-latency model for Tavus and fast triage (~2.5s warm)*.
  * `qwen3:32b` (32.8B params, Q4_K_M, ~20.2GB) — *Primary high-reasoning model for 5-Judge consensus panel and BMC audit*.
  * `gemma4:latest` (8.0B params, Q4_K_M, ~9.6GB) — *Ultra-low latency model (~1.0s warm)*.
  * `translategemma:27b` (27.4B params, Q4_K_M, ~17.3GB) — *Translation & cross-language synthesis*.
  * `gemma4:26b` (25.8B params, Q4_K_M, ~18.0GB).

---

## 3. Public SSL Gateway: Hetzner CX23 Server
* **Server ID**: `164586470` (`ubuntu-4gb-hel1-2`)
* **Public IPv4**: `89.167.22.10`
* **Location**: Helsinki, Finland (DC eu-central)
* **Root Credentials**: `root` / `@Wei2Shi4Lin2`
* **Tailscale Node**: `hetzner-cx23` (`100.102.97.18`) on `chris.westland@gmail.com`
* **SSL Certificate**: Let's Encrypt Wildcard / Direct SAN for `89.167.22.10.sslip.io` (expires 2027-01-20)
* **Reverse Proxy Engine**: Nginx with Server-Sent Events (SSE) streaming enabled:
  * Route: `https://89.167.22.10.sslip.io/v1/`
  * Upstream: `http://100.77.93.2:11434/v1/` (over Tailscale WireGuard mesh)
  * Settings: `proxy_buffering off`, `proxy_cache off`, `chunked_transfer_encoding on`, timeouts 300s.
  * *Bypasses Cloudflare bot detection so Tavus webhooks and streaming APIs connect uninterrupted*.

---

## 4. Tavus Conversational Video Avatars (CVI)
* **Active Production Account**: `westland@uic.edu` (**Builder Tier** — active credits, no 402 errors)
* **Active Production API Key**: `5946393e01674a92a0e17f2c3231278c`
* **Deprecated Free Account**: `chris.westland@gmail.com` (deprecated/deleted, previously hit credit cap)
* **Custom LLM Endpoint Registered with Tavus**: `https://89.167.22.10.sslip.io/v1`
* **Active Replicas & Personas on Builder Account**:
  1. **Mateo (Spanish Male Avatar)**:
     * **Persona ID**: `pd0f8ef69aaf`
     * **Replica ID**: `rbb3d627a705` (Mateo, Phoenix-4.5)
     * **Voice ID**: `v5afffb3826f5` (Native Spanish male voice)
     * **Flow Settings**: `replica_interruptibility: "low"`, `turn_taking_patience: "high"`, `turn_detection_model: "sparrow-2"`
     * **Thumbnail Image**: `https://cdn.replica.tavus.io/61338/thumbnail.jpg`
     * **HD Video Feed**: `https://cdn.replica.tavus.io/61338/198f094f.mp4`
     * **LLM Engine**: `qwen2.5:14b` via `89.167.22.10.sslip.io`
     * **Prompt**: Exclusively Spanish, Socratic, concise for conversational video flow (1-2 sentences), completes sentences with fluent cadence.
  2. **Prof. Luna (English Female Avatar)**:
     * **Persona ID**: `p2f0e8a584be`
     * **Replica ID**: `r983d5889432` (Luna, Phoenix-4.5)
     * **TTS Engine**: `elevenlabs`
     * **Voice ID**: `jsCqWAovK2LkecY7zXl4` (**Freya**: Sensual, breathy, captivating feminine voice)
     * **Voice Settings**: `stability: 0.35` (dynamic breathiness), `similarity_boost: 0.82`, `style: 0.45`
     * **Flow Settings**: `replica_interruptibility: "low"`, `turn_taking_patience: "high"`, `turn_detection_model: "sparrow-2"` (resolves audio drop-out during participant speech; lipsync and audio stay strictly synchronized)
     * **Thumbnail Image**: `https://cdn.replica.tavus.io/60594/thumbnail.jpg`
     * **HD Video Feed**: `https://cdn.replica.tavus.io/60594/51c5ab29.mp4`
     * **LLM Engine**: `qwen2.5:14b` via `89.167.22.10.sslip.io`
* **Interactive Studio Architecture**:
  * Dual-view video booth embedded on page:
    * **View 1 (Daily.co WebRTC Call)**: Embeds live Daily room generated via Builder account (`https://tavus.daily.co/{conv_id}`) with multi-participant group calling support, copy link bar, and **"Nueva Sala" (Fresh Session)** button.
    * **View 2 (Socratic Rehearsal Studio)**: Includes live student webcam preview, 3-minute pitch countdown timer, audio wave visualizer, and instant Socratic challenges generated by local Titan Qwen 2.5.
* **Timeout Configuration Standard**:
  * `participant_absent_timeout: 3600` (1 hour wait time before expiring if host hasn't joined)
  * `participant_left_timeout: 300` (5 minutes tolerance for browser reconnects)
  * `max_call_duration: 3600` (1 hour maximum call length)

---

## 5. Universidad Anáhuac Mayab Automated Pipeline

### 5.1 System Directory & Files
Located at `c:\Users\chris\Desktop\Mayra_projects_paper\anahuac_workflow\`:
* [`config.py`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/config.py): Centralized endpoint URLs, dual-Titan model definitions, Tavus PAL IDs, and target cohort constants.
* [`01_intake_validator.py`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/01_intake_validator.py): Ingestion, schema validation, and academic track segmentation (2nd Sem *Innovación* vs 4th Sem *Emprendimiento*).
* [`02_tavus_sparring_manager.py`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/02_tavus_sparring_manager.py): On-demand Socratic pitch sparring room generator using the Spanish Mateo Avatar with 1-hour timeout overrides.
* [`03_synthetic_5judges_panel.py`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/03_synthetic_5judges_panel.py): The 5 Synthetic Judge persona jury + meta-judge consensus and discrepancy detection (>15 pts).
* [`04_statistical_calibrator.py`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/04_statistical_calibrator.py): Z-score normalization and percentile ranking across all 450 projects to guarantee *Objetivo Justo* and select the Top 50.
* [`05_phase2_dossier_generator.py`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/05_phase2_dossier_generator.py): 1-page executive memos / investor dossiers for human judging panels.
* [`pipeline_orchestrator.py`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/pipeline_orchestrator.py): Master CLI orchestrator that chains all modules end-to-end.
* [`sample_cohort.json`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/sample_cohort.json): Representative student cohort dataset for testing and demonstrations.

### 5.2 Academic Track Schemas
* **Track 1: 2nd Semester (*Innovación / Feria de Prototipos*)**:
  * Deliverable: Physical or digital prototype showcase.
  * Required fields: `team_id`, `team_name`, `semester: 2`, `project_title`, `video_pitch_url`, `prototype_type`, `prototype_description`, `target_user`.
  * Avatar Coaching Focus: Empirical validation, user testing failures, desirability metrics.
* **Track 2: 4th Semester (*Emprendimiento / Business Model Canvas*)**:
  * Deliverable: Formal venture business model (Alexander Osterwalder 9 blocks).
  * Required fields: `team_id`, `team_name`, `semester: 4`, `project_title`, `video_pitch_url`, `value_proposition`, `customer_segments`, `revenue_streams`, `cost_structure`.
  * Avatar Coaching Focus: Unit economics, CAC vs LTV, distribution channels, contribution margins.

### 5.3 The 5 Synthetic Judges Panel (Objetivo Justo)
1. **Dr. Fernando Ruiz** (*Viabilidad Financiera*): Evaluates cost structures, pricing, unit economics, CAC/LTV.
2. **Mtra. Sofía Morales** (*Validación de Mercado*): Evaluates user discovery, interviews, empirical proof, and problem authenticity.
3. **Ing. Carlos Méndez** (*Innovación y Diferenciación*): Evaluates technical feasibility, regional competitiveness in Yucatán/Mexico, and moat.
4. **Lic. Valeria Garza** (*Pitch y Comunicación*): Evaluates hook, narrative structure, time compliance, and storytelling.
5. **Dr. Alejandro H.** (*Auditor de Rúbrica Académica*): Verifies compliance with Anáhuac institutional deliverables (TRL prototype vs 9 BMC blocks).
* **Consensus Synthesis**: Meta-judge calculates mean and standard deviation, flags judges with delta > 15 pts from the mean, and drafts a 3-paragraph official verdict.

### 5.4 Statistical Calibration (Z-Score Normalization)
* Computes cohort mean ($\mu$) and standard deviation ($\sigma$).
* Calculates $z = \frac{x - \mu}{\sigma}$.
* Maps to calibrated score: $S_{cal} = 75.0 + (z \times 10.0)$, bounded to $[0, 100]$.
* Ranks cohort descending, flags borderline teams ($\pm 1.0$ pt from cutoff), and exports `cohort_calibrated_ranking.csv`.

### 5.5 Phase 2 Executive Dossiers
* Generates a 1-page high-density Markdown investor memo for each Top 50 finalist.
* Includes: 30-Second Executive Summary, Technical Prototype / Unit Economics Breakdown, 5-Judge Matrix, and 3 Critical Challenge Questions for human judges during the live final.

### 5.6 Operational Commands
* **Run Complete Pipeline**:
  ```bash
  python pipeline_orchestrator.py --input sample_cohort.json --top-k 50 --output-dir output
  ```
* **Test Individual Modules**:
  ```bash
  # Test Intake Validation
  python 01_intake_validator.py

  # Generate Live 1-Hour Tavus Avatar Sparring Room
  python 02_tavus_sparring_manager.py

  # Test 5-Judge Consensus Panel
  python 03_synthetic_5judges_panel.py
  ```

---

## 6. Official Web Portal on Hetzner CX23

* **Public Portal URL**: [`https://89.167.22.10.sslip.io/`](https://89.167.22.10.sslip.io/)
* **Server**: Hetzner CX23 (`89.167.22.10`), Ubuntu 24.04
* **Systemd Service**: `anahuac-portal.service` (Active & Enabled on boot)
  * Working Directory: `/var/www/anahuac_portal`
  * Process: `/usr/local/bin/uvicorn app:app --host 127.0.0.1 --port 8500`
* **Nginx Reverse Proxy Routing**:
  * Root `/` -> `http://127.0.0.1:8500` (FastAPI Web Portal, Spanish UI, SPA)
  * API `/v1/` -> `http://100.77.93.2:11434/v1/` (Ollama LLM dual Titan mesh)
  * Client Max Body Size: `60M` (supports direct PDF, BMC, presentation, and media uploads)
* **Branding Implementation**:
  * Anáhuac Orange: `#FF5900`
  * Dark Charcoal: `#231F20`
  * Warm Cream: `#FAF8F5`
  * Soft Orange Badges: `#FFEEDC` / `#C44100`
  * Official Logo: `/static/anahuac_mayab_highres.png`
* **Avatar Pitch Sparring Integration**:
  * **Mateo (Mentor en Español)**: PAL `p270626e4080`
    * Dynamic Room Generator: Endpoint `POST /api/sparring/launch-room` calls Tavus v2 API (`https://tavusapi.com/v2/conversations`) on-demand with `persona_id: p270626e4080`.
    * Eliminates static link expiration ("The meeting has ended") by creating fresh 1-hour active Daily.co rooms with `participant_absent_timeout: 3600` and `max_call_duration: 3600`.
    * Group Calling: One-click "Copiar Enlace para Reunión en Grupo" allows all 3-5 student team members to join simultaneously on video with Mateo.
  * **Prof. Luna (English / Global Track)**: PAL `p10847d10581`
    * Dynamic Room Generator via `POST /api/sparring/launch-room` with `persona_id: p10847d10581`.
* **Interactive Features & Data Safeguards**:
  1. *Registro y Entrega*: Dynamic track switching (2do Semestre *Prototipos* vs 4to Semestre *BMC*), drag & drop file upload with progress feedback, and official Folio receipt generation.
  2. *Cabina de Sparring*: Dynamic on-demand video room launching, Socratic question cards, 1-hour session timers, group video room link sharing.
  3. *Panel de 5 Jueces*: Real-time pre-audit evaluation simulation with multi-persona scoring and meta-judge synthesis.
  4. *Tablero de Calificaciones (Permanently Protected)*: Calibrated Z-score rankings across 450 projects (Mean 72.01, Cutoff 88.08, Top 50 badges), instant 1-page executive dossier viewer, and CSV ledger download.
  5. *Clean-Up Safeguard*: The "Limpiar" button and clean-up strip have been completely removed from the dashboard to guarantee zero accidental deletion of synthetic or student evaluation data.
* **Verified Browser Recording Artifacts**:
  * Recording: `anahuac_portal_demo_1792699185216.webp`
  * Recording: `anahuac_mode_toggle_demo_1792701094301.webp`

---

## 7. Custom Domain & Cloudflare Zero Trust Tunnel

* **Registered Custom Domain**: **`anahuac-innovation.com`**
  * Registrar: Cloudflare Registrar (Account: `chris.westland@gmail.com`)
* **Live Domain Endpoints**:
  * **`https://anahuac-innovation.com/`** (Primary custom domain)
  * **`https://www.anahuac-innovation.com/`** (Subdomain route)
  * **`https://89.167.22.10.sslip.io/`** (Direct Let's Encrypt SSL Gateway)
* **Cloudflare Tunnel Architecture**:
  * **Tunnel Name**: `anahuac-portal-tunnel`
  * **Tunnel ID**: `845445b9-ee21-411b-81ba-501c5973f315`
  * **Connector Daemon**: `cloudflared.service` (Systemd active & enabled on Hetzner CX23 `89.167.22.10`)
  * **Edge Protocol**: QUIC (connected to multiple edge locations: `hel01`, `dme05`)
  * **Origin Route Target**: `http://localhost:8500`
* **Nginx Dual-Binding**:
  * Configured in `/etc/nginx/sites-enabled/sslip-llm.conf` to handle `server_name anahuac-innovation.com www.anahuac-innovation.com 89.167.22.10.sslip.io 89.167.22.10;`
  * Proxies `/` to FastAPI port `8500` and `/v1/` to Tailscale GPU node `http://100.77.93.2:11434/v1/`.

---

## 8. Summary of Persistent System Knowledge

1. **Hardware & Models**:
   - `clawinc` (`100.77.93.2:11434`): Dual GTX Titan X GPUs (24GB VRAM total), running `qwen2.5:14b` (latency ~2.5s) for real-time triage, and `qwen3:32b` for deep 5-judge reasoning panels.
2. **Gateway & Portal**:
   - Hetzner CX23 (`89.167.22.10` / `100.102.97.18`): `anahuac-portal.service` on port `8500`, Nginx SSL proxy, Let's Encrypt certificates, `cloudflared` tunnel. Port `8000` is reserved for AstroSentry.
3. **Cohort Data**:
   - 450 student ventures (2nd Sem Prototipos & 4th Sem BMC) permanently calibrated with Z-score normalizer, Top 50 cutoff at 88.08/100, and individual 1-page dossiers. Clean buttons removed to prevent any accidental wipe.
4. **Avatars & Sparring**:
   - Tavus API key: `5946393e01674a92a0e17f2c3231278c` (Builder Account: `westland@uic.edu`).
   - Mateo (Spanish): Persona `pd0f8ef69aaf`, Replica `rbb3d627a705`, Voice `v5afffb3826f5`, `replica_interruptibility: low`, `turn_taking_patience: high`.
   - Prof. Luna (English): Persona `p2f0e8a584be`, Replica `r983d5889432`, ElevenLabs Freya voice `jsCqWAovK2LkecY7zXl4` (breathy, sensual feminine tone), `replica_interruptibility: low` (prevents sound cutoff while moving lips), `turn_taking_patience: high`.
   - On-demand dynamic session creation via `POST /api/sparring/launch-room` guarantees fresh 1-hour Daily.co rooms with group calling, copy link bar, and "Nueva Sala" quick-action button.

---

## 9. Responsive Avatar Scaling & Multi-Device UI Architecture (October 2026 Fix)

### 9.1 Root Cause of Avatar Blow-up
* **High-Res Unconstrained CDN Source**: The Tavus thumbnail portraits (`https://cdn.replica.tavus.io/61338/thumbnail.jpg` and `60594/thumbnail.jpg`) are raw 1920×1080 JPEG assets.
* **Missing Media Reset & CDN Cache**: Without a global CSS reset for `img` and without explicit width/height inline styles on the HTML tags, client browsers and Cloudflare edge caches rendered the images at their full native width (1920px), breaking out of the 72px `.avatar-portrait-wrap` and overflowing the viewport.

### 9.2 Comprehensive Solutions Deployed
1. **Global CSS Media Reset** ([`style.css`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/web_portal/static/style.css)):
   ```css
   img, picture, video, canvas, svg, iframe {
     max-width: 100%;
     box-sizing: border-box;
   }
   ```
2. **Defensive Inline Sizing** ([`index.html`](file:///c:/Users/chris/Desktop/Mayra_projects_paper/anahuac_workflow/web_portal/templates/index.html)):
   ```html
   <img src="https://cdn.replica.tavus.io/61338/thumbnail.jpg" alt="Mateo" class="avatar-portrait-img" width="80" height="80" style="width: 80px; height: 80px; min-width: 80px; max-width: 80px; min-height: 80px; max-height: 80px; object-fit: cover; object-position: center top; border-radius: 50%; display: block;">
   ```
   *Guarantees strict 80px boundary rendering instantly on initial HTML parse before any stylesheet downloads.*
3. **Dedicated Flex Top-Row for Badges**:
   * Wrapped badges in `.avatar-top-row` (`display: flex; justify-content: flex-end; margin-bottom: 6px;`).
   * Eliminates absolute-position collisions with mentor name titles on narrow mobile screens (390px iPhone).
4. **Adaptive Device Breakpoints**:
   * **Desktop (> 992px)**: Dual-column grid with 80×80px circular portraits, brand accent borders (`#FF5900`), and pulsating green online status dots.
   * **Tablet (768px – 992px)**: 72×72px circular portraits, fluid full-width cards.
   * **Mobile (≤ 480px / 390px)**: 64×64px circular portraits, full title legibility with zero text truncation.
5. **Fluid Studio Booth & WebRTC Video**:
   * Configured `.daily-call-container .iframe-wrap iframe` with `height: clamp(380px, 62vh, 660px); max-width: 100%;` to scale seamlessly on laptops, iPads, and mobile phones.
6. **Cache-Busting & Deployment**:
   * Live deployment verified in browser automation across Desktop (1280px), Tablet (768px), and Mobile (390px) viewports on `https://anahuac-innovation.com/?tab=sparring`.

---

## 10. Official GitHub Repository & Documentation

* **Repository Name**: **`AnahuacInnovation`**
* **GitHub URL**: [**`https://github.com/westland/AnahuacInnovation`**](https://github.com/westland/AnahuacInnovation)
* **Default Branch**: `main`
* **Account**: `westland` (`westland@uic.edu`)
* **Included Documentation & Assets**:
  - [`README.md`](README.md): System overview, architecture diagram, module descriptions, quickstart guide, and badges.
  - [`USER_MANUAL.md`](USER_MANUAL.md): Comprehensive Spanish & English User Manual with step-by-step instructions for Students, Faculty/Judges, and System Administrators.
  - [`anahuac_workflow/`](anahuac_workflow/): Full automated pipeline, 450-student calibrated dataset, executive dossiers, and FastAPI web portal SPA.
  - `.gitignore`: Configured to safeguard sensitive server passwords (`Tavus.txt`), environments, and Python build caches.





