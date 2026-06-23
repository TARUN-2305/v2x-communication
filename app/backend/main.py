import os
import sys
import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from stable_baselines3 import PPO
from pydantic import BaseModel

# Add root directory to sys path so we can import test_env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from test_env import BengaluruBusEnv
from app.backend.reasoning import explain_action

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation state
sim_config = {
    "mode": "agentic",
    "reset_flag": False,
    "arrival_scale": 1.0   # P4-A: multiplier for passenger arrival rates
}

class ResetRequest(BaseModel):
    mode: str = "agentic"

class ConfigRequest(BaseModel):
    arrival_scale: float = 1.0

@app.post("/api/reset")
async def reset_simulation(req: ResetRequest):
    sim_config["mode"] = req.mode
    sim_config["reset_flag"] = True
    return {"status": "ok", "mode": req.mode}

@app.post("/api/config")
async def update_config(req: ConfigRequest):
    sim_config["arrival_scale"] = max(0.1, min(3.0, req.arrival_scale))
    return {"status": "ok", "arrival_scale": sim_config["arrival_scale"]}

@app.get("/api/results")
def get_results():
    results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'simulation_results.json'))
    try:
        with open(results_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    env = BengaluruBusEnv()
    obs, info = env.reset()
    
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'eco_sync_ppo.zip'))
    try:
        model = PPO.load(model_path)
    except Exception as e:
        await websocket.send_json({"error": "Failed to load model", "details": str(e)})
        return
        
    try:
        while True:
            if sim_config["reset_flag"]:
                obs, info = env.reset()
                sim_config["reset_flag"] = False

            bus_id = env.current_step % env.num_buses
            
            if sim_config["mode"] == "agentic":
                action, _ = model.predict(obs, deterministic=True)
                action = int(action)
            else:
                # Real static timetable logic: HOLD if bus ahead is too close
                gap_ahead = float(obs[0])
                action = 1 if gap_ahead <= 2 else 0
                
            # Capture telemetry of the current bus before taking the step
            curr_gap_ahead = float(obs[0])
            curr_gap_behind = float(obs[1])
            curr_queue_len = float(obs[2])
            
            obs, reward, done, truncated, info = env.step(action)
            
            econ_data = {
                "wait_cost": float(info.get("wait_cost", 0)),
                "fuel_cost": float(info.get("fuel_cost", 0)),
                "revenue": float(info.get("revenue", 0))
            }
            # Apply arrival scale from sim_config
            scale = sim_config.get("arrival_scale", 1.0)
            current_bus_stop = env.bus_pos[bus_id]
            env.stops[current_bus_stop]['queue_length'] = max(
                0, env.stops[current_bus_stop]['queue_length'] * scale
            )
            loop = asyncio.get_event_loop()
            explanation = await loop.run_in_executor(
                None, explain_action, bus_id, action, econ_data,
                curr_gap_ahead, curr_gap_behind, curr_queue_len
            )
            
            # Construct payload
            bus_pos_list = [{"id": int(k), "stop": int(v)} for k, v in env.bus_pos.items()]
            bus_load_list = [{"id": int(k), "load": int(v)} for k, v in env.bus_load.items()]
            stop_queues = [{"stop": int(k), "queue": int(v['queue_length'])} for k, v in env.stops.items()]
            
            payload = {
                "step": int(env.current_step),
                "mode": sim_config["mode"],
                "buses": bus_pos_list,
                "loads": bus_load_list,
                "stop_queues": stop_queues,
                "metrics": econ_data,
                "action_log": {
                    "bus_id": bus_id,
                    "action": action,
                    "explanation": explanation,
                    "reward": float(reward),
                    "bunching": int(info.get("bunching", 0))
                }
            }
            
            await websocket.send_json(payload)
            
            if done:
                obs, info = env.reset()
                
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        print("WebSocket Disconnected.")
