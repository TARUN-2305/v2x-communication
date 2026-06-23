import os
import pickle
import numpy as np
import gymnasium as gym
from gymnasium import spaces

class BengaluruBusEnv(gym.Env):
    def __init__(self):
        super(BengaluruBusEnv, self).__init__()
        
        # Load synthetic data
        data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data", "processed", "bengaluru_simulation_data.pkl"
        )
        with open(data_path, "rb") as f:
            self.data = pickle.load(f)
            
        self.num_stops = self.data['metadata']['num_stops']
        self.time_steps = self.data['metadata']['time_steps']
        self.arrival_rates = self.data['arrival_rates']
        self.delays_matrix = self.data['delays_matrix']
        self.eco_baselines = self.data['economic_baselines']
        
        self.num_buses = 5
        self.capacity = 80
        
        # Action space: 0: PROCEED, 1: HOLD, 2: SKIP
        self.action_space = spaces.Discrete(3)
        
        # Observation space: [gap_ahead, gap_behind, queue_length]
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(3,), dtype=np.float32)
        
        self.reset()
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.bus_pos = {i: (i * (self.num_stops // self.num_buses)) % self.num_stops for i in range(self.num_buses)}
        self.bus_load = {i: 0 for i in range(self.num_buses)}
        
        self.stops = {i: {'queue_length': 0} for i in range(self.num_stops)}
        
        return self._get_obs(0), {}
        
    def _get_obs(self, bus_id):
        ahead_id = (bus_id - 1) % self.num_buses
        behind_id = (bus_id + 1) % self.num_buses
        
        gap_ahead = (self.bus_pos[ahead_id] - self.bus_pos[bus_id]) % self.num_stops
        gap_behind = (self.bus_pos[bus_id] - self.bus_pos[behind_id]) % self.num_stops
        queue_len = self.stops[self.bus_pos[bus_id]]['queue_length']
        
        return np.array([gap_ahead, gap_behind, queue_len], dtype=np.float32)
        
    def compute_reward(self, bus_id, action):
        passengers_waiting = self.stops[self.bus_pos[bus_id]]['queue_length']
        passengers_onboard = self.bus_load[bus_id]
        
        # Calculate delays from synthetic matrix
        time_idx = min(self.current_step, self.time_steps - 1)
        segment = min(self.bus_pos[bus_id], self.num_stops - 2)
        delay_seconds = self.delays_matrix[segment, time_idx]
        self.delay_minutes = delay_seconds / 60.0
        
        # Skipping a stop avoids acceleration/deceleration/door delays, reducing delay by 30%
        if action == 2:
            self.delay_minutes *= 0.7
            
        idle_minutes = 1.0 if action == 1 else 0.0
        self.idle_or_delay_minutes = self.delay_minutes + idle_minutes
        
        # Micro: wait cost (Value of Time scaled 10x for proper economic penalty)
        wait_cost = passengers_waiting * 1.67 * self.delay_minutes * 10.0
        if action == 2:
            # Passenger inconvenience penalty for being passed by
            wait_cost += passengers_waiting * 15.0
            
        # Macro: BMTC operational fuel cost (Speed 15km/h = ₹0.83/min)
        fuel_cost = 0.83 * self.idle_or_delay_minutes
        
        # Revenue: ticket price ₹15 x boarded passengers (0 if skipping stop)
        if action == 2:
            boarded = 0
        else:
            boarded = min(passengers_waiting, self.capacity - passengers_onboard)
        revenue = 15 * boarded
        
        return revenue, wait_cost, fuel_cost

    def step(self, action):
        bus_id = self.current_step % self.num_buses
        stop = self.bus_pos[bus_id]
        
        time_idx = min(self.current_step, self.time_steps - 1)
        
        # Continuous passenger arrivals at all stops
        for s in range(self.num_stops):
            self.stops[s]['queue_length'] += self.arrival_rates[s, time_idx] / self.num_buses
            
        revenue, wait_cost, fuel_cost = self.compute_reward(bus_id, action)
        reward = revenue - wait_cost - fuel_cost
        
        # Check bunching to apply penalty
        ahead_id = (bus_id - 1) % self.num_buses
        gap_ahead = (self.bus_pos[ahead_id] - self.bus_pos[bus_id]) % self.num_stops
        if gap_ahead <= 1.0:
            reward -= 250.0  # Dynamic bunching penalty
            
        if action == 2: # SKIP
            # No boarding or alighting at this stop
            boarded = 0
            alighting = 0
        else:
            passengers_waiting = self.stops[stop]['queue_length']
            boarded = min(passengers_waiting, self.capacity - self.bus_load[bus_id])
            self.stops[stop]['queue_length'] -= boarded
            self.bus_load[bus_id] += boarded
            
            alighting = int(self.bus_load[bus_id] * 0.1)
            self.bus_load[bus_id] -= alighting
        
        if action == 0: # PROCEED
            self.bus_pos[bus_id] = (self.bus_pos[bus_id] + 1) % self.num_stops
        elif action == 1: # HOLD
            pass
        elif action == 2: # SKIP
            # Moves to the next stop but without boarding/alighting at the current one
            self.bus_pos[bus_id] = (self.bus_pos[bus_id] + 1) % self.num_stops
            
        self.current_step += 1
        done = self.current_step >= self.time_steps * self.num_buses
        
        next_bus_id = self.current_step % self.num_buses
        obs = self._get_obs(next_bus_id)
        
        info = {
            'revenue': float(revenue),
            'wait_cost': float(wait_cost),
            'fuel_cost': float(fuel_cost),
            'gap_ahead': float(obs[0]),
            'bunching': 1 if float(obs[0]) <= 1.0 else 0
        }
        
        return obs, float(reward), done, False, info

if __name__ == "__main__":
    env = BengaluruBusEnv()
    obs, info = env.reset()
    print("Environment Initialized Successfully.")
    print(f"Observation Space Shape: {env.observation_space.shape}")
    print(f"Action Space: {env.action_space}\n")

    print("Running 10 steps with random actions...")
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {i+1}: Action={action}, Reward={reward:.2f}, Obs={obs}")
