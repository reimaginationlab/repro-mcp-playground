import anyio
from dotenv import load_dotenv
from fastmcp import FastMCP
from typing import Annotated, Literal
from processing import process_policy_request

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


if __name__ == "__main__":
    mcp.run()