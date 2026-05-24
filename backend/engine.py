"""
ECO-SYNC V2X — Production Engine
Wraps original RouteSimulator, adds:
  - N buses (default 6) spaced evenly on the 1203-point OSRM polyline
  - Real headway calculation in seconds (speed-aware)
  - Bunching detection (headway < 60s)
  - Agentic vs Static comparison mode
  - Ollama fallback when Groq fails
  - MQTT BSM/DEBATE/METRICS publishing
  - PostgreSQL persistence (sampled every 5 ticks)
  - WebSocket broadcast
"""
import asyncio
import json
import os
import random
import time
import uuid
from typing import Optional, Callable

import httpx
import numpy as np
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

# Calibrated Bengaluru ORR traffic profile (km/h per hour-of-day)
SPEED_PROFILE = {
    0: 38, 1: 40, 2: 40, 3: 38, 4: 35, 5: 30,
    6: 22, 7: 14, 8: 12, 9: 16, 10: 22, 11: 24,
    12: 22, 13: 20, 14: 22, 15: 20, 16: 15, 17: 12,
    18: 14, 19: 18, 20: 22, 21: 26, 22: 30, 23: 36,
}

# Route 378: 34.4 km, 1203 polyline points
ROUTE_KM  = 34.4
ROUTE_PTS = 1203

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # radius of Earth in meters
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1-a))

# Calibrated from BMTC boarding data (passengers arriving per minute at stop)
STOP_ARRIVAL_RATES = {
    "Kengeri TTMC":      3.5,   # major terminus
    "Uttarahalli":       1.8,
    "Konanakunte Cross": 2.2,
    "Gottigere":         1.5,
    "Electronic City":   3.0,   # IT hub terminus
}

TRAFFIC_EVENTS = [
    {"location": "Uttarahalli",    "severity": "High",   "desc": "ORR signal failure — heavy queue"},
    {"location": "Konanakunte Cross","severity":"Medium", "desc": "BBMP pothole repair, single lane"},
    {"location": "Gottigere",       "severity": "Low",   "desc": "School dismissal pedestrian surge"},
    {"location": "Silk Board area", "severity": "High",  "desc": "Junction gridlock, all lanes blocked"},
]

BUS_COLORS = ["#00D4FF","#FF6B35","#7FFF00","#FF1493","#FFD700","#EE82EE"]


class ProductionSimulator:
    def __init__(self, base_sim, agent_fn, map_data, storage, v2x, ws_clients):
        self._BaseSim   = base_sim       # class (not instance) — we rebuild for each session
        self._agent_fn  = agent_fn
        self._map_data  = map_data
        self._storage   = storage
        self._v2x       = v2x
        self._ws        = ws_clients

        self.running     = False
        self.mode        = "agentic"
        self.session_id: Optional[uuid.UUID] = None

        self._sim        = None          # base RouteSimulator instance
        self._buses      = []            # production bus list (extends base)
        self._stops      = {}            # {name: {waiting, lat, lng}}
        self._route      = []            # polyline [[lat,lng],…]
        self._segment_m  = []            # distance in meters for each segment
        self._stop_idx   = {}            # stop_name → nearest path_index
        self._traffic    = []
        self._tmc_ttl    = 0
        self._debate_history = []
        self._tick_count = 0
        self._metrics    = {}
        self._task: Optional[asyncio.Task] = None
        self._last_debate_key = None

        # Ollama client
        self._http = httpx.AsyncClient(timeout=float(os.getenv("LLM_TIMEOUT","8")))

    # ── Lifecycle ──────────────────────────────────────────────────────────────
    async def start(self, num_buses: int = 6, mode: str = "agentic") -> uuid.UUID:
        if self.running:
            await self.stop()

        self.mode = mode
        self.session_id = uuid.uuid4()
        self._debate_history = []
        self._tick_count = 0
        self._metrics = {
            "tick": 0, "bunching": 0, "decisions": 0,
            "holds": 0, "skips": 0, "proceeds": 0,
            "avg_headway_s": 180.0, "variance": 0.0,
            "passengers_served": 0, "mode": mode,
        }

        # Fresh base simulator (loads the saved OSRM polyline)
        self._sim = self._BaseSim()
        self._route = self._sim.route_path          # [[lat,lng],…]
        n = len(self._route)

        # Pre-compute segment distances
        self._segment_m = [0.0] * n
        for i in range(n - 1):
            p1, p2 = self._route[i], self._route[i+1]
            self._segment_m[i] = haversine(p1[0], p1[1], p2[0], p2[1])

        # Pre-compute stop→path index map
        stops_data = self._map_data["stops"]
        for sname, sc in stops_data.items():
            self._stop_idx[sname] = min(
                range(n),
                key=lambda i: (self._route[i][0]-sc["lat"])**2 + (self._route[i][1]-sc["lng"])**2
            )

        # Init passenger queues from calibrated rates
        self._stops = {
            name: {"waiting": random.randint(5, 20), "lat": sc["lat"], "lng": sc["lng"]}
            for name, sc in stops_data.items()
        }

        # Build N buses (bi-directional)
        self._buses = []
        for i in range(num_buses):
            # Half buses go direction 1 (Kengeri -> EC), half go -1 (EC -> Kengeri)
            direction = 1 if i < (num_buses // 2) else -1
            pi = 0 if direction == 1 else n - 1
            
            # Stagger start positions slightly to avoid instant stack
            if direction == 1:
                pi = (i * (n // num_buses)) % n
            else:
                pi = (n - 1) - ((i - num_buses // 2) * (n // num_buses)) % n

            self._buses.append({
                "id": f"Bus_{i+1}",
                "path_index": pi,
                "partial_dist": 0.0,   # progress within current segment
                "passengers": random.randint(8, 45),
                "status": "moving",
                "direction": direction,
                "dwell_ticks": 0,
                "color": BUS_COLORS[i % len(BUS_COLORS)],
                "action": "PROCEED",
                "headway_ahead_s": 180,
                "headway_behind_s": 180,
                "lat": self._route[pi][0],
                "lng": self._route[pi][1],
            })

        self._traffic = []
        self._tmc_ttl = 0

        # Persist session
        await self._storage.create_session(self.session_id, mode, num_buses)
        self.running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(f"▶ Session {self.session_id} | {num_buses} buses | mode={mode}")
        return self.session_id

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try: await self._task
            except asyncio.CancelledError: pass
        if self.session_id:
            await self._storage.close_session(self.session_id)
        logger.info("⏹ Simulation stopped")

    async def toggle_mode(self) -> str:
        self.mode = "static" if self.mode == "agentic" else "agentic"
        self._metrics["mode"] = self.mode
        logger.info(f"Mode → {self.mode}")
        return self.mode

    # ── Main loop ──────────────────────────────────────────────────────────────
    async def _loop(self):
        speed = float(os.getenv("SIM_SPEED", "1.0"))
        interval = 1.0 / speed
        while self.running:
            t0 = time.monotonic()
            try:
                await self._tick()
            except Exception as e:
                logger.error(f"Tick error: {e}")
            elapsed = time.monotonic() - t0
            await asyncio.sleep(max(0.0, interval - elapsed))

    async def _tick(self):
        n  = len(self._route)
        m  = self._metrics
        m["tick"] += 1
        self._tick_count += 1
        hour = (7 + self._tick_count // 3600) % 24  # sim starts at 7 AM

        # ── Passenger arrivals (Poisson, calibrated to BMTC data) ─────────────
        for sname, sdata in self._stops.items():
            rate = STOP_ARRIVAL_RATES.get(sname, 1.5)
            # Peak hour multiplier
            if hour in (7, 8, 17, 18): rate *= 2.2
            elif hour in (9, 16, 19):  rate *= 1.5
            arrivals = int(np.random.poisson(rate / 60.0))   # per second
            sdata["waiting"] = min(sdata["waiting"] + arrivals, 80)

        # ── Traffic event (V2I from TMC, ~4% chance/tick) ─────────────────────
        if self._tmc_ttl <= 0:
            self._traffic = []
            if random.random() < 0.04:
                ev = random.choice(TRAFFIC_EVENTS).copy()
                self._traffic = [ev]
                self._tmc_ttl = random.randint(60, 300)
                # Publish V2I TIM message
                self._v2x.publish("v2x/v2i/tmc/tim", {
                    "type": "TIM", "event": ev, "ts": time.time()
                })
                # Persist
                await self._storage.log_traffic(self.session_id, ev)
        else:
            self._tmc_ttl -= 1

        # ── Move buses (Distance-based physics + Dwell Time) ───────────────────
        base_speed_kmh = SPEED_PROFILE.get(hour, 20)
        for bus in self._buses:
            # 1. Check Dwell / Hold
            if bus.get("hold_ticks", 0) > 0:
                bus["hold_ticks"] -= 1
                bus["action"] = "HOLD"
                continue
            if bus.get("dwell_ticks", 0) > 0:
                bus["dwell_ticks"] -= 1
                bus["action"] = "DWELL"
                continue

            # 2. Calculate speed
            spd_kmh = base_speed_kmh * random.uniform(0.8, 1.2)
            if self._traffic:
                ev = self._traffic[0]
                if ev["severity"] == "High":   spd_kmh *= 0.4
                elif ev["severity"] == "Medium": spd_kmh *= 0.65
            spd_kmh = max(5, min(spd_kmh, 55))
            spd_ms  = spd_kmh * 1000 / 3600

            # 3. Distance-based advancement
            dist_to_move = spd_ms  # we move spd_ms meters in this 1s tick
            while dist_to_move > 0:
                curr_idx = bus["path_index"]
                # Determine next segment
                if bus["direction"] == 1:
                    if curr_idx >= n - 1: # Terminus bounce
                        bus["direction"] = -1
                        bus["passengers"] = 0 # Drop everyone at end
                        bus["dwell_ticks"] = 15
                        break
                    seg_len = self._segment_m[curr_idx]
                    rem_in_seg = seg_len - bus["partial_dist"]
                    move = min(dist_to_move, rem_in_seg)
                    bus["partial_dist"] += move
                    dist_to_move -= move
                    if bus["partial_dist"] >= seg_len:
                        bus["path_index"] += 1
                        bus["partial_dist"] = 0
                else:
                    if curr_idx <= 0: # Terminus bounce
                        bus["direction"] = 1
                        bus["passengers"] = 0
                        bus["dwell_ticks"] = 15
                        break
                    seg_len = self._segment_m[curr_idx - 1]
                    rem_in_seg = bus["partial_dist"] if bus["partial_dist"] > 0 else seg_len
                    move = min(dist_to_move, rem_in_seg)
                    bus["partial_dist"] = (bus["partial_dist"] or seg_len) - move
                    dist_to_move -= move
                    if bus["partial_dist"] <= 0:
                        bus["path_index"] -= 1
                        bus["partial_dist"] = 0

            pi = bus["path_index"]
            bus["lat"] = self._route[pi][0]
            bus["lng"] = self._route[pi][1]
            bus["action"] = "PROCEED"

            # 4. Board/alight at stops (now with Dwell Time)
            for sname, sidx in self._stop_idx.items():
                if abs(pi - sidx) <= 1: # tighter stop detection
                    sdata = self._stops[sname]
                    board = min(sdata["waiting"], max(0, 60 - bus["passengers"]))
                    alight = max(0, int(bus["passengers"] * random.uniform(0.08, 0.18)))
                    
                    if board > 0 or alight > 0:
                        bus["passengers"] = max(0, bus["passengers"] - alight) + board
                        sdata["waiting"] = max(0, sdata["waiting"] - board)
                        m["passengers_served"] += board
                        # Add dwell time: ~1s per pax boarding/alighting
                        bus["dwell_ticks"] = max(3, int((board + alight) * 0.8))
                        break # only one stop per tick

        # ── Compute headways (Direction-aware) ────────────────────────────────
        for bus in self._buses:
            # Find the next bus in the SAME direction
            others = [b for b in self._buses if b["id"] != bus["id"] and b["direction"] == bus["direction"]]
            if not others:
                bus["headway_ahead_s"] = 180
                bus["headway_behind_s"] = 180
                continue
            
            # Distance along route to next bus
            if bus["direction"] == 1:
                ahead = min([b for b in others if b["path_index"] > bus["path_index"]] or [min(others, key=lambda b: b["path_index"])], 
                            key=lambda b: (b["path_index"] - bus["path_index"]) % n)
                gap_pts = (ahead["path_index"] - bus["path_index"]) % n
            else:
                ahead = min([b for b in others if b["path_index"] < bus["path_index"]] or [max(others, key=lambda b: b["path_index"])], 
                            key=lambda b: (bus["path_index"] - b["path_index"]) % n)
                gap_pts = (bus["path_index"] - ahead["path_index"]) % n
            
            # Approx seconds (using avg speed)
            spd_km = base_speed_kmh or 20
            # Rough distance estimate (m_per_step approx 28.6)
            gap_m = gap_pts * 28.6
            bus["headway_ahead_s"] = int(gap_m / (spd_km * 1000 / 3600))
            # (behind is just ahead for the other bus)

        # ── Agentic debates (only in agentic mode) ────────────────────────────
        latest_debate = None
        if self.mode == "agentic":
            latest_debate = await self._maybe_debate()

        # ── Metrics ───────────────────────────────────────────────────────────
        headways = [b["headway_ahead_s"] for b in self._buses]
        m["avg_headway_s"]  = float(np.mean(headways))
        m["variance"]       = float(np.var(headways))
        bunching = sum(1 for h in headways if h < 60)
        if bunching:
            m["bunching"] += bunching

        # Persist every 5 ticks
        if self._tick_count % 5 == 0:
            await self._storage.save_metrics(self.session_id, m)

        # Publish BSMs
        for bus in self._buses:
            self._v2x.publish(f"v2x/v2v/{bus['id']}/bsm", {
                "type": "BSM", "bus_id": bus["id"],
                "lat": bus["lat"], "lng": bus["lng"],
                "path_index": bus["path_index"],
                "direction": bus["direction"],
                "passengers": bus["passengers"],
                "headway_ahead_s": bus["headway_ahead_s"],
                "action": bus["action"],
                "ts": time.time(),
            })

        # ── Broadcast to all WebSocket clients ───────────────────────────────
        payload = self._build_payload(latest_debate)
        dead = set()
        for ws in list(self._ws):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)
        self._ws -= dead

    # ── V2V Agent Debate ──────────────────────────────────────────────────────
    async def _maybe_debate(self) -> Optional[dict]:
        major_stops = list(self._stop_idx.keys())
        for bus in self._buses:
            for sname in major_stops:
                sidx = self._stop_idx[sname]
                if abs(bus["path_index"] - sidx) > 6:
                    continue
                # Find the bus behind this one
                following = self._find_following(bus)
                if not following:
                    continue
                key = f"{bus['id']}:{following['id']}:{sname}:{bus['path_index'] // 20}"
                if key == self._last_debate_key:
                    continue
                self._last_debate_key = key
                return await self._run_debate(bus, following, sname)
        return None

    def _find_following(self, lead):
        # Must be in same direction
        candidates = [b for b in self._buses if b["id"] != lead["id"]
                      and b["direction"] == lead["direction"]]
        if not candidates:
            return None
        
        if lead["direction"] == 1:
            # Traveling Kengeri -> EC: follower is at smaller index
            followers = [b for b in candidates if b["path_index"] <= lead["path_index"]]
            if not followers: # wrap around
                return max(candidates, key=lambda b: b["path_index"])
            return max(followers, key=lambda b: b["path_index"])
        else:
            # Traveling EC -> Kengeri: follower is at larger index
            followers = [b for b in candidates if b["path_index"] >= lead["path_index"]]
            if not followers: # wrap around
                return min(candidates, key=lambda b: b["path_index"])
            return min(followers, key=lambda b: b["path_index"])

    async def _run_debate(self, bus1, bus2, stop_name) -> dict:
        stop_state = {"name": stop_name, **self._stops[stop_name]}
        traffic    = self._traffic or [{"location": stop_name, "severity": "Normal"}]
        t0 = time.monotonic()

        try:
            raw = await self._call_llm(bus1, bus2, stop_state, traffic)
            decision = json.loads(raw)
            model_used = "groq" if os.getenv("GROQ_API_KEY") else "ollama"
        except Exception as e:
            logger.warning(f"LLM failed: {e}. Using rule-based fallback.")
            decision = self._rule_fallback(bus1, bus2, stop_state)
            model_used = "rule_fallback"

        latency_ms = int((time.monotonic() - t0) * 1000)

        # Apply actions
        self._apply_action(bus1, decision.get("bus_1_action", "PROCEED"))
        self._apply_action(bus2, decision.get("bus_2_action", "PROCEED"))

        m = self._metrics
        m["decisions"] += 1
        a1 = decision.get("bus_1_action","PROCEED")
        if a1 == "HOLD":     m["holds"]    += 1
        elif a1 == "SKIP_STOP": m["skips"] += 1
        else:                m["proceeds"] += 1

        event = {
            "stop": stop_name,
            "bus_1_id": bus1["id"],
            "bus_2_id": bus2["id"],
            "decision": decision,
            "model": model_used,
            "latency_ms": latency_ms,
            "ts": time.time(),
        }
        self._debate_history.append(event)
        self._debate_history = self._debate_history[-20:]

        # Publish V2V debate message
        self._v2x.publish(f"v2x/v2v/debate/{bus1['id']}/{bus2['id']}", {
            "type": "DEBATE", **event
        })

        # Publish ATIS signboard
        self._v2x.publish(f"v2x/atis/{stop_name.replace(' ','_')}", {
            "type": "ATIS",
            "stop": stop_name,
            "message": decision.get("reasoning_for_signboard", ""),
            "bus_1_action": decision.get("bus_1_action"),
            "bus_2_action": decision.get("bus_2_action"),
            "direction": bus1["direction"]
        })

        # Persist decision
        await self._storage.save_decision(
            self.session_id, stop_name, bus1["id"], bus2["id"],
            decision.get("bus_1_action"), decision.get("bus_2_action"),
            decision.get("reasoning_for_signboard",""), model_used, latency_ms,
            bus1.get("headway_ahead_s", 0), 0
        )
        return event

    async def _call_llm(self, bus1, bus2, stop_state, traffic) -> str:
        """Groq primary → Ollama gemma3:4b → Ollama phi3 → rule fallback"""
        # Build user prompt identical to original 03_agent_debate.py
        prompt_args = (bus1, bus2, stop_state, traffic)

        # 1. Groq
        if os.getenv("GROQ_API_KEY"):
            try:
                # Reuse original agent function (sync → run in executor)
                loop = asyncio.get_event_loop()
                raw = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: self._agent_fn(*prompt_args)),
                    timeout=8.0
                )
                return raw
            except Exception as e:
                logger.warning(f"Groq failed ({e}), trying Ollama…")

        # 2. Ollama
        ollama_host = os.getenv("ECOSYNC_OLLAMA_HOST", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        for model in [
            os.getenv("OLLAMA_PRIMARY",  "gemma3:4b"),
            os.getenv("OLLAMA_FALLBACK", "phi3:latest"),
        ]:
            try:
                sys_p, usr_p = self._build_ollama_prompts(bus1, bus2, stop_state, traffic)
                resp = await self._http.post(
                    f"{ollama_host}/api/chat",
                    json={
                        "model": model,
                        "format": "json",
                        "stream": False,
                        "options": {"temperature": 0.2, "num_predict": 150},
                        "messages": [
                            {"role": "system",  "content": sys_p},
                            {"role": "user",    "content": usr_p},
                        ]
                    },
                    timeout=10.0
                )
                content = resp.json()["message"]["content"]
                logger.info(f"Ollama {model} responded in {resp.elapsed.total_seconds()*1000:.0f}ms")
                return content
            except Exception as e:
                logger.warning(f"Ollama {model} failed: {e}")

        raise RuntimeError("All LLMs unavailable")

    def _build_ollama_prompts(self, bus1, bus2, stop, traffic):
        sys_p = (
            "You are the V2X routing intelligence for BMTC Route 378 Bengaluru.\n"
            "Return ONLY a raw JSON object with keys: "
            "bus_1_action (PROCEED|HOLD|SKIP_STOP), "
            "bus_2_action (PROCEED|HOLD|SKIP_STOP), "
            "reasoning_for_signboard (short string).\n"
            "No markdown. No explanation. Pure JSON."
        )
        usr_p = (
            f"Bus {bus1['id']} approaches {stop['name']} with {bus1['passengers']} pax. "
            f"Headway ahead: {bus1.get('headway_ahead_s',180)}s. "
            f"Bus {bus2['id']} follows with {bus2['passengers']} pax. "
            f"Waiting at stop: {stop['waiting']}. "
            f"Traffic: {json.dumps(traffic)}. "
            "Decide actions for both buses."
        )
        return sys_p, usr_p

    def _rule_fallback(self, bus1, bus2, stop) -> dict:
        h = bus1.get("headway_ahead_s", 180)
        w = stop.get("waiting", 0)
        if h < 60 and w < 15:
            return {"bus_1_action": "HOLD", "bus_2_action": "PROCEED",
                    "reasoning_for_signboard": f"Bus {bus1['id']} holds — headway {h}s below threshold."}
        elif h < 90 and w > 20:
            return {"bus_1_action": "PROCEED", "bus_2_action": "HOLD",
                    "reasoning_for_signboard": f"High demand at {stop['name']} — both buses slow."}
        return {"bus_1_action": "PROCEED", "bus_2_action": "PROCEED",
                "reasoning_for_signboard": "Nominal flow — both buses proceed on schedule."}

    def _apply_action(self, bus, action: str):
        bus["action"] = action
        if action == "HOLD":
            bus["hold_ticks"] = 45      # ~45 s hold
        elif action == "SKIP_STOP":
            bus["path_index"] = (bus["path_index"] + 20) % len(self._route)

    # ── Snapshot ───────────────────────────────────────────────────────────────
    def _build_payload(self, latest_debate) -> dict:
        return {
            "stops": self._stops,
            "buses": self._buses,
            "traffic": self._traffic,
            "latest_debate": latest_debate,
            "debate_history": self._debate_history,
            "metrics": self._metrics,
            "mode": self.mode,
            "session_id": str(self.session_id) if self.session_id else None,
            "tick": self._tick_count,
        }

    def get_snapshot(self) -> dict:
        return self._build_payload(None)
