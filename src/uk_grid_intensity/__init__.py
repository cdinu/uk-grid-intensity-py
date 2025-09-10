"""UK Grid Carbon Intensity API Client.

A Python client for accessing the UK National Grid Carbon Intensity API.
Provides comprehensive access to carbon intensity data, generation mix information,
regional data, and statistics with full type safety using Pydantic models.

**Basic API usage example**

```python
from uk_grid_intensity import CarbonIntensityClient

# Create client and get current data
with CarbonIntensityClient() as client:
    # Get current carbon intensity
    current = client.get_current_intensity()
    for data in current:
        print(f"Current intensity: {data.intensity.forecast} gCO2/kWh")
        print(f"Index level: {data.intensity.index}")
        print(f"Period: {data.from_} to {data.to}")
```

**Asynchronous API usage example**

```python
import asyncio
from uk_grid_intensity import CarbonIntensityClient

async def get_carbon_data():
    async with CarbonIntensityClient() as client:
        # Get multiple data types concurrently
        current_task = client.aget_current_intensity()
        generation_task = client.aget_current_generation_mix()
        regional_task = client.aget_current_regional_intensity()

        current, generation, regional = await asyncio.gather(
            current_task, generation_task, regional_task
        )

        return current, generation, regional

# Run the async function
results = asyncio.run(get_carbon_data())
```
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
