import json
import os

import polyline
import requests


STOPS = {
    "Kengeri TTMC": {"lat": 12.9176, "lng": 77.4838},
    "Uttarahalli": {"lat": 12.9056, "lng": 77.5457},
    "Konanakunte Cross": {"lat": 12.8858, "lng": 77.5738},
    "Gottigere": {"lat": 12.8574, "lng": 77.5949},
    "Electronic City": {"lat": 12.8452, "lng": 77.6601},
}


def fetch_route_geometry():
    coords_str = ";".join(f"{data['lng']},{data['lat']}" for data in STOPS.values())
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full"

    print("Fetching real road geometry from OSRM...")
    response = requests.get(osrm_url, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if payload["code"] != "Ok":
        raise RuntimeError(f"Failed to fetch route: {payload}")

    encoded_polyline = payload["routes"][0]["geometry"]
    route_coords = polyline.decode(encoded_polyline)

    map_data = {"stops": STOPS, "route_polyline": route_coords}

    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "route_378_map.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(map_data, file)

    print(f"Map extracted and saved to {output_path}.")
    print(f"Saved {len(route_coords)} geometry points.")
    return output_path, map_data


if __name__ == "__main__":
    fetch_route_geometry()
