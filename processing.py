import anyio
from geography import city_latlon


def process_policy_request(inputs: dict) -> dict:
    state = inputs["state"]
    preference = inputs["preference"]
    
    lat, lon = city_latlon(state)
    
    return {"state": state, "preference": preference, "lat": lat, "lon": lon}

