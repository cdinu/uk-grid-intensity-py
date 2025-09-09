"""Command-line interface for the UK Grid Carbon Intensity API client."""

import argparse
import sys
from datetime import datetime
from typing import Optional

from .client import CarbonIntensityClient, CarbonIntensityAPIError
from ._version import __version__


def format_intensity_data(data_list):
    """Format intensity data for display."""
    if not data_list:
        return "No data available."

    output = []
    for item in data_list:
        output.append(f"Period: {item.from_} to {item.to}")
        output.append(f"  Forecast: {item.intensity.forecast} gCO2/kWh")
        if item.intensity.actual:
            output.append(f"  Actual: {item.intensity.actual} gCO2/kWh")
        output.append(f"  Index: {item.intensity.index}")
        output.append("")
    return "\n".join(output)


def format_generation_data(data):
    """Format generation mix data for display."""
    if not data:
        return "No data available."

    output = []
    output.append(f"Period: {data.from_} to {data.to}")
    output.append("  Generation Mix:")
    for fuel in data.generationmix:
        output.append(f"    {fuel.fuel}: {fuel.perc}%")
    return "\n".join(output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="UK Grid Carbon Intensity API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version", action="version", version=f"uk-grid-intensity {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Current intensity command
    current_parser = subparsers.add_parser(
        "current", help="Get current carbon intensity"
    )
    current_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )

    # Intensity by date command
    date_parser = subparsers.add_parser("date", help="Get intensity for specific date")
    date_parser.add_argument("date", help="Date in YYYY-MM-DD format")
    date_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )

    # Generation mix command
    generation_parser = subparsers.add_parser(
        "generation", help="Get current generation mix"
    )
    generation_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )

    # Regional command
    regional_parser = subparsers.add_parser("regional", help="Get regional data")
    regional_group = regional_parser.add_mutually_exclusive_group()
    regional_group.add_argument("--postcode", help="Postcode (e.g., SW1, RG41)")
    regional_group.add_argument("--region-id", type=int, help="Region ID (1-17)")
    regional_group.add_argument(
        "--country", choices=["england", "scotland", "wales"], help="Country name"
    )
    regional_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )

    # Factors command
    factors_parser = subparsers.add_parser(
        "factors", help="Get carbon intensity factors"
    )
    factors_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        client = CarbonIntensityClient()

        if args.command == "current":
            data = client.get_current_intensity()
            if args.format == "json":
                import json

                print(
                    json.dumps(
                        [item.model_dump() for item in data], indent=2, default=str
                    )
                )
            else:
                print("Current Carbon Intensity:")
                print(format_intensity_data(data))

        elif args.command == "date":
            data = client.get_intensity_by_date(args.date)
            if args.format == "json":
                import json

                print(
                    json.dumps(
                        [item.model_dump() for item in data], indent=2, default=str
                    )
                )
            else:
                print(f"Carbon Intensity for {args.date}:")
                print(format_intensity_data(data))

        elif args.command == "generation":
            data = client.get_current_generation_mix()
            if args.format == "json":
                import json

                print(
                    json.dumps(
                        [item.model_dump() for item in data], indent=2, default=str
                    )
                )
            else:
                print("Current Generation Mix:")
                print(format_generation_data(data))

        elif args.command == "regional":
            if args.postcode:
                data = client.get_intensity_by_postcode(args.postcode)
            elif args.region_id:
                data = client.get_intensity_by_region_id(args.region_id)
            elif args.country == "england":
                data = client.get_current_england_intensity()
            elif args.country == "scotland":
                data = client.get_current_scotland_intensity()
            elif args.country == "wales":
                data = client.get_current_wales_intensity()
            else:
                data = client.get_current_regional_intensity()

            if args.format == "json":
                import json

                print(
                    json.dumps(
                        [item.model_dump() for item in data], indent=2, default=str
                    )
                )
            else:
                print("Regional Carbon Intensity:")
                # Regional data formatting would need more complex logic
                print("Use --format json for detailed output")

        elif args.command == "factors":
            data = client.get_intensity_factors()
            if args.format == "json":
                import json

                print(
                    json.dumps(
                        [item.model_dump() for item in data], indent=2, default=str
                    )
                )
            else:
                print("Carbon Intensity Factors:")
                for item in data:
                    for field_name, field_value in item.model_dump().items():
                        if field_value is not None:
                            print(f"  {field_name}: {field_value} gCO2/kWh")

    except CarbonIntensityAPIError as e:
        print(f"API Error: {e.message}", file=sys.stderr)
        if e.status_code:
            print(f"Status Code: {e.status_code}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
