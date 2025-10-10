#!/usr/bin/env python3
"""
Debug CLI for testing the abortion policy tool responses
"""

import argparse
import json
import sys
from dotenv import load_dotenv
from processing import process_policy_request


def main():
    """Main CLI entry point"""
    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Debug CLI for testing abortion policy tool responses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --state TX
  %(prog)s --state CA --preference "abortion pill"
  %(prog)s --state NY --preference "abortion procedure"
  %(prog)s --state FL --pretty
        """
    )

    parser.add_argument(
        "--state",
        required=True,
        help="Two-letter state abbreviation (e.g., TX, CA, NY)"
    )

    parser.add_argument(
        "--preference",
        choices=["abortion pill", "abortion procedure", "undecided"],
        default="undecided",
        help="User's preference for abortion type (default: undecided)"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output including API calls"
    )

    args = parser.parse_args()

    # Prepare inputs
    inputs = {
        "state": args.state.upper(),
        "preference": args.preference
    }

    if args.verbose:
        print(f"Input parameters:", file=sys.stderr)
        print(f"  State: {inputs['state']}", file=sys.stderr)
        print(f"  Preference: {inputs['preference']}", file=sys.stderr)
        print(f"\nFetching data...\n", file=sys.stderr)

    try:
        # Process the request
        result = process_policy_request(inputs)

        # Output the result
        if args.pretty:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result))

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nMake sure you have created a .env file with the required API keys:", file=sys.stderr)
        print("  INEEDANA_API_KEY", file=sys.stderr)
        print("  ABORTION_POLICY_API_KEY", file=sys.stderr)
        print("  ABORTION_POLICY_SUBSCRIPTION_KEY", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
