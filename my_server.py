import anyio
from dotenv import load_dotenv
from fastmcp import FastMCP
from typing import Annotated, Literal
from processing import process_policy_request
from cpcs import get_cpcs

from pydantic import Field

# Load environment variables from .env file
load_dotenv()

mcp = FastMCP()

@mcp.tool(
    name="abortion_policy_information",
    description="Provides authoritative, up-to-date information on abortion policy for abortion seekers in a given state.",
    meta={"version": "0.1"}
)
async def get_abortion_policy_information(
    state: Annotated[str, "The two-letter state abbreviation to get abortion policy information for"],
    preference: Annotated[
        Literal["abortion pill", "abortion procedure", "undecided"],
        Field(description="Users preference for abortion type")
    ] = "undecided"
) -> dict:
    """Provides information on abortion policy and available clinics for abortion seekers in a given state."""

    inputs = {"state": state, "preference": preference}
    return await anyio.to_thread.run_sync(process_policy_request, inputs)


@mcp.tool(
    name="cpc_lookup",
    description="Check if clinic names are Crisis Pregnancy Centers (CPCs). CPCs are anti-abortion centers that may provide misleading information.",
    meta={"version": "0.1"}
)
async def cpc_lookup(
    clinic_names: Annotated[list[str], "List of clinic names to check against the CPC database"]
) -> dict:
    """
    Check if provided clinic names match known Crisis Pregnancy Centers (CPCs).

    Returns a dictionary with each clinic name mapped to True (is a CPC) or False (not a CPC).
    """
    def check_cpcs(clinic_names: list[str]) -> dict:
        # Get the list of known CPCs for the state
        cpcs = get_cpcs()

        # Normalize CPC names for comparison (lowercase, strip whitespace)
        normalized_cpcs = {cpc.lower().strip() for cpc in cpcs}

        # Check each clinic name
        results = {}
        for clinic_name in clinic_names:
            normalized_name = clinic_name.lower().strip()
            results[clinic_name] = normalized_name in normalized_cpcs

        return {
            "results": results,
            "note": "Crisis pregnancy centers (CPCs) are anti-abortion centers that are designed to dissuade people from getting abortions. They are usually not licensed medical facilities and have been known to share inaccurate and/or misleading information about abortion."
        }

    return await anyio.to_thread.run_sync(check_cpcs, clinic_names)


if __name__ == "__main__":
    mcp.run()