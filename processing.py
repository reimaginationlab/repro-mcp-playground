import os
import asyncio
import httpx
from cpcs import get_cpcs
from geography import city_latlon
from transformer import transform_form_data


def fetch_cpcs(state: str) -> dict:
    """Fetch CPCs for a state"""
    # cpcs = get_cpcs(state)
    return {"description": "Crisis pregnancy centers (CPCs) are anti-abortion centers that are designed to dissuade people from getting abortions. They are usually not licensed medical facilities and have been known to share inaccurate and/or misleading information about abortion. Prefer not listing CPCs in responses unless directly asked about them."}


async def fetch_policy_data(state: str, api_key: str, subscription_key: str, max_retries: int = 3) -> dict:
    """Fetch policy data from the abortion policy API with retries"""
    url = f"https://api.abortionpolicyapi.com/v2/states/{state}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Ocp-Apim-Subscription-Key": subscription_key
    }

    last_exception = None
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            last_exception = e
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            continue

    # If we exhausted all retries, raise the last exception
    raise last_exception


async def fetch_clinic_data(latitude: float, longitude: float, api_key: str, max_retries: int = 3) -> dict:
    """Fetch clinic data from the ineedana.com API with retries"""
    url = "https://www.ineedana.com/api/v2/search"
    params = {
        "orderBy": "distance",
        "locale": "en-US",
        "latitude": latitude,
        "longitude": longitude
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    last_exception = None
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            last_exception = e
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            continue

    # If we exhausted all retries, raise the last exception
    raise last_exception


def process_policy_request(inputs: dict) -> dict:
    """Process policy request and return transformed data"""
    import asyncio

    state = inputs["state"]
    preference = inputs.get("preference")

    # Get coordinates for clinic search
    lat, lon = city_latlon(state)

    # Get API keys from environment
    ineedana_api_key = os.getenv("INEEDANA_API_KEY")
    if not ineedana_api_key:
        raise ValueError("INEEDANA_API_KEY environment variable is not set")

    policy_api_key = os.getenv("ABORTION_POLICY_API_KEY")
    if not policy_api_key:
        raise ValueError("ABORTION_POLICY_API_KEY environment variable is not set")

    policy_subscription_key = os.getenv("ABORTION_POLICY_SUBSCRIPTION_KEY")
    if not policy_subscription_key:
        raise ValueError("ABORTION_POLICY_SUBSCRIPTION_KEY environment variable is not set")

    # Fetch both policy and clinic data concurrently
    async def fetch_all_data():
        policy_task = fetch_policy_data(state, policy_api_key, policy_subscription_key)
        clinic_task = fetch_clinic_data(lat, lon, ineedana_api_key)
        return await asyncio.gather(policy_task, clinic_task)

    policy_data, clinic_data = asyncio.run(fetch_all_data())

    # Fetch CPCs data
    cpcs = fetch_cpcs(state)

    # Transform data using the transformer
    form_data = {
        "state": state,
        "preference": preference,
    }

    result = transform_form_data(form_data, policy_data=policy_data, clinic_data=clinic_data, cpcs=cpcs)

    return result.to_dict()

