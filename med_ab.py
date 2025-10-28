import json

DATA_PATH = "data/medab_suppliers.json"

def get_medab_suppliers(state):
    """Return suppliers that operate in the given state name."""
    with open(DATA_PATH) as f:
        data = json.load(f)

    state = state.strip().lower()
    results = [
        s for s in data
        if state in [x.strip().lower() for x in s.get("States", "").split(",")]
    ]
    return results


if __name__ == "__main__":
    # Example test
    suppliers = get_medab_suppliers("Texas")
    print(json.dumps(suppliers, indent=2))
