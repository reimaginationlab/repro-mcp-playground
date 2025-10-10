# Debug CLI Usage

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env and add your actual API keys
```

## Usage

### Basic usage with state only:
```bash
python debug_cli.py --state TX
```

### With preference specified:
```bash
python debug_cli.py --state CA --preference "abortion pill"
```

### With pretty-printed JSON output:
```bash
python debug_cli.py --state NY --pretty
```

### With verbose output (shows API calls):
```bash
python debug_cli.py --state FL --verbose --pretty
```

### Piping output for further processing:
```bash
python debug_cli.py --state TX --pretty | jq '.conclusions'
```

## Arguments

- `--state` (required): Two-letter state abbreviation (e.g., TX, CA, NY)
- `--preference`: User's preference - choices: "abortion pill", "abortion procedure", "undecided" (default: "undecided")
- `--pretty`: Pretty-print the JSON output
- `--verbose`: Show verbose output including input parameters

## Example Output

```bash
$ python debug_cli.py --state TX --pretty

{
  "input": {
    "queries": [],
    "known_params": {
      "us_state": "TX",
      "gestational_age_days": null,
      "able_to_travel": null,
      "preference": "undecided",
      "age_years": null
    }
  },
  "conclusions": {
    "clinic_access_in_state": false,
    "pill_dispense_in_state": false,
    "pill_receive_by_mail_to_resident": true,
    "travel_may_enable_care": true
  },
  "next_steps": [...],
  "plain_text": "In Texas, abortion care is banned except for very limited emergencies...",
  "nearby_clinics": [...]
}
```

## Troubleshooting

If you see an error about missing API keys:
```
Error: INEEDANA_API_KEY environment variable is not set
```

Make sure you have:
1. Created a `.env` file in the project root
2. Added all three required API keys:
   - `INEEDANA_API_KEY`
   - `ABORTION_POLICY_API_KEY`
   - `ABORTION_POLICY_SUBSCRIPTION_KEY`
