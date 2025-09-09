"""Constants and utility mappings for the UK Carbon Intensity API."""

from typing import Dict

# Region ID to name mapping
REGION_NAMES: Dict[int, str] = {
    1: "North Scotland",
    2: "South Scotland",
    3: "North West England",
    4: "North East England",
    5: "Yorkshire",
    6: "North Wales",
    7: "South Wales",
    8: "West Midlands",
    9: "East Midlands",
    10: "East England",
    11: "South West England",
    12: "South England",
    13: "London",
    14: "South East England",
    15: "England",
    16: "Scotland",
    17: "Wales",
    18: "GB",
}

# Reverse mapping: name to region ID
REGION_IDS: Dict[str, int] = {name.lower(): id_ for id_, name in REGION_NAMES.items()}

# Fuel type descriptions
FUEL_DESCRIPTIONS = {
    "gas": "Natural Gas",
    "coal": "Coal",
    "biomass": "Biomass",
    "nuclear": "Nuclear",
    "hydro": "Hydroelectric",
    "imports": "Electricity Imports",
    "other": "Other Sources",
    "wind": "Wind Power",
    "solar": "Solar Power",
    "storage": "Pumped Storage",
}

# API endpoints
BASE_URL = "https://api.carbonintensity.org.uk"

# Default timeout for HTTP requests
DEFAULT_TIMEOUT = 30.0

# User agent for requests
USER_AGENT_PREFIX = "uk-grid-intensity-python-client"
