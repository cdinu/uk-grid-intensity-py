"""Examples of using the UK Grid Carbon Intensity API client."""

import asyncio
from datetime import datetime, date, timedelta

from uk_grid_intensity import CarbonIntensityClient
from uk_grid_intensity.constants import REGION_NAMES


async def basic_examples():
    """Basic usage examples."""
    print("=== Basic Examples ===")

    # Create client (can be used as context manager)
    async with CarbonIntensityClient() as client:

        # Get current intensity
        print("\n1. Current Carbon Intensity:")
        current = await client.aget_current_intensity()
        for data in current:
            print(f"  Period: {data.from_} to {data.to}")
            print(f"  Forecast: {data.intensity.forecast} gCO2/kWh")
            print(f"  Index: {data.intensity.index}")

        # Get intensity for specific date
        print("\n2. Carbon Intensity for Today:")
        today_data = await client.aget_intensity_today()
        print(f"  Found {len(today_data)} half-hour periods")

        # Get generation mix
        print("\n3. Current Generation Mix:")
        generation = await client.aget_current_generation_mix()
        print(f"  Period: {generation.from_} to {generation.to}")
        for fuel in generation.generationmix:
            print(f"    {fuel.fuel}: {fuel.perc}%")

        # Get regional data
        print("\n4. Regional Data for London:")
        london_data = await client.aget_intensity_by_region_id(
            13
        )  # London is region 13
        for region in london_data:
            print(f"  Region: {region.shortname}")
            for data_point in region.data:
                print(f"    {data_point.from_} to {data_point.to}")
                print(
                    f"    Intensity: {data_point.intensity.forecast} gCO2/kWh ({data_point.intensity.index})"
                )


async def advanced_examples():
    """Advanced usage examples."""
    print("\n=== Advanced Examples ===")

    client = CarbonIntensityClient()

    try:
        # Get statistics for the past week
        print("\n1. Weekly Statistics:")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        stats = await client.aget_intensity_statistics(start_date, end_date)
        for data in stats:
            print(f"  Period: {data.from_} to {data.to}")
            print(f"    Average: {data.intensity.average} gCO2/kWh")
            print(f"    Min: {data.intensity.min} gCO2/kWh")
            print(f"    Max: {data.intensity.max} gCO2/kWh")
            print(f"    Index: {data.intensity.index}")

        # Get intensity factors
        print("\n2. Carbon Intensity Factors:")
        factors = await client.aget_intensity_factors()
        for factor_data in factors:
            factor_dict = factor_data.model_dump()
            for fuel_type, factor_value in factor_dict.items():
                if factor_value is not None:
                    print(f"  {fuel_type}: {factor_value} gCO2/kWh")

        # Get forecast for next 24 hours
        print("\n3. 24-Hour Forecast:")
        forecast = await client.aget_intensity_forward_24h(datetime.now())
        print(f"  Found {len(forecast)} forecast periods")

        # Find the cleanest time in the next 24 hours
        if forecast:
            cleanest = min(forecast, key=lambda x: x.intensity.forecast or float("inf"))
            print(f"  Cleanest period: {cleanest.from_} to {cleanest.to}")
            print(
                f"  Intensity: {cleanest.intensity.forecast} gCO2/kWh ({cleanest.intensity.index})"
            )

        # Get data for a specific postcode
        print("\n4. Data for Postcode SW1A 1AA:")
        postcode_data = await client.aget_intensity_by_postcode("SW1A1AA")
        for region in postcode_data:
            print(f"  Region: {region.shortname} (ID: {region.regionid})")
            print(f"  DNO: {region.dnoregion}")

    finally:
        await client.aclose()


def synchronous_examples():
    """Synchronous usage examples."""
    print("\n=== Synchronous Examples ===")

    # Using context manager
    with CarbonIntensityClient() as client:

        # Get current intensity
        print("\n1. Current Intensity (Sync):")
        current = client.get_current_intensity()
        for data in current:
            print(f"  {data.intensity.forecast} gCO2/kWh ({data.intensity.index})")

        # Get intensity by date and period
        print("\n2. Specific Date and Period:")
        try:
            specific = client.get_intensity_by_date_and_period(
                date.today(), 25
            )  # Period 25 (12:00-12:30)
            for data in specific:
                print(f"  Period 25: {data.intensity.forecast} gCO2/kWh")
        except Exception as e:
            print(f"  Error: {e}")

        # Get all regions
        print("\n3. All Regions:")
        regional = client.get_current_regional_intensity()
        for time_data in regional:
            print(f"  Time: {time_data.from_} to {time_data.to}")
            for region in time_data.regions:
                region_name = REGION_NAMES.get(
                    region.regionid, f"Region {region.regionid}"
                )
                print(f"    {region_name}: {region.intensity.forecast} gCO2/kWh")


def error_handling_examples():
    """Error handling examples."""
    print("\n=== Error Handling Examples ===")

    from uk_grid_intensity import CarbonIntensityAPIError

    client = CarbonIntensityClient()

    try:
        # Invalid region ID
        print("\n1. Testing Invalid Region ID:")
        try:
            client.get_intensity_by_region_id(99)  # Invalid region ID
        except ValueError as e:
            print(f"  Validation Error: {e}")

        # Invalid date format (this would be caught by datetime parsing)
        print("\n2. Testing Invalid Date:")
        try:
            client.get_intensity_by_date("invalid-date")
        except Exception as e:
            print(f"  Date Error: {e}")

        # API error simulation (using non-existent endpoint)
        print("\n3. Testing API Error:")
        try:
            # This would trigger an HTTP error if the endpoint doesn't exist
            response = client._client.get("/nonexistent")
            client._handle_response(response)
        except CarbonIntensityAPIError as e:
            print(f"  API Error: {e.message}")
            print(f"  Status Code: {e.status_code}")

    finally:
        client.close()


def data_analysis_example():
    """Example of analyzing carbon intensity data."""
    print("\n=== Data Analysis Example ===")

    with CarbonIntensityClient() as client:

        # Get today's data
        today_data = client.get_intensity_today()

        if today_data:
            intensities = [
                d.intensity.forecast for d in today_data if d.intensity.forecast
            ]

            if intensities:
                avg_intensity = sum(intensities) / len(intensities)
                min_intensity = min(intensities)
                max_intensity = max(intensities)

                print("\nToday's Carbon Intensity Analysis:")
                print(f"  Periods analyzed: {len(intensities)}")
                print(f"  Average: {avg_intensity:.1f} gCO2/kWh")
                print(f"  Minimum: {min_intensity} gCO2/kWh")
                print(f"  Maximum: {max_intensity} gCO2/kWh")
                print(f"  Range: {max_intensity - min_intensity} gCO2/kWh")

                # Find cleanest and dirtiest periods
                cleanest = min(
                    today_data, key=lambda x: x.intensity.forecast or float("inf")
                )
                dirtiest = max(today_data, key=lambda x: x.intensity.forecast or 0)

                print(
                    f"\n  Cleanest period: {cleanest.from_.strftime('%H:%M')} - {cleanest.to.strftime('%H:%M')}"
                )
                print(f"    Intensity: {cleanest.intensity.forecast} gCO2/kWh")
                print(
                    f"  Dirtiest period: {dirtiest.from_.strftime('%H:%M')} - {dirtiest.to.strftime('%H:%M')}"
                )
                print(f"    Intensity: {dirtiest.intensity.forecast} gCO2/kWh")


async def main():
    """Run all examples."""
    print("UK Grid Carbon Intensity API Client Examples")
    print("=" * 50)

    await basic_examples()
    await advanced_examples()
    synchronous_examples()
    error_handling_examples()
    data_analysis_example()

    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
