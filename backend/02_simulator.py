import json
import os
import random

import numpy as np


class RouteSimulator:
    def __init__(self):
        map_path = os.path.join(os.path.dirname(__file__), "..", "data", "route_378_map.json")
        with open(map_path, "r", encoding="utf-8") as file:
            self.map_data = json.load(file)

        self.route_path = self.map_data["route_polyline"]
        self.stops = {
            name: {"waiting": 0, "lat": data["lat"], "lng": data["lng"]}
            for name, data in self.map_data["stops"].items()
        }

        last_index = max(0, len(self.route_path) - 1)
        bus_2_start = min(100, last_index)
        self.buses = [
            {
                "id": "Bus_1",
                "path_index": 0,
                "passengers": 45,
                "status": "moving",
                "direction": 1,
            },
            {
                "id": "Bus_2",
                "path_index": bus_2_start,
                "passengers": 10,
                "status": "moving",
                "direction": 1,
            },
        ]
        self.traffic_events = []

    def tick(self):
        for stop in self.stops:
            self.stops[stop]["waiting"] += int(np.random.poisson(0.5))

        if random.random() < 0.05 and not self.traffic_events:
            self.traffic_events.append({"location": "Uttarahalli", "severity": "High"})

        for bus in self.buses:
            if bus["status"] == "moving":
                bus["path_index"] += bus["direction"]
                bus["path_index"] = max(0, min(bus["path_index"], len(self.route_path) - 1))

        return self.get_state()

    def get_state(self):
        for bus in self.buses:
            bus["lat"] = self.route_path[bus["path_index"]][0]
            bus["lng"] = self.route_path[bus["path_index"]][1]

        return {"stops": self.stops, "buses": self.buses, "traffic": self.traffic_events}


if __name__ == "__main__":
    simulator = RouteSimulator()
    final_state = None
    for step in range(5):
        final_state = simulator.tick()
        print(f"Tick {step + 1}: {[(bus['id'], bus['path_index']) for bus in final_state['buses']]}")

    print(json.dumps(final_state, indent=2))
