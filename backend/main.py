"""
ECO-SYNC V2X — Production Backend v2.0
Extends original 3-module architecture with Docker, MQTT, Postgres, 6 buses, Ollama fallback.
"""
import asyncio
import importlib.util
import json
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

load_dotenv()

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_PATH  = BASE_DIR / "data" / "route_378_map.json"
BACKEND_DIR= BASE_DIR / "backend"

def _load(name, file):
    path = BACKEND_DIR / file
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

sim_mod   = _load("sim",   "02_simulator.py")
agent_mod = _load("agent", "03_agent_debate.py")

from backend.db.storage    import Storage
from backend.mqtt.v2x_broker import V2XBroker
from backend.engine        import ProductionSimulator

storage : Optional[Storage]             = None
v2x     : Optional[V2XBroker]          = None
engine  : Optional[ProductionSimulator] = None
ws_clients: set[WebSocket]              = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global storage, v2x, engine
    logger.info("🚀 ECO-SYNC V2X Backend v2.0")

    storage = Storage(os.getenv("DATABASE_URL", ""))
    await storage.init()

    v2x = V2XBroker(
        host=os.getenv("MQTT_HOST", "localhost"),
        port=int(os.getenv("MQTT_PORT", "1883")),
    )
    await v2x.connect()

    engine = ProductionSimulator(
        base_sim=sim_mod.RouteSimulator,
        agent_fn=agent_mod.trigger_v2x_debate,
        map_data=json.loads(DATA_PATH.read_text()),
        storage=storage,
        v2x=v2x,
        ws_clients=ws_clients,
    )
    app.state.engine = engine
    logger.info("✅ Ready — http://localhost:8000/docs")
    yield
    await engine.stop()
    await v2x.disconnect()


app = FastAPI(title="ECO-SYNC V2X", version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/map")
async def get_map():
    return json.loads(DATA_PATH.read_text())


@app.post("/api/simulation/start")
async def start(num_buses: int = 6, mode: str = "agentic"):
    sid = await engine.start(num_buses=num_buses, mode=mode)
    return {"status": "started", "session_id": str(sid), "mode": mode}


@app.post("/api/simulation/stop")
async def stop():
    await engine.stop()
    return {"status": "stopped"}


@app.post("/api/simulation/mode")
async def toggle_mode():
    return {"mode": await engine.toggle_mode()}


@app.get("/api/simulation/state")
async def state():
    return engine.get_snapshot()


@app.get("/api/metrics/history")
async def metrics_history(limit: int = 60):
    return await storage.get_metrics(str(engine.session_id) if engine.session_id else None, limit)


@app.get("/api/decisions/history")
async def decisions_history(limit: int = 20):
    return await storage.get_decisions(str(engine.session_id) if engine.session_id else None, limit)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "running": engine.running if engine else False,
        "mode": engine.mode if engine else None,
        "mqtt": v2x.connected if v2x else False,
        "ws_clients": len(ws_clients),
    }


@app.websocket("/ws/live")
async def live_stream(websocket: WebSocket):
    await websocket.accept()
    ws_clients.add(websocket)
    logger.info(f"WS connected — {len(ws_clients)} clients")
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.send_text('{"type":"heartbeat"}')
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(websocket)
        logger.info(f"WS disconnected — {len(ws_clients)} clients")
