# ECO-SYNC Transit AI Poster — Content Map
## Direct replacement guide for the RVCE poster template (AaaS Labs layout)

Go through this top to bottom — it follows the exact panel order in your template.

---

## HEADER

**Replace:**
- College name: keep as-is — "RV College of Engineering, Bengaluru – 560059."
- **Title:** `ECO-SYNC Transit AI: Agentic AI for Economic Dispatch and Anti-Bunching in Urban Transit`
- **Authors:** `Vikas K T | Vishwas V | Vijaykumar Yallappa Murkibhanvi | Tarun R`
- **USNs:** `1RV23CS286 | 1RV23CS293 | 1RV24CS424 | 1RV23CS271`

---

## INTRODUCTION

Replace the AaaS paragraph with:

> ECO-SYNC Transit AI is an intelligent headway control and economic dispatch framework for urban bus networks. Public transit corridors suffer severely from "bus bunching"—a dynamic instability where a minor delay at a stop increases passenger queues, slowing that vehicle further while trailing vehicles catch up. ECO-SYNC replaces rigid static timetables with a cooperative multi-agent Reinforcement Learning (RL) dispatcher. Trained in a custom Gymnasium environment representing Bengaluru's Outer Ring Road (ORR), the system optimizes a combined micro/macro-economic reward function. To make the RL decisions transparent, an explainable AI layer using Groq Llama-3.1 streams real-time, natural language operational justifications to transit operators.

---

## PROBLEM DEFINITION

Replace the AaaS bullet list with:

> Urban transit corridors encounter severe headway instability under stochastic passenger arrival rates and congestion.

1. **Bunching Cascade**: Minor delays snowball into bus bunching, leaving huge service gaps exceeding 20 minutes on high-density routes like Bengaluru ORR.
2. **Timetable Inflexibility**: Static schedules cannot adapt to dynamic congestion surges, signal delays, or sudden passenger queues.
3. **Economic Disalignment**: Existing headway control systems focus purely on minimizing spacing variance, ignoring the passenger Value of Time (VoT) and vehicle fuel idling costs.
4. **Black-Box AI Decisions**: Lack of interpretability in Deep RL actions prevents transit operators and drivers from trusting autonomous recommendations.
5. **Dashboard Fragmentation**: Transit agencies lack a single, real-time platform integrating Leaflet geospatial mapping, WebSocket telemetry, and explainable justifications.

---

## OBJECTIVES

Replace the AaaS numbered list with:

1. Formulate a high-fidelity Gymnasium simulation environment modeling a 30-stop circular transit route based on Bengaluru ORR road coordinates.
2. Design a multi-dimensional economic reward function that incorporates ticket revenues, passenger wait costs (Value of Time), fuel burn, and headway spacing penalties.
3. Train a stable Proximal Policy Optimization (PPO) model to output optimal proceed, hold, and skip recommendations at each stop.
4. Integrate an explainable AI (XAI) reasoning layer using the Groq Llama-3.1 API to justify dispatch actions in plain language.
5. Build a real-time web dashboard using FastAPI WebSockets and React.js to visualize live vehicle telemetry and economic KPIs.

---

## METHODOLOGY (the 6-step numbered flowchart)

The AaaS template has a **vertical 6-box numbered flowchart** (Requirements Collection → Workflow Creation → ... → Report Generation). Replace each box's title and bullets exactly as below — keep the same colored-box style and numbering 1–6.

**Box 1 — Geospatial Route Extraction**
- OSMnx graph extraction of Bengaluru Outer Ring Road
- 30 physical bus stops mapped with real coordinates
- Peak/off-peak Poisson passenger arrival distributions

**Box 2 — Gym Environment Formulation**
- Custom Gymnasium wrapper (`BengaluruBusEnv`)
- State space $S = [gap\_ahead, gap\_behind, queue\_length]$
- Action space $A = [0: PROCEED, 1: HOLD, 2: SKIP]$

**Box 3 — Economic Reward Design**
- $R = Revenue - Wait\_Cost - Fuel\_Cost - Bunching\_Penalty$
- Wait cost scaled by 10.0 to balance revenue (₹1.67/min VoT)
- Skipping stops incurs left-behind penalty; $gap\_ahead \le 1.0$ penalized by -250

**Box 4 — Agent Policy Training**
- Stable-Baselines3 PPO (actor-critic, MLP architecture)
- Offline model training for 100,000 steps
- Headway stabilization policy convergence validation

**Box 5 — Explainability & API Setup**
- FastAPI server handles async WebSockets at 1Hz
- Groq Llama-3.1 API generates plain-language justifications
- Deterministic rule-based fallback for offline resilience

**Box 6 — Dashboard Integration**
- React.js frontend with dynamic Leaflet map layer
- Real-time bus markers and stop passenger queue nodes
- Live cost-benefit analysis (CBA) charts

---

## TOOLS USED

The AaaS template has an icon grid with categories (Frontend / Backend / Security Tools / AI / DevOps). Replace categories and items as follows — keep same icon-grid visual style:

**Category 1 — Simulation & RL**
- Gymnasium (Gym)
- Stable-Baselines3 (PPO)
- OSMnx (GIS Graphs)
- OSRM Routing API

**Category 2 — Backend & AI**
- FastAPI (REST + WebSockets)
- Groq API (Llama-3.1)
- python-dotenv / uvicorn
- python-docx (reporting)

**Category 3 — Frontend & Maps**
- React.js / Vite
- Leaflet / react-leaflet
- Tailwind CSS
- Recharts (visuals)

**Category 4 — Data & Tools**
- NumPy / Pandas
- Matplotlib / Seaborn
- Git / GitHub
- VS Code / Jupyter

**Bottom banner text** (replacing "Built for Security..."):
> Built for Transit Efficiency. Formally modeled, economically optimized, and explainable in real-time — open source at github.com/TARUN-2305/v2x-communication

---

## RESULTS AND DISCUSSIONS

### Top "KEY RESULTS" icon row (6 boxes in AaaS — keep 6, replace each)

| Icon box | Big number | Label |
|---|---|---|
| 1 | **+100.4%** | Net Efficiency Gain (ENV) |
| 2 | **97.3%** | Passenger Wait Cost Saved |
| 3 | **Zero** | Bunching Cascades (100% Resolved) |
| 4 | **0.22** | Gini Equity Index (from 1.16) |
| 5 | **+₹713,737** | Net Economic Savings |
| 6 | **1Hz** | Live Telemetry WebSocket Latency |

### "RESULT HIGHLIGHTS" bar chart

Replace the AaaS bar chart with a **4-bar comparison chart** — comparing Static Timetable vs. Agentic PPO:

| Bar | Value (₹) |
|---|---|
| Static Wait Cost | 733,858.41 |
| Agentic Wait Cost | 20,118.73 |
| Static Net ENV | -710,981.19 |
| Agentic Net ENV | +2,756.42 |

*(Note: Under the Static Timetable, bunching leads to massive passenger queues at gaps, exploding wait costs. The Agentic AI uses strategic holds and skips to keep buses evenly spaced, reducing wait costs and turning a net operational loss into a net benefit.)*

### "DISCUSSIONS" box

Replace AaaS discussion bullets with:

- **Headway Stabilization**: PPO agent coordinates spacing dynamically, eliminating the bunching cascade.
- **Strategic Holding & Skipping**: HOLD actions are triggered when trailing buses get too close, while SKIP actions allow delayed buses to catch up.
- **Economic Feasibility**: The 97.3% passenger wait-time savings vastly outweigh the minor +0.55% idling fuel increase.
- **Explainable Operations**: Real-time justifications explain autonomous holds/skips, establishing driver and operator trust.

### "Overall Outcome" line at the bottom

> ECO-SYNC Transit AI demonstrates that aligning machine learning rewards with transportation micro-economics stabilizes headways, offering a transparent, explainable solution to bus bunching.

---

## CONCLUSIONS

Replace the AaaS paragraph with:

> ECO-SYNC Transit AI successfully demonstrates that urban transit headway control and anti-bunching can be effectively resolved by framing scheduling as a micro-economic optimization problem. By coordinating proceed, hold, and skip actions, the PPO agent stabilized spacing along a simulated 30-stop Outer Ring Road route. Over a 250-episode Monte Carlo evaluation, the agent achieved a 100.4% Net Efficiency Gain and reduced passenger wait costs by 97.3% (saving ₹713,739) compared to the static baseline. Integrating Groq Llama-3.1 provides explainable justifications in real-time, bridging the gap between deep reinforcement learning models and real-world municipal transit operators.

---

## OUTCOME OF THE WORK

Replace the AaaS paragraph with:

> A fully functional explainable transit dispatch prototype consisting of: (1) Custom Gymnasium environment mapping Bengaluru ORR stops and Poisson arrivals; (2) Trained PPO model achieving headway stability across 250 episodes; (3) FastAPI server streaming telemetry via WebSockets; (4) React.js dashboard with interactive Leaflet mapping, live economic charts, and real-time Llama-3.1 justifications; and (5) A research manuscript titled "ECO-SYNC: Explainable RL for Economic Headway Regulation in Public Transit" targeted for submission to the IEEE Transactions on Intelligent Transportation Systems.

---

## REFERENCES

Replace the 5 AaaS references with:

```
[1] Newell, G. F., and Potts, R. B. (1964). "Maintaining a bus schedule." Proc. ARRB, 2(1).
[2] Daganzo, C. F. (2009). "Headway control with delayed information." Trans. Res. Part B, 43(5).
[3] Schulman, J., et al. (2017). "Proximal Policy Optimization algorithms." arXiv:1707.06347.
[4] Rafferty, P. (2018). "Valuing commuter time in public transit networks." J. Pub. Trans., 21(2).
[5] Boeing, G. (2017). "OSMnx: street networks." Computers, Env. and Urban Systems, vol. 65.
```

---

## MENTOR

Replace with:

> Dr. Sunil S, Department of Civil Engineering, RV College of Engineering, Bengaluru.

---

## IMAGE/FIGURE PLACEMENTS

Your template has image placeholders. Use the following figures from the project assets directory for high-resolution uploads into Canva:

| Panel | Best figure to drop in |
|---|---|
| **Methodology** (Visual Area) | System Flow / Architecture schematic showing: Env -> PPO Action -> WebSocket Stream -> React Map & Groq Explanations |
| **Results** (Visual Area) | `chart_headway_light.png` (Stop performance comparison) |
| **Results** (Secondary Area) | `chart_waitcost_light.png` (Cumulative wait cost curves) |

---

## QUICK CHECKLIST

- [ ] Header: Project title, 4 authors, 4 USNs, mentor name.
- [ ] Introduction paragraph (explains bunching and ECO-SYNC solution).
- [ ] Problem Definition (5 points on bunching, static timetables, and economic disalignment).
- [ ] Objectives (5 points outlining route formulation, reward, PPO agent, and XAI).
- [ ] Methodology (6 flowchart boxes with ORR extraction, state/action spaces, PPO, and WebSockets).
- [ ] Tools Used (4 categories with Gym, FastAPI, React/Leaflet, Groq API, and GitHub link).
- [ ] Results: 6 KPI boxes, 4-bar comparison chart, discussion bullets, and bottom outcome line.
- [ ] Conclusions paragraph summarizing the economics-aligned RL results.
- [ ] Outcome of the work paragraph detailing the TMS dashboard and IEEE paper plan.
- [ ] References (5 standard citations).
- [ ] Mentor line (Dr. Sunil S, Dept. of Civil Engineering, RVCE).
- [ ] Uploaded figures (Headway stop performance and cumulative wait cost charts).
