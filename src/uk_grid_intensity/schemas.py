"""Pydantic schemas for the UK Carbon Intensity API.

This module defines all the data models used by the Carbon Intensity API,
providing type safety and validation for API responses.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class IntensityIndex(str, Enum):
    """Carbon intensity index levels."""

    VERY_LOW = "very low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very high"


class FuelType(str, Enum):
    """Fuel types used in generation mix."""

    GAS = "gas"
    COAL = "coal"
    BIOMASS = "biomass"
    NUCLEAR = "nuclear"
    HYDRO = "hydro"
    IMPORTS = "imports"
    OTHER = "other"
    WIND = "wind"
    SOLAR = "solar"
    STORAGE = "storage"  # Pumped storage


class IntensityValue(BaseModel):
    """Carbon intensity values with forecast, actual, and index."""

    forecast: Optional[int] = Field(
        None, description="Forecast carbon intensity in gCO2/kWh"
    )
    actual: Optional[int] = Field(
        None, description="Actual carbon intensity in gCO2/kWh"
    )
    index: IntensityIndex = Field(..., description="Intensity index level")


class StatisticsIntensity(BaseModel):
    """Carbon intensity statistics with max, average, min, and index."""

    max: int = Field(..., description="Maximum carbon intensity in gCO2/kWh")
    average: int = Field(..., description="Average carbon intensity in gCO2/kWh")
    min: int = Field(..., description="Minimum carbon intensity in gCO2/kWh")
    index: IntensityIndex = Field(..., description="Intensity index level")


class FuelMix(BaseModel):
    """Individual fuel type in generation mix."""

    fuel: Union[FuelType, str] = Field(..., description="Fuel type")
    perc: float = Field(..., description="Percentage of total generation", ge=0, le=100)


class IntensityData(BaseModel):
    """Core intensity data with time period and intensity values."""

    from_: datetime = Field(..., alias="from", description="Start datetime in UTC")
    to: datetime = Field(..., description="End datetime in UTC")
    intensity: IntensityValue = Field(..., description="Carbon intensity data")


class GenerationData(BaseModel):
    """Generation mix data with time period."""

    from_: datetime = Field(..., alias="from", description="Start datetime in UTC")
    to: datetime = Field(..., description="End datetime in UTC")
    generationmix: List[FuelMix] = Field(..., description="Generation mix by fuel type")


class StatisticsData(BaseModel):
    """Statistics data with time period and intensity statistics."""

    from_: datetime = Field(..., alias="from", description="Start datetime in UTC")
    to: datetime = Field(..., description="End datetime in UTC")
    intensity: StatisticsIntensity = Field(
        ..., description="Carbon intensity statistics"
    )


class RegionalIntensityData(BaseModel):
    """Regional intensity data with time period, intensity, and generation mix."""

    from_: datetime = Field(..., alias="from", description="Start datetime in UTC")
    to: datetime = Field(..., description="End datetime in UTC")
    intensity: IntensityValue = Field(..., description="Carbon intensity data")
    generationmix: Optional[List[FuelMix]] = Field(
        None, description="Generation mix by fuel type"
    )


class RegionalDataPoint(BaseModel):
    """Individual region data point."""

    regionid: int = Field(..., description="Region ID (1-17)", ge=1, le=17)
    dnoregion: str = Field(..., description="Distribution Network Operator region name")
    shortname: str = Field(..., description="Short region name")
    intensity: IntensityValue = Field(..., description="Carbon intensity data")
    generationmix: Optional[List[FuelMix]] = Field(
        None, description="Generation mix by fuel type"
    )


class RegionalFromTo(BaseModel):
    """Regional data for a specific time period."""

    from_: datetime = Field(..., alias="from", description="Start datetime in UTC")
    to: datetime = Field(..., description="End datetime in UTC")
    regions: List[RegionalDataPoint] = Field(..., description="Regional data points")


class RegionalId(BaseModel):
    """Regional data for a specific region with historical data."""

    regionid: int = Field(..., description="Region ID (1-17)", ge=1, le=17)
    dnoregion: str = Field(..., description="Distribution Network Operator region name")
    shortname: str = Field(..., description="Short region name")
    postcode: Optional[str] = Field(None, description="Outward postcode")
    data: List[RegionalIntensityData] = Field(
        ..., description="Time series intensity data"
    )


class FactorsData(BaseModel):
    """Carbon intensity factors for different fuel types."""

    biomass: Optional[int] = Field(None, alias="Biomass")
    coal: Optional[int] = Field(None, alias="Coal")
    dutch_imports: Optional[int] = Field(None, alias="Dutch Imports")
    french_imports: Optional[int] = Field(None, alias="French Imports")
    gas_combined_cycle: Optional[int] = Field(None, alias="Gas (Combined Cycle)")
    gas_open_cycle: Optional[int] = Field(None, alias="Gas (Open Cycle)")
    hydro: Optional[int] = Field(None, alias="Hydro")
    irish_imports: Optional[int] = Field(None, alias="Irish Imports")
    nuclear: Optional[int] = Field(None, alias="Nuclear")
    oil: Optional[int] = Field(None, alias="Oil")
    other: Optional[int] = Field(None, alias="Other")
    pumped_storage: Optional[int] = Field(None, alias="Pumped Storage")
    solar: Optional[int] = Field(None, alias="Solar")
    wind: Optional[int] = Field(None, alias="Wind")


class ErrorDetails(BaseModel):
    """Error details."""

    code: str = Field(..., description="HTTP error code")
    message: str = Field(..., description="Error message")


class ErrorResponse(BaseModel):
    """API error response."""

    error: ErrorDetails = Field(..., description="Error details")


# Response models
class IntensityResponse(BaseModel):
    """Response model for intensity endpoints."""

    data: List[IntensityData] = Field(..., description="Intensity data list")


class GenerationResponse(BaseModel):
    """Response model for generation endpoints."""

    data: GenerationData = Field(..., description="Generation data")


class StatisticsResponse(BaseModel):
    """Response model for statistics endpoints."""

    data: List[StatisticsData] = Field(..., description="Statistics data list")


class RegionalFromToResponse(BaseModel):
    """Response model for regional endpoints, list based on regions, national or country level."""

    data: List[RegionalFromTo] = Field(
        ..., description="Regional data list with a list of regional data"
    )


class RegionalIdResponse(BaseModel):
    """Response model for regional endpoints, list based on ID."""

    data: List[RegionalId] = Field(
        ..., description="Regional data list with data for each region ID"
    )


class RegionalResponse(BaseModel):
    """Response model for regional endpoints."""

    data: List[Union[RegionalFromTo, RegionalId]] = Field(
        ..., description="Regional data list"
    )


class FactorsResponse(BaseModel):
    """Response model for factors endpoint."""

    data: List[FactorsData] = Field(..., description="Factors data list")


GenerationMix = List[FuelMix]
