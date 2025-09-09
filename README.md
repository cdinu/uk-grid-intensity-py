# UK Grid Carbon Intensity API Client

A comprehensive Python client for the [UK National Grid Carbon Intensity API](https://carbonintensity.org.uk/). This package provides easy access to carbon intensity data, generation mix information, regional data, and statistics with full type safety using Pydantic models.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

### Using pip

```bash
pip install uk-grid-intensity
```

### Using UV (recommended for development)

```bash
uv add uk-grid-intensity
```

## Quick Start

### Basic Usage

```python
from uk_grid_intensity import CarbonIntensityClient

# Create client
client = CarbonIntensityClient()

# Get current carbon intensity
current = client.get_current_intensity()
for data in current:
    print(f"Period: {data.from_} to {data.to}")
    print(f"Intensity: {data.intensity.forecast} gCO2/kWh")
    print(f"Index: {data.intensity.index}")
# close the httpx connection
client.close()
```

### Using Context Manager (Recommended)

```python
from uk_grid_intensity import CarbonIntensityClient

with CarbonIntensityClient() as client:
    # Get current generation mix
    generation = client.get_current_generation_mix()
    for fuel in generation.generationmix:
        print(f"{fuel.fuel}: {fuel.perc}%")
```

### Async Usage

```python
import asyncio
from uk_grid_intensity import CarbonIntensityClient

async def get_data():
    async with CarbonIntensityClient() as client:
        # Get current intensity asynchronously
        current = await client.aget_current_intensity()
        return current

# Run async function
data = asyncio.run(get_data())
```

## API Coverage

The client supports all endpoints from the UK Carbon Intensity API:

### Intensity Data
- Current intensity
- Intensity by date/date range
- Intensity by periods
- Forward forecasts (24h, 48h)
- Intensity statistics

### Generation Mix
- Current generation mix
- Generation mix by date/period

### Regional Data
- Regional intensity data
- Data by region ID
- Data by postcode/outcode

### Additional Data
- Carbon intensity factors
- National statistics

## Command Line Interface

The package includes a CLI tool for quick access:

```bash
# Get current intensity
uk-grid-intensity current

# Get intensity for today
uk-grid-intensity date today

# Get generation mix
uk-grid-intensity generation

# Get regional data
uk-grid-intensity regional --region-id 13

# Get carbon factors
uk-grid-intensity factors
```

### CLI Help

```bash
uk-grid-intensity --help
uk-grid-intensity current --help
```

## Advanced Usage

### Error Handling

```python
from uk_grid_intensity import CarbonIntensityClient, CarbonIntensityAPIError

try:
    with CarbonIntensityClient() as client:
        data = client.get_intensity_by_region_id(99)  # Invalid region
except CarbonIntensityAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
except ValueError as e:
    print(f"Validation Error: {e}")
```

### Custom Configuration

```python
from uk_grid_intensity import CarbonIntensityClient

client = CarbonIntensityClient(
    base_url="https://api.carbonintensity.org.uk",  # Custom base URL
    timeout=60,  # Custom timeout in seconds
)
```

### Working with Regions

```python
from uk_grid_intensity import CarbonIntensityClient
from uk_grid_intensity.constants import REGION_NAMES

with CarbonIntensityClient() as client:
    # Get data for all regions
    regional_data = client.get_current_regional_intensity()
    
    for time_data in regional_data:
        for region in time_data.regions:
            region_name = REGION_NAMES.get(region.regionid, f"Region {region.regionid}")
            print(f"{region_name}: {region.intensity.forecast} gCO2/kWh")
```

## Data Models

All API responses are parsed into Pydantic models with full type safety:

```python
from uk_grid_intensity.schemas import IntensityData, GenerationData

# All models include proper typing and validation
intensity: IntensityData = client.get_current_intensity()[0]
print(intensity.intensity.forecast)  # Type-safe access
print(intensity.intensity.index)     # Enum value

# Rich model with all fields
generation: GenerationData = client.get_current_generation_mix()
for fuel in generation.generationmix:
    print(f"{fuel.fuel}: {fuel.perc}%")  # Type-safe iteration
```

## Examples

### Find the Cleanest Time Today

```python
from uk_grid_intensity import CarbonIntensityClient

with CarbonIntensityClient() as client:
    today_data = client.get_intensity_today()
    
    if today_data:
        cleanest = min(today_data, key=lambda x: x.intensity.forecast or float('inf'))
        print(f"Cleanest period: {cleanest.from_.strftime('%H:%M')} - {cleanest.to.strftime('%H:%M')}")
        print(f"Intensity: {cleanest.intensity.forecast} gCO2/kWh")
```

### Get Weekly Statistics

```python
from datetime import datetime, timedelta
from uk_grid_intensity import CarbonIntensityClient

with CarbonIntensityClient() as client:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    stats = client.get_intensity_statistics(start_date, end_date)
    for data in stats:
        print(f"Average: {data.intensity.average} gCO2/kWh")
        print(f"Min: {data.intensity.min} gCO2/kWh")
        print(f"Max: {data.intensity.max} gCO2/kWh")
```

### Compare Regional Data

```python
from uk_grid_intensity import CarbonIntensityClient

with CarbonIntensityClient() as client:
    # London (region 13) vs Scotland (region 1)
    london = client.get_intensity_by_region_id(13)
    scotland = client.get_intensity_by_region_id(1)
    
    london_intensity = london[0].data[0].intensity.forecast
    scotland_intensity = scotland[0].data[0].intensity.forecast
    
    print(f"London: {london_intensity} gCO2/kWh")
    print(f"Scotland: {scotland_intensity} gCO2/kWh")
```

## Contributing

1. Fork the repository
2. Create a branch
3. Make your changes
4. (ideally) Add tests for your changes
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [National Energy System Operator (NESO)](https://carbonintensity.org.uk/) for providing the Carbon Intensity API

- [Pydantic](https://pydantic.dev/)
- [HTTPX](https://www.python-httpx.org/)

## API Reference

For detailed API documentation, visit the [UK Carbon Intensity API documentation](https://carbon-intensity.github.io/api-definitions/).

## Supported Regions

| Region ID | Region Name |
|-----------|-------------|
| 1 | North Scotland |
| 2 | South Scotland |
| 3 | North West England |
| 4 | North East England |
| 5 | Yorkshire |
| 6 | North Wales |
| 7 | South Wales |
| 8 | West Midlands |
| 9 | East Midlands |
| 10 | East England |
| 11 | South West England |
| 12 | South England |
| 13 | London |
| 14 | South East England |
| 15 | England |
| 16 | Scotland |
| 17 | Wales |
