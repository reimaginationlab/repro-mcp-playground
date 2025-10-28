import json
import os
from typing import List, Dict

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "medab_suppliers.json")

def get_medab_suppliers(state: str) -> List[Dict]:
    """Fetch MedAb suppliers filtered by state abbreviation or full name."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"medab_suppliers.json not found at {DATA_PATH}")

    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    # Normalize & filter
    state = state.strip().lower()
    results = [
        supplier for supplier in data
        if supplier.get("state", "").lower() == state
        or supplier.get("state_code", "").lower() == state
    ]
    return results