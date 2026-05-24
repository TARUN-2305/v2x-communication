import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = """
You are the central V2X routing intelligence for BMTC Route 378 in Bengaluru South.
Your job is to compute the economic trade-off for two buses using only:
- passenger wait time at the stop
- traffic delay ahead
- current passenger load on each bus

You must decide the operational action for Bus 1 and Bus 2.

Return ONLY a raw JSON object with exactly these keys:
{"bus_1_action":"PROCEED|HOLD|SKIP_STOP","bus_2_action":"PROCEED|HOLD|SKIP_STOP","reasoning_for_signboard":"short rider-facing explanation"}

Rules:
- Output valid JSON only.
- Do not wrap the JSON in markdown.
- Do not add commentary before or after the JSON.
- Keep reasoning_for_signboard concise and operational.
""".strip()


def _get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to a .env file or the environment.")
    return Groq(api_key=api_key)


def trigger_v2x_debate(bus_1_state, bus_2_state, stop_state, traffic_state):
    client = _get_client()
    traffic_summary = json.dumps(traffic_state)
    user_prompt = f"""
Bus 1 is approaching {stop_state['name']} with {bus_1_state['passengers']} passengers.
Bus 2 is behind with {bus_2_state['passengers']} passengers.
There are {stop_state['waiting']} people waiting at the stop.
Traffic ahead is {traffic_summary}.

Calculate the economic trade-off between wait time, traffic delay, and passenger load.
Choose the best action for Bus 1 and Bus 2.
Return only the required raw JSON object.
""".strip()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=150,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    bus_1_state = {"id": "Bus_1", "passengers": 50}
    bus_2_state = {"id": "Bus_2", "passengers": 5}
    stop_state = {"name": "Uttarahalli", "waiting": 40}
    traffic_state = {"location": "Uttarahalli", "severity": "Severe Gridlock"}

    raw_output = trigger_v2x_debate(bus_1_state, bus_2_state, stop_state, traffic_state)
    print(raw_output)

    parsed_output = json.loads(raw_output)
    print("Parsed JSON OK")
    print(json.dumps(parsed_output, indent=2))
