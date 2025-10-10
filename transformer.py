from typing import Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta


STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "Washington DC"
}


@dataclass
class Clinic:
    name: str
    phone: str
    hours: Any
    address: str
    website: str
    distance: float
    drive_time: float
    services: Any


@dataclass
class KnownParams:
    us_state: Optional[str] = None
    gestational_age_days: Optional[int] = None
    able_to_travel: Optional[bool] = None
    preference: Optional[str] = None
    age_years: Optional[int] = None


@dataclass
class InputData:
    queries: list[str] = field(default_factory=list)
    known_params: KnownParams = field(default_factory=KnownParams)


@dataclass
class Conclusions:
    clinic_access_in_state: Optional[bool] = None
    pill_dispense_in_state: Optional[bool] = None
    pill_receive_by_mail_to_resident: Optional[bool] = None
    travel_may_enable_care: Optional[bool] = None


@dataclass
class TransformedOutput:
    input: InputData
    conclusions: Conclusions
    next_steps: list[str] = field(default_factory=list)
    plain_text: str = ""
    nearby_clinics: Optional[list[Clinic]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, omitting None values for nearby_clinics"""
        result = {
            "input": {
                "queries": self.input.queries,
                "known_params": asdict(self.input.known_params)
            },
            "conclusions": asdict(self.conclusions),
            "next_steps": self.next_steps,
            "plain_text": self.plain_text
        }

        if self.nearby_clinics is not None:
            result["nearby_clinics"] = [asdict(clinic) for clinic in self.nearby_clinics]

        return result


def transform_form_data(
    data: dict,
    policy_data: Optional[dict] = None,
    clinic_data: Optional[dict] = None
) -> TransformedOutput:
    """
    Transform form data and policy data into structured output

    Args:
        data: Input form data with keys like 'state', 'preference', 'gestationalAge', etc.
        policy_data: Policy data from the abortion policy API
        clinic_data: Clinic data with nearby clinics

    Returns:
        TransformedOutput object with structured information
    """
    # Parse queries if provided
    queries = []
    if "queries" in data and data["queries"]:
        queries = [q.strip() for q in data["queries"].split('\n') if q.strip()]

    # Build input structure
    known_params = KnownParams(
        us_state=data.get("state"),
        gestational_age_days=data.get("gestationalAge"),
        able_to_travel=True if data.get("ableToTravel") else None,
        preference=data.get("preference"),
        age_years=data.get("age")
    )

    input_data = InputData(queries=queries, known_params=known_params)

    # Initialize conclusions and output variables
    conclusions = Conclusions()
    next_steps = []
    plain_text = ""
    nearby_clinics = None

    # Process policy data if available
    if policy_data and data.get("state"):
        policies = policy_data.get("policies", {})
        abortion_bans = policies.get("Abortion Bans", {})
        minors = policies.get("Minors", {})
        tmab = policies.get("TMAB", {})

        ban_type = abortion_bans.get("Abortion Bans")
        ban_exceptions = abortion_bans.get("Ban Exceptions", [])
        tmab_status = tmab.get("TMAB", [])
        state_name = STATE_NAMES.get(data["state"], data["state"])

        # Handle different ban types
        if ban_type == "Total Ban":
            conclusions.clinic_access_in_state = False
            conclusions.pill_dispense_in_state = False
            conclusions.pill_receive_by_mail_to_resident = "Prohibited" not in tmab_status
            conclusions.travel_may_enable_care = True

            plain_text = (
                f"In {state_name}, abortion care is banned except for very limited "
                f"emergencies, so the user can't get an in-state clinic appointment."
            )

            if not data.get("preference"):
                next_steps.append(
                    "The user's preference of abortion pills or an in-clinic procedure "
                    "has significant implications on their options. Once known, this "
                    "information can be added to the tool call to provide more concise "
                    "options and recommendations."
                )

        elif ban_type == "Gestational Duration Ban":
            conclusions.clinic_access_in_state = True  # May have access depending on timing
            conclusions.pill_dispense_in_state = True  # Usually available early
            conclusions.pill_receive_by_mail_to_resident = "Prohibited" not in tmab_status
            conclusions.travel_may_enable_care = True

            # Get gestational ban weeks and convert to days
            gestational_ban_weeks = abortion_bans.get("Gestational Ban Weeks")
            if gestational_ban_weeks is not None:
                # Convert weeks to days
                gestational_ban_days = int(gestational_ban_weeks * 7)

                # Calculate the cutoff date (days ago from today)
                today = datetime.now()
                cutoff_date = today - timedelta(days=gestational_ban_days)
                cutoff_date_str = cutoff_date.strftime("%B %d, %Y")

                plain_text = (
                    f"In {state_name}, abortion care is restricted based on gestational duration. "
                    f"Abortion is available up to {gestational_ban_weeks} weeks ({gestational_ban_days} days) "
                    f"of pregnancy. For someone seeking care today, this means their last menstrual period "
                    f"would need to have started on or after {cutoff_date_str}. The user may have "
                    f"access to in-state care depending on how far along they are."
                )
            else:
                plain_text = (
                    f"In {state_name}, abortion care is restricted based on gestational duration. "
                    f"Abortion is available up to a specific point in pregnancy. The user may have "
                    f"access to in-state care depending on how far along they are."
                )

        elif ban_type == "Cardiac Activity Ban":
            conclusions.clinic_access_in_state = True  # Very early access only
            conclusions.pill_dispense_in_state = True  # Available very early
            conclusions.pill_receive_by_mail_to_resident = "Prohibited" not in tmab_status
            conclusions.travel_may_enable_care = True

            plain_text = (
                f"In {state_name}, abortion care is banned once cardiac activity is detected "
                f"(typically around 6 weeks). The user may have very limited time to access "
                f"in-state care, usually only in the first few weeks after a missed period."
            )

        elif ban_type == "Fetal Viability Ban":
            conclusions.clinic_access_in_state = True
            conclusions.pill_dispense_in_state = True
            conclusions.pill_receive_by_mail_to_resident = "Prohibited" not in tmab_status
            conclusions.travel_may_enable_care = False  # Usually not needed

            plain_text = (
                f"In {state_name}, abortion care is available until fetal viability "
                f"(typically around 24-28 weeks). The user should have access to in-state "
                f"care for most of their pregnancy."
            )

        elif ban_type == "No Ban":
            conclusions.clinic_access_in_state = True
            conclusions.pill_dispense_in_state = True
            conclusions.pill_receive_by_mail_to_resident = "Prohibited" not in tmab_status
            conclusions.travel_may_enable_care = False  # Not needed

            plain_text = (
                f"In {state_name}, abortion care is accessible throughout pregnancy. "
                f"The user should have good access to both medication and procedural "
                f"abortion care in-state."
            )

        else:
            # Unknown or null ban type
            plain_text = (
                f"Policy information for {state_name} is available. Please review the "
                f"detailed policy data for specific restrictions and requirements."
            )

    # Process clinic data if available
    if clinic_data and clinic_data.get("clinics") and isinstance(clinic_data["clinics"], list):
        nearby_clinics = []
        for clinic in clinic_data["clinics"][:5]:
            nearby_clinics.append(Clinic(
                name=clinic.get("name", ""),
                phone=clinic.get("phone", ""),
                hours=clinic.get("hours"),
                address=f"{clinic.get('streetAddress', '')}, {clinic.get('city', '')}, "
                        f"{clinic.get('state', '')}, {clinic.get('zipcode', '')}",
                website=clinic.get("website", ""),
                distance=clinic.get("distance", 0),
                drive_time=clinic.get("driveTime", 0),
                services=clinic.get("services")
            ))

    # Build result
    result = TransformedOutput(
        input=input_data,
        conclusions=conclusions,
        next_steps=next_steps,
        plain_text=plain_text,
        nearby_clinics=nearby_clinics if nearby_clinics else None
    )

    return result
