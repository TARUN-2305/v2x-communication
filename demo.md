# ECO-SYNC V2X — Demonstration Guide

This document provides a step-by-step guide to demonstrating the full capabilities of the **ECO-SYNC V2X (v2.0)** system.

---

## 🏗️ 1. Preparation & Setup

### API Keys & LLMs
To see the **Agentic V2X** reasoning (instead of `rule_fallback`), you need at least one of these:
1.  **Groq (Recommended)**: Get a free key at [console.groq.com](https://console.groq.com) and paste it into the `.env` file under `GROQ_API_KEY`.
2.  **Ollama (Local)**: Ensure [Ollama](https://ollama.com) is running on your machine and you have pulled the models:
    ```bash
    ollama pull gemma3:4b
    ollama pull phi3:latest
    ```

Ensure the system is running:
```bash
docker compose up -d
```
Access the dashboard at: `http://localhost:3000`

### Demonstration Workflow
1.  **Initial State**: Open the dashboard. It should show the map and empty metrics panels.
2.  **Start Simulation**: Click the **"Start"** button.
3.  **Observation**: Watch the 6 buses populate and move along Route 378 (Bengaluru).

---

## 📊 2. Key Features to Demonstrate

### Feature A: Multi-Agent V2V "Debates"
*   **What it is**: When two buses cluster (headway < 90s) near a stop, they "debate" using an LLM to decide on actions (HOLD, PROCEED, or SKIP_STOP).
*   **Where to look**: The **"V2X Debate Feed"** (right sidebar).
*   **Demo Tip**: Wait for a few minutes. You will see cards appearing with reasoning like *"Bus 1 holds — headway 45s below threshold"*.
*   **📸 Screenshot Recommendation**: Capture a cluster of buses on the map side-by-side with a detailed card in the **Debate Feed** showing the LLM's reasoning and the model used (e.g., `groq` or `ollama`).

### Feature B: V2I Traffic Management (TMC)
*   **What it is**: The system simulates a Traffic Management Centre (TMC) injecting events (signal failures, roadwork).
*   **Where to look**: The **"TMC Traffic Events (V2I)"** panel (right sidebar) and the map (events appear as markers).
*   **Demo Tip**: These appear stochastically. When one appears (High/Medium/Low severity), notice how the buses in that sector slow down.
*   **📸 Screenshot Recommendation**: A "High Severity" traffic event card showing a "signal failure" or "gridlock" description.

### Feature C: Agentic vs. Static Comparison
*   **What it is**: Toggle between "Agentic V2X" (AI-driven) and "Static Timetable" (baseline) to see the difference in performance.
*   **Where to look**: The **"Agentic V2X"** toggle in the top control bar and the **Metrics Charts** at the bottom.
*   **Demo Tip**: Start in "Static" mode for 2 minutes, then switch to "Agentic". Observe how the "Bunching Events" chart flattens out in Agentic mode.
*   **📸 Screenshot Recommendation**: The **"Avg Headway"** chart showing the line stabilizing around the 180s target line after switching to Agentic mode.

### Feature D: Real-Time Fleet Metrics
*   **What it is**: Live KPIs including Avg Headway, Total Decisions, Bunching Count, and Passengers Served.
*   **Where to look**: The **KPI Strip** at the top.
*   **📸 Screenshot Recommendation**: The top bar when "Passengers Served" is high (e.g., > 100) and "Bunching" is low (green color).

---

## 🛠️ 3. "Under the Hood" (CLI Demo)

To show the project is actually using industry-standard V2X protocols:

### 1. Raw MQTT Traffic
Open a terminal and run:
```bash
docker exec -it ecosync_mqtt mosquitto_sub -t "v2x/#" -v
```
*   **What it shows**: The raw BSM (Basic Safety Messages) and TIM (Traffic Information Messages) flowing through the system in real-time.

### 2. Database Persistence
Show that every decision is logged:
```bash
docker exec -it ecosync_postgres psql -U ecosync -d ecosync -c "SELECT stop_name, bus_1_action, llm_model FROM decisions ORDER BY ts DESC LIMIT 5;"
```
*   **What it shows**: A table of recent AI decisions stored in PostgreSQL.

---

## 📸 4. Screenshot Checklist

- [ ] **The "Hero" Shot**: Full dashboard with buses moving, a live debate in the feed, and the metrics charts populated.
- [ ] **The "Brain"**: Close-up of a V2X Debate card showing the reasoning text (ATIS signboard).
- [ ] **The "Crisis"**: A map view showing a traffic event marker and the corresponding traffic event card.
- [ ] **The "Proof"**: A terminal window showing the `mosquitto_sub` output (JSON messages) next to the dashboard.
- [ ] **The "Result"**: The **Bunching Events** chart showing a clear downward trend or low value.
