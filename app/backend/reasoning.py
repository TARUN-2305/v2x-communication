import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

import groq

def explain_action(bus_id, action, econ_data, gap_ahead=None, gap_behind=None, queue_length=None):
    action_str = {0: "PROCEED", 1: "HOLD", 2: "SKIP"}.get(action, "UNKNOWN")
    api_key = os.environ.get("GROQ_API_KEY", "").strip()

    # Rich, context-aware rule-based fallback when Groq API key is not available
    if not api_key:
        net = econ_data['revenue'] - econ_data['wait_cost'] - econ_data['fuel_cost']
        if action == 0: # PROCEED
            if queue_length and queue_length > 15:
                return f"Proceeded to stop to clear a large queue of {queue_length:.0f} passengers, generating ₹{econ_data['revenue']:.0f} in ticket revenue."
            return f"Proceeded to service stop. Ticket revenue ₹{econ_data['revenue']:.0f} offset wait-time penalty ₹{econ_data['wait_cost']:.0f} and operational fuel cost ₹{econ_data['fuel_cost']:.0f}."
        elif action == 1: # HOLD
            if gap_ahead and gap_ahead <= 1.5:
                return f"Held at station to widen headway to bus ahead (currently only {gap_ahead:.1f} stops away) to mitigate dynamic bunching risks."
            return f"Held at stop to regulate headways and balance route frequency, minimizing aggregate wait time down-route."
        elif action == 2: # SKIP
            if queue_length and queue_length <= 3:
                return f"Skipped stop due to very low passenger demand ({queue_length:.0f} waiting), reducing travel delay by 30% for {80 - queue_length:.0f} onboard passengers."
            return f"Skipped stop to recover route schedule, catch up to target spacing, and prevent bunching cascade on Outer Ring Road."
        return f"Bus {bus_id} chose {action_str} (Net: ₹{net:.0f})."

    # LLM Prompt with rich operational context
    prompt = (
        f"Context: Bengaluru Outer Ring Road Transit Route. "
        f"Bus {bus_id} decided to {action_str} at the current stop. "
        f"Telemetry: Gap Ahead={gap_ahead if gap_ahead is not None else 'N/A'} stops, "
        f"Gap Behind={gap_behind if gap_behind is not None else 'N/A'} stops, "
        f"Queue Length={queue_length if queue_length is not None else 'N/A'} passengers. "
        f"Financials: Wait Cost=₹{econ_data['wait_cost']:.0f}, Fuel Cost=₹{econ_data['fuel_cost']:.0f}, Revenue=₹{econ_data['revenue']:.0f}. "
        f"Explain in exactly one concise, professional sentence the operational and economic justification for this {action_str} decision."
    )
    
    try:
        client = groq.Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional transit operations controller explaining AI dispatching decisions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM error: {str(e)}. Fallback: Chose {action_str} (Revenue: ₹{econ_data['revenue']:.0f}, Wait: ₹{econ_data['wait_cost']:.0f}, Fuel: ₹{econ_data['fuel_cost']:.0f})."

if __name__ == "__main__":
    dummy_econ_data = {
        'wait_cost': 45.0,
        'fuel_cost': 22.0,
        'revenue': 150.0
    }
    explanation = explain_action(bus_id=2, action=0, econ_data=dummy_econ_data, gap_ahead=1.2, gap_behind=3.0, queue_length=5)
    print("--- LLM/Fallback Reasoning Output ---")
    print(explanation)
