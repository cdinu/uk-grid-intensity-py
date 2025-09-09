"""UK Grid Carbon Intensity API Client.

A Python client for accessing the UK National Grid Carbon Intensity API.
Provides comprehensive access to carbon intensity data, generation mix information,
regional data, and statistics with full type safety using Pydantic models.
"""

from .client import CarbonIntensityAPIError, CarbonIntensityClient
from .schemas import (  # Response types; Data models; Nested models; Enums
    ErrorDetails,
    ErrorResponse,
    FactorsData,
    FactorsResponse,
    FuelMix,
    FuelType,
    GenerationData,
    GenerationResponse,
    IntensityData,
    IntensityIndex,
    IntensityResponse,
    IntensityValue,
    RegionalDataPoint,
    RegionalFromTo,
    RegionalId,
    RegionalIntensityData,
    RegionalResponse,
    StatisticsData,
    StatisticsIntensity,
    StatisticsResponse,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "CarbonIntensityClient",
    "CarbonIntensityAPIError",
    # Response types
    "IntensityResponse",
    "GenerationResponse",
    "RegionalResponse",
    "StatisticsResponse",
    "FactorsResponse",
    "ErrorResponse",
    # Data models
    "IntensityData",
    "GenerationData",
    "RegionalId",
    "RegionalFromTo",
    "StatisticsData",
    "FactorsData",
    # Nested models
    "IntensityValue",
    "StatisticsIntensity",
    "FuelMix",
    "RegionalIntensityData",
    "RegionalDataPoint",
    "ErrorDetails",
    # Enums
    "IntensityIndex",
    "FuelType",
]
