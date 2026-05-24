# ECO-SYNC V2X v2.0 — Production

Multi-agent V2X intelligent transport system for BMTC Route 378 (Kengeri TTMC ↔ Electronic City). Fully containerised with Docker Compose.

## Quick Start

```bash
cp .env.example .env          # add your GROQ_API_KEY
ollama pull gemma3:4b         # local LLM fallback
ollama pull phi3:latest
ollama serve &
docker compose up --build
open http://localhost:3000
```

Click **Start** in the dashboard → watch 6 buses navigate real Bengaluru roads.

## What's New vs v1.0

| | v1.0 | v2.0 |
|---|---|---|
| Buses | 2 hardcoded | 2–8 configurable |
| V2X | Groq API call | MQTT broker + Groq + Ollama fallback |
| LLM fallback | None | Ollama gemma3:4b → phi3 → rules |
| Storage | None | PostgreSQL (all decisions, metrics) |
| Deployment | Manual uvicorn | Docker Compose one-command |
| Comparison | None | Agentic V2X vs Static toggle |
| Metrics | None | Live headway/bunching/decisions charts |
| Demand | Flat Poisson(0.5) | BMTC-calibrated hourly profile |

## Services

| Service | URL | Description |
|---|---|---|
| Dashboard | http://localhost:3000 | React + Leaflet live map |
| Backend API | http://localhost:8000/docs | FastAPI + WebSocket |
| MQTT | localhost:1883 | V2X broker (subscribe with mosquitto_sub) |
| PostgreSQL | localhost:5432 | Persistent storage |

## Monitor V2X Traffic

```bash
mosquitto_sub -h localhost -t "v2x/#" -v
```

## Paper
See `paper/ICCCNT_2026_EcoSync_V2X.md` — draft for ICCCNT 2026, IIT Delhi (June 28 – July 3, 2026). Student fee: ₹9,200.
