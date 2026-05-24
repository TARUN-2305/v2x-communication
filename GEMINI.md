# ECO-SYNC V2X (v2.0 — Production)

A multi-agent V2X (Vehicle-to-Everything) intelligent transport system for BMTC Route 378 (Kengeri TTMC ↔ Electronic City), Bengaluru. This system uses LLM-powered agents to mitigate bus bunching in real-time.

## Project Overview

- **Purpose**: Mitigate bus bunching on urban corridors using V2X communication and LLM-based decision making.
- **Key Technologies**:
    - **Backend**: FastAPI, Python, Paho-MQTT, SQLAlchemy (PostgreSQL), Redis.
    - **Frontend**: React, Leaflet (map), Recharts (metrics), Lucide-React.
    - **Infrastucture**: Docker Compose, MQTT (Mosquitto), PostgreSQL, Redis.
    - **LLM Stack**: Groq (Llama-3.3-70B) as primary, Ollama (Gemma 3, Phi-3) as local fallback.
- **Architecture**:
    - **Bus Agents (V2V)**: Broadcast Basic Safety Messages (BSM) and negotiate dispatch decisions.
    - **Traffic Management Centre (V2I)**: Broadcast Traffic Information Messages (TIM).
    - **Passenger Information (ATIS)**: Display real-time reasoning for decisions.
    - **Simulation Engine**: Models 6+ buses on a 1,203-point OSRM polyline with calibrated Poisson passenger arrivals.

## Building and Running

### Prerequisites
- Docker & Docker Compose
- Node.js (for local frontend development)
- Python 3.10+ (for local backend development)
- Ollama (optional, for local LLM fallback)

### Quick Start
1.  **Environment Setup**:
    ```bash
    cp .env.example .env
    # Edit .env and add GROQ_API_KEY for best results
    ```
2.  **Pull Local LLMs** (Optional but recommended):
    ```bash
    ollama pull gemma3:4b
    ollama pull phi3:latest
    ```
3.  **Launch with Docker Compose**:
    ```bash
    docker compose up --build
    ```
4.  **Access the Dashboard**: Open `http://localhost:3000` in your browser.

### Development Commands
- **Backend**:
    - Start locally: `uvicorn backend.main:app --reload`
    - Install deps: `pip install -r requirements.txt`
- **Frontend**:
    - Start dev server: `npm run dev` (in `frontend/` directory)
    - Build: `npm run build`
    - Lint: `npm run lint`

## Development Conventions

- **V2X Messaging**: All V2X messages follow SAE J2735 / ETSI ITS-G5 naming conventions.
    - `v2x/v2v/{bus_id}/bsm`: Basic Safety Messages.
    - `v2x/v2i/tmc/tim`: Traffic Information Messages.
    - `v2x/v2v/debate/{b1}/{b2}`: LLM debate transcripts.
    - `v2x/atis/{stop}`: Passenger information messages.
- **LLM Fallback**: Logic is implemented in `backend/engine.py`. It follows a strict hierarchy: Groq → Ollama Primary → Ollama Fallback → Rule-based fallback.
- **Persistence**: Metrics and decisions are persisted to PostgreSQL for longitudinal analysis. Ensure `DATABASE_URL` is set in `.env`.
- **Styling**: Frontend uses Tailwind CSS (v4) and Lucide-React for icons.
- **Real-time**: Communication between backend and frontend is via WebSockets (`/ws/live`).

## Key Files
- `backend/main.py`: Entry point for the FastAPI application.
- `backend/engine.py`: Core simulation logic and agent orchestration.
- `backend/mqtt/v2x_broker.py`: MQTT client for V2X message publishing.
- `backend/db/storage.py`: PostgreSQL persistence layer.
- `frontend/src/App.jsx`: Main React application and dashboard UI.
- `paper/ICCCNT_2026_EcoSync_V2X.md`: Draft research paper detailing the project's methodology and results.
