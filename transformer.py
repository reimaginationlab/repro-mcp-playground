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

    abortion_pill_policy = """
    Abortion pills are available by mail in every state, even though some states have laws to restrict them. 
    This is because other states have passed shield laws to protect medical providers who offer abortion pills through telehealth. 
    Two trusted sources for abortion pills online are Aid Access (aidaccess.org) and The Massachusetts Medication Abortion Access 
    Project (cambridgereproductivehealthconsultants.org/map).It is generally considered legal for a pregnant person to 
    get and take abortion pills, no matter what state they live in. People concerned about their legal risk can
    contact the Repro Legal Helpline to talk to a lawyer for free (reprolegalhelpline.org)."
    """

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
        abortion_bans = policies.get("abortion_bans", {})
        minors = policies.get("Minors", {})
        tmab = policies.get("TMAB", {})

        ban_type = abortion_bans.get("abortion_ban")
        ban_type_norm = (ban_type or "").strip().casefold()
        ban_exceptions = abortion_bans.get("ban_exceptions", [])
        tmab_status = tmab.get("tmab", [])
        state_name = STATE_NAMES.get(data["state"], data["state"])

        # Handle different ban types
        if ban_type_norm == "total ban":
            conclusions.clinic_access_in_state = False
            conclusions.pill_dispense_in_state = False
            conclusions.pill_receive_by_mail_to_resident = True
            conclusions.travel_may_enable_care = True

            plain_text = (
                f"In {state_name}, abortion is banned except in very few situations, like medical emergencies. "
                f"People can't get an abortion at a clinic in Texas, but they may be able to get abortion "
                f"pills in the mail or travel to get an abortion. "
            )

        elif ban_type_norm == "gestational duration ban":
            conclusions.clinic_access_in_state = True  # May have access depending on timing
            conclusions.pill_dispense_in_state = True  # Usually available early
            conclusions.pill_receive_by_mail_to_resident = True
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
                    f"In North Carolina, abortion is available through {gestational_ban_weeks} weeks ({gestational_ban_days} days) of pregnancy. "
                    f"For someone looking for an abortion today, this means their last period would need to have started on or after {cutoff_date_str}. "
                    f"After 12 weeks, people may be able to get abortion pills in the mail or travel to get an abortion. "
                )
            else:
                # TODO: have Nicole check this 
                plain_text = (
                    f"In {state_name}, abortion care is restricted based on gestational duration. "
                    f"Abortion is available up to a specific point in pregnancy. The user may have "
                    f"access to in-state care depending on how far along they are."
                )

        elif ban_type_norm == "cardiac activity ban":
            conclusions.clinic_access_in_state = True  # Very early access only
            conclusions.pill_dispense_in_state = True  # Available very early
            conclusions.pill_receive_by_mail_to_resident = True
            conclusions.travel_may_enable_care = True

            plain_text = (
                f"In {state_name}, abortion is only available very early in pregnancy "
                f"(usually around 6 weeks - just a few weeks after a missed period). "
                f"This is because a South Carolina law bans abortions after cardiac activity " 
                f"is found in the fetus. After that point, people may be able to get abortion pills "
                f"n the mail or travel to get an abortion. "
            )

        elif ban_type_norm == "fetal viability ban":
            conclusions.clinic_access_in_state = True
            conclusions.pill_dispense_in_state = True
            conclusions.pill_receive_by_mail_to_resident = True
            conclusions.travel_may_enable_care = False  # Usually not needed

            plain_text = (
                f"In {state_name}, abortion is available through most of pregnancy (until around 24-28 weeks). "
                f"After that point, a state law bans abortions once the fetus may be able to survive outside the womb. "
                f"If someone needs an abortion after 24-28 weeks of pregnancy, they may "
                f"be able to travel to get an abortion. "
            )

        elif ban_type_norm == "no ban":
            conclusions.clinic_access_in_state = True
            conclusions.pill_dispense_in_state = True
            conclusions.pill_receive_by_mail_to_resident = True
            conclusions.travel_may_enable_care = False  # Not needed

            plain_text = (
                f"In {state_name}, abortion care is avaliable throughout pregnancy. "
                f"People looking for an abortion in Oregon should be able to find "
                f"a clinic and/or get abortion pills in the state. "
            )

        else:
            # Unknown or null ban type
            plain_text = (
                f"Policy information for {state_name} is available. Please review the "
                f"detailed policy data for specific restrictions and requirements."
                f"[{ban_type_norm}] The response is:"
                f"{policy_data}"
            )

        plain_text += "\n\n" + abortion_pill_policy

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
