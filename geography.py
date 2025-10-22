from typing import Tuple

def city_latlon(state_abbr: str) -> Tuple[float, float]:
    """
    Return (latitude, longitude) near the state capital for a US state/territory
    abbreviation. Supports all 50 states plus DC.

    Note: returns lat/lon for Dallas for Texas for reasons.

    Example:
        capital_latlon("TX") -> (30.27467, -97.740349)
        capital_latlon("dc") -> (38.89511, -77.03637)
    """
    abbr = state_abbr.strip().upper()
    coords = {
        "AL": (32.377716, -86.300568),  # Montgomery
        "AK": (58.301598, -134.420212), # Juneau
        "AZ": (33.448143, -112.096962), # Phoenix
        "AR": (34.746613, -92.288986),  # Little Rock
        "CA": (38.576668, -121.493629), # Sacramento
        "CO": (39.739227, -104.984856), # Denver
        "CT": (41.764046, -72.682198),  # Hartford
        "DE": (39.157307, -75.519722),  # Dover
        "FL": (30.438118, -84.281296),  # Tallahassee
        "GA": (33.749027, -84.388229),  # Atlanta
        "HI": (21.307442, -157.857376), # Honolulu
        "ID": (43.617775, -116.199722), # Boise
        "IL": (39.798363, -89.654961),  # Springfield
        "IN": (39.768623, -86.162643),  # Indianapolis
        "IA": (41.591087, -93.603729),  # Des Moines
        "KS": (39.048191, -95.677956),  # Topeka
        "KY": (38.186722, -84.875374),  # Frankfort
        "LA": (30.457069, -91.187393),  # Baton Rouge
        "ME": (44.307167, -69.781693),  # Augusta
        "MD": (38.978764, -76.490936),  # Annapolis
        "MA": (42.358162, -71.063698),  # Boston
        "MI": (42.733635, -84.555328),  # Lansing
        "MN": (44.955097, -93.102211),  # Saint Paul
        "MS": (32.303848, -90.182106),  # Jackson
        "MO": (38.576702, -92.173516),  # Jefferson City
        "MT": (46.585709, -112.018417), # Helena
        "NE": (40.808075, -96.699654),  # Lincoln
        "NV": (39.163914, -119.766121), # Carson City
        "NH": (43.206898, -71.537994),  # Concord
        "NJ": (40.220596, -74.769913),  # Trenton
        "NM": (35.686974, -105.937799), # Santa Fe
        "NY": (42.652843, -73.757874),  # Albany
        "NC": (35.780430, -78.639099),  # Raleigh
        "ND": (46.820850, -100.783318), # Bismarck
        "OH": (39.961346, -82.999069),  # Columbus
        "OK": (35.467560, -97.516428),  # Oklahoma City
        "OR": (44.942898, -123.035095), # Salem
        "PA": (40.264378, -76.883598),  # Harrisburg
        "RI": (41.830914, -71.414963),  # Providence
        "SC": (34.000343, -81.033211),  # Columbia
        "SD": (44.367031, -100.346405), # Pierre
        "TN": (36.162277, -86.774391),  # Nashville
        "TX": (32.825347, -96.963550),  # Dallas (I know)
        "UT": (40.760780, -111.891050), # Salt Lake City
        "VT": (44.262436, -72.580536),  # Montpelier
        "VA": (37.540726, -77.436050),  # Richmond
        "WA": (47.035805, -122.905014), # Olympia
        "WV": (38.336246, -81.612328),  # Charleston
        "WI": (43.074684, -89.384445),  # Madison
        "WY": (41.140259, -104.820236), # Cheyenne
        "DC": (38.895110, -77.036370),  # Washington, DC
    }
    try:
        return coords[abbr]
    except KeyError:
        raise ValueError(f"Unknown US state/territory abbreviation: {state_abbr!r}")


def get_state_id(state_abbr: str) -> str:
    abbr = state_abbr.strip().upper()
    names = {
        "AL": "alabama",
        "AK": "alaska",
        "AZ": "arizona",
        "AR": "arkansas",
        "CA": "california",
        "CO": "colorado",
        "CT": "connecticut",
        "DE": "delaware",
        "FL": "florida",
        "GA": "georgia",
        "HI": "hawaii",
        "ID": "idaho",
        "IL": "illinois",
        "IN": "indiana",
        "IA": "iowa",
        "KS": "kansas",
        "KY": "kentucky",
        "LA": "louisiana",
        "ME": "maine",
        "MD": "maryland",
        "MA": "massachusetts",
        "MI": "michigan",
        "MN": "minnesota",
        "MS": "mississippi",
        "MO": "missouri",
        "MT": "montana",
        "NE": "nebraska",
        "NV": "nevada",
        "NH": "new_hampshire",
        "NJ": "new_jersey",
        "NM": "new_mexico",
        "NY": "new_york",
        "NC": "north_carolina",
        "ND": "north_dakota",
        "OH": "ohio",
        "OK": "oklahoma",
        "OR": "oregon",
        "PA": "pennsylvania",
        "RI": "rhode_island",
        "SC": "south_carolina",
        "SD": "south_dakota",
        "TN": "tennessee",
        "TX": "texas",
        "UT": "utah",
        "VT": "vermont",
        "VA": "virginia",
        "WA": "washington",
        "WV": "west_virginia",
        "WI": "wisconsin",
        "WY": "wyoming",
        "DC": "washington_dc",
    }
    try:
        return names[abbr]
    except KeyError:
        raise ValueError(f"Unknown US state/territory abbreviation: {state_abbr!r}")

# List of state_id values from backend
# "state_id": "alabama",
# "state_id": "alaska",
# "state_id": "american_samoa",
# "state_id": "arizona",
# "state_id": "arkansas",
# "state_id": "california",
# "state_id": "colorado",
# "state_id": "connecticut",
# "state_id": "delaware",
# "state_id": "florida",
# "state_id": "georgia",
# "state_id": "guam",
# "state_id": "hawaii",
# "state_id": "idaho",
# "state_id": "illinois",
# "state_id": "indiana",
# "state_id": "iowa",
# "state_id": "kansas",
# "state_id": "kentucky",
# "state_id": "louisiana",
# "state_id": "maine",
# "state_id": "maryland",
# "state_id": "massachusetts",
# "state_id": "michigan",
# "state_id": "minnesota",
# "state_id": "mississippi",
# "state_id": "missouri",
# "state_id": "montana",
# "state_id": "nebraska",
# "state_id": "nevada",
# "state_id": "new_hampshire",
# "state_id": "new_jersey",
# "state_id": "new_mexico",
# "state_id": "new_york",
# "state_id": "north_carolina",
# "state_id": "north_dakota",
# "state_id": "northern_mariana_islands",
# "state_id": "ohio",
# "state_id": "oklahoma",
# "state_id": "oregon",
# "state_id": "pennsylvania",
# "state_id": "puerto_rico",
# "state_id": "rhode_island",
# "state_id": "south_carolina",
# "state_id": "south_dakota",
# "state_id": "tennessee",
# "state_id": "texas",
# "state_id": "us_virgin_islands",
# "state_id": "utah",
# "state_id": "vermont",
# "state_id": "virginia",
# "state_id": "washington_dc",
# "state_id": "washington",
# "state_id": "west_virginia",
# "state_id": "wisconsin",
# "state_id": "wyoming",