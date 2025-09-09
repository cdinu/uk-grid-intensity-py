"""Carbon Intensity API Client.

A comprehensive client for the UK National Grid Carbon Intensity API.
Provides methods to access all API endpoints with proper type safety.
"""

import asyncio
from datetime import date, datetime
from typing import List, Optional, Union
from urllib.parse import urljoin

import httpx

from .schemas import (
    FactorsData,
    FactorsResponse,
    GenerationData,
    GenerationResponse,
    IntensityData,
    IntensityResponse,
    RegionalFromTo,
    RegionalFromToResponse,
    RegionalId,
    RegionalIdResponse,
    RegionalResponse,
    StatisticsData,
    StatisticsResponse,
)

# Constants
_REGION_ID_ERROR = "Region ID must be between 1 and 18"


class CarbonIntensityAPIError(Exception):
    """Exception raised when the Carbon Intensity API returns an error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class CarbonIntensityClient:
    """Client for the UK Carbon Intensity API.

    Provides synchronous and asynchronous methods to access carbon intensity data,
    generation mix information, regional data, and statistics.

    Args:
        base_url: Base URL for the API (default: https://api.carbonintensity.org.uk)
        timeout: Request timeout in seconds (default: 30)
        user_agent: User agent string for requests
    """

    def __init__(
        self,
        base_url: str = "https://api.carbonintensity.org.uk",
        timeout: float = 30.0,
        user_agent: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent or "uk-grid-intensity-client-python"

        # Configure httpx client
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent},
        )
        self._async_client: Optional[httpx.AsyncClient] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    def close(self):
        """Close the synchronous client."""
        self._client.close()

    async def aclose(self):
        """Close the asynchronous client."""
        if self._async_client:
            await self._async_client.aclose()

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create the async client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
            )
        return self._async_client

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and check for errors."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            try:
                error_data = response.json()
                if "error" in error_data:
                    error = error_data["error"]
                    raise CarbonIntensityAPIError(
                        error.get("message", "Unknown API error"),
                        response.status_code,
                        error.get("code"),
                    )
            except (ValueError, KeyError):
                pass

            raise CarbonIntensityAPIError(
                f"HTTP {response.status_code}: {response.text}", response.status_code
            )

    def _format_datetime(self, dt: Union[datetime, str]) -> str:
        """Format datetime for API requests."""
        if isinstance(dt, str):
            return dt
        return dt.strftime("%Y-%m-%dT%H:%MZ")

    def _format_date(self, d: Union[date, str]) -> str:
        """Format date for API requests."""
        if isinstance(d, str):
            return d
        return d.strftime("%Y-%m-%d")

    # Intensity endpoints
    def get_current_intensity(self) -> List[IntensityData]:
        """Get carbon intensity data for current half hour."""
        response = self._client.get("/intensity")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_current_intensity(self) -> List[IntensityData]:
        """Get carbon intensity data for current half hour (async)."""
        response = await self.async_client.get("/intensity")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    def get_intensity_today(self) -> List[IntensityData]:
        """Get carbon intensity data for today."""
        response = self._client.get("/intensity/date")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_intensity_today(self) -> List[IntensityData]:
        """Get carbon intensity data for today (async)."""
        response = await self.async_client.get("/intensity/date")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    def get_intensity_by_date(self, date_: Union[date, str]) -> List[IntensityData]:
        """Get carbon intensity data for specific date."""
        date_str = self._format_date(date_)
        response = self._client.get(f"/intensity/date/{date_str}")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_intensity_by_date(
        self, date_: Union[date, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data for specific date (async)."""
        date_str = self._format_date(date_)
        response = await self.async_client.get(f"/intensity/date/{date_str}")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    def get_intensity_by_date_and_period(
        self, date_: Union[date, str], period: int
    ) -> List[IntensityData]:
        """Get carbon intensity data for specific date and settlement period (1-48)."""
        if not 1 <= period <= 48:
            raise ValueError("Period must be between 1 and 48")

        date_str = self._format_date(date_)
        response = self._client.get(f"/intensity/date/{date_str}/{period}")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_intensity_by_date_and_period(
        self, date_: Union[date, str], period: int
    ) -> List[IntensityData]:
        """Get carbon intensity data for specific date and settlement period (async)."""
        if not 1 <= period <= 48:
            raise ValueError("Period must be between 1 and 48")

        date_str = self._format_date(date_)
        response = await self.async_client.get(f"/intensity/date/{date_str}/{period}")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    def get_intensity_factors(self) -> List[FactorsData]:
        """Get carbon intensity factors for each fuel type."""
        response = self._client.get("/intensity/factors")
        data = self._handle_response(response)
        return FactorsResponse.model_validate(data).data

    async def aget_intensity_factors(self) -> List[FactorsData]:
        """Get carbon intensity factors for each fuel type (async)."""
        response = await self.async_client.get("/intensity/factors")
        data = self._handle_response(response)
        return FactorsResponse.model_validate(data).data

    def get_intensity_by_datetime(
        self, from_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data for specific datetime."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(f"/intensity/{from_str}")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_intensity_by_datetime(
        self, from_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data for specific datetime (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(f"/intensity/{from_str}")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    def get_intensity_forward_24h(
        self, from_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data 24 hours forward from datetime."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(f"/intensity/{from_str}/fw24h")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_intensity_forward_24h(
        self, from_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data 24 hours forward from datetime (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(f"/intensity/{from_str}/fw24h")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    def get_intensity_forward_48h(
        self, from_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data 48 hours forward from datetime."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(f"/intensity/{from_str}/fw48h")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_intensity_forward_48h(
        self, from_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data 48 hours forward from datetime (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(f"/intensity/{from_str}/fw48h")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    def get_intensity_past_24h(
        self, from_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data 24 hours in the past from datetime."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(f"/intensity/{from_str}/pt24h")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_intensity_past_24h(
        self, from_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data 24 hours in the past from datetime (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(f"/intensity/{from_str}/pt24h")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    def get_intensity_between_datetimes(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data between two datetimes (max 14 days)."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = self._client.get(f"/intensity/{from_str}/{to_str}")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    async def aget_intensity_between_datetimes(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str]
    ) -> List[IntensityData]:
        """Get carbon intensity data between two datetimes (async)."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = await self.async_client.get(f"/intensity/{from_str}/{to_str}")
        data = self._handle_response(response)
        return IntensityResponse.model_validate(data).data

    # Statistics endpoints
    def get_intensity_statistics(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str]
    ) -> List[StatisticsData]:
        """Get carbon intensity statistics between datetimes (max 30 days)."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = self._client.get(f"/intensity/stats/{from_str}/{to_str}")
        data = self._handle_response(response)
        return StatisticsResponse.model_validate(data).data

    async def aget_intensity_statistics(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str]
    ) -> List[StatisticsData]:
        """Get carbon intensity statistics between datetimes (async)."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = await self.async_client.get(f"/intensity/stats/{from_str}/{to_str}")
        data = self._handle_response(response)
        return StatisticsResponse.model_validate(data).data

    def get_intensity_statistics_with_blocks(
        self,
        from_dt: Union[datetime, str],
        to_dt: Union[datetime, str],
        block_hours: int,
    ) -> List[StatisticsData]:
        """Get block average carbon intensity statistics (block 1-24 hours)."""
        if not 1 <= block_hours <= 24:
            raise ValueError("Block hours must be between 1 and 24")

        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = self._client.get(
            f"/intensity/stats/{from_str}/{to_str}/{block_hours}"
        )
        data = self._handle_response(response)
        return StatisticsResponse.model_validate(data).data

    async def aget_intensity_statistics_with_blocks(
        self,
        from_dt: Union[datetime, str],
        to_dt: Union[datetime, str],
        block_hours: int,
    ) -> List[StatisticsData]:
        """Get block average carbon intensity statistics (async)."""
        if not 1 <= block_hours <= 24:
            raise ValueError("Block hours must be between 1 and 24")

        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = await self.async_client.get(
            f"/intensity/stats/{from_str}/{to_str}/{block_hours}"
        )
        data = self._handle_response(response)
        return StatisticsResponse.model_validate(data).data

    # Generation mix endpoints
    def get_current_generation_mix(self) -> GenerationData:
        """Get generation mix for current half hour."""
        response = self._client.get("/generation")
        data = self._handle_response(response)
        return GenerationResponse.model_validate(data).data

    async def aget_current_generation_mix(self) -> GenerationData:
        """Get generation mix for current half hour (async)."""
        response = await self.async_client.get("/generation")
        data = self._handle_response(response)
        return GenerationResponse.model_validate(data).data

    def get_generation_mix_past_24h(
        self, from_dt: Union[datetime, str]
    ) -> GenerationData:
        """Get generation mix for past 24 hours from datetime."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(f"/generation/{from_str}/pt24h")
        data = self._handle_response(response)
        return GenerationResponse.model_validate(data).data

    async def aget_generation_mix_past_24h(
        self, from_dt: Union[datetime, str]
    ) -> GenerationData:
        """Get generation mix for past 24 hours from datetime (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(f"/generation/{from_str}/pt24h")
        data = self._handle_response(response)
        return GenerationResponse.model_validate(data).data

    def get_generation_mix_between_datetimes(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str]
    ) -> GenerationData:
        """Get generation mix between two datetimes."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = self._client.get(f"/generation/{from_str}/{to_str}")
        data = self._handle_response(response)
        return GenerationResponse.model_validate(data).data

    async def aget_generation_mix_between_datetimes(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str]
    ) -> GenerationData:
        """Get generation mix between two datetimes (async)."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = await self.async_client.get(f"/generation/{from_str}/{to_str}")
        data = self._handle_response(response)
        return GenerationResponse.model_validate(data).data

    # Regional endpoints
    def get_current_regional_intensity(self) -> List[RegionalFromTo]:
        """Get regional carbon intensity data for current half hour."""
        response = self._client.get("/regional")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    async def aget_current_regional_intensity(self) -> List[RegionalFromTo]:
        """Get regional carbon intensity data for current half hour (async)."""
        response = await self.async_client.get("/regional")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    def get_current_england_intensity(self) -> List[RegionalFromTo]:
        """Get carbon intensity data for England."""
        response = self._client.get("/regional/england")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    async def aget_current_england_intensity(self) -> List[RegionalFromTo]:
        """Get carbon intensity data for England (async)."""
        response = await self.async_client.get("/regional/england")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    def get_current_scotland_intensity(self) -> List[RegionalFromTo]:
        """Get carbon intensity data for Scotland."""
        response = self._client.get("/regional/scotland")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    async def aget_current_scotland_intensity(self) -> List[RegionalFromTo]:
        """Get carbon intensity data for Scotland (async)."""
        response = await self.async_client.get("/regional/scotland")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    def get_current_wales_intensity(self) -> List[RegionalFromTo]:
        """Get carbon intensity data for Wales."""
        response = self._client.get("/regional/wales")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    async def aget_current_wales_intensity(self) -> List[RegionalFromTo]:
        """Get carbon intensity data for Wales (async)."""
        response = await self.async_client.get("/regional/wales")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    def get_intensity_by_postcode(self, postcode: str) -> List[RegionalId]:
        """Get carbon intensity data for specific postcode."""
        response = self._client.get(f"/regional/postcode/{postcode}")
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_intensity_by_postcode(self, postcode: str) -> List[RegionalId]:
        """Get carbon intensity data for specific postcode (async)."""
        response = await self.async_client.get(f"/regional/postcode/{postcode}")
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    def get_intensity_by_region_id(self, region_id: int) -> List[RegionalId]:
        """Get carbon intensity data for specific region ID (1-18)."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        response = self._client.get(f"/regional/regionid/{region_id}")
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_intensity_by_region_id(self, region_id: int) -> List[RegionalId]:
        """Get carbon intensity data for specific region ID (async)."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        response = await self.async_client.get(f"/regional/regionid/{region_id}")
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    # Regional forward/past 24h/48h endpoints
    def get_regional_intensity_forward_24h(
        self, from_dt: Union[datetime, str]
    ) -> List[RegionalFromTo]:
        """Get regional carbon intensity data 24 hours forward."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(f"/regional/intensity/{from_str}/fw24h")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    async def aget_regional_intensity_forward_24h(
        self, from_dt: Union[datetime, str]
    ) -> List[RegionalFromTo]:
        """Get regional carbon intensity data 24 hours forward (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(f"/regional/intensity/{from_str}/fw24h")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    def get_regional_intensity_forward_24h_postcode(
        self, from_dt: Union[datetime, str], postcode: str
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 24 hours forward for postcode."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(
            f"/regional/intensity/{from_str}/fw24h/postcode/{postcode}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_regional_intensity_forward_24h_postcode(
        self, from_dt: Union[datetime, str], postcode: str
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 24 hours forward for postcode (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/fw24h/postcode/{postcode}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    def get_regional_intensity_forward_24h_region(
        self, from_dt: Union[datetime, str], region_id: int
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 24 hours forward for region."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        from_str = self._format_datetime(from_dt)
        response = self._client.get(
            f"/regional/intensity/{from_str}/fw24h/regionid/{region_id}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_regional_intensity_forward_24h_region(
        self, from_dt: Union[datetime, str], region_id: int
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 24 hours forward for region (async)."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/fw24h/regionid/{region_id}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    def get_regional_intensity_forward_48h(
        self, from_dt: Union[datetime, str]
    ) -> List[RegionalFromTo]:
        """Get regional carbon intensity data 48 hours forward."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(f"/regional/intensity/{from_str}/fw48h")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    async def aget_regional_intensity_forward_48h(
        self, from_dt: Union[datetime, str]
    ) -> List[RegionalFromTo]:
        """Get regional carbon intensity data 48 hours forward (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(f"/regional/intensity/{from_str}/fw48h")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    def get_regional_intensity_forward_48h_postcode(
        self, from_dt: Union[datetime, str], postcode: str
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 48 hours forward for postcode."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(
            f"/regional/intensity/{from_str}/fw48h/postcode/{postcode}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_regional_intensity_forward_48h_postcode(
        self, from_dt: Union[datetime, str], postcode: str
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 48 hours forward for postcode (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/fw48h/postcode/{postcode}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    def get_regional_intensity_forward_48h_region(
        self, from_dt: Union[datetime, str], region_id: int
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 48 hours forward for region."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        from_str = self._format_datetime(from_dt)
        response = self._client.get(
            f"/regional/intensity/{from_str}/fw48h/regionid/{region_id}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_regional_intensity_forward_48h_region(
        self, from_dt: Union[datetime, str], region_id: int
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 48 hours forward for region (async)."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/fw48h/regionid/{region_id}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    def get_regional_intensity_past_24h(
        self, from_dt: Union[datetime, str]
    ) -> List[RegionalFromTo]:
        """Get regional carbon intensity data 24 hours in the past."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(f"/regional/intensity/{from_str}/pt24h")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    async def aget_regional_intensity_past_24h(
        self, from_dt: Union[datetime, str]
    ) -> List[RegionalFromTo]:
        """Get regional carbon intensity data 24 hours in the past (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(f"/regional/intensity/{from_str}/pt24h")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    def get_regional_intensity_past_24h_postcode(
        self, from_dt: Union[datetime, str], postcode: str
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 24 hours in the past for postcode."""
        from_str = self._format_datetime(from_dt)
        response = self._client.get(
            f"/regional/intensity/{from_str}/pt24h/postcode/{postcode}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_regional_intensity_past_24h_postcode(
        self, from_dt: Union[datetime, str], postcode: str
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 24 hours in the past for postcode (async)."""
        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/pt24h/postcode/{postcode}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    def get_regional_intensity_past_24h_region(
        self, from_dt: Union[datetime, str], region_id: int
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 24 hours in the past for region."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        from_str = self._format_datetime(from_dt)
        response = self._client.get(
            f"/regional/intensity/{from_str}/pt24h/regionid/{region_id}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_regional_intensity_past_24h_region(
        self, from_dt: Union[datetime, str], region_id: int
    ) -> List[RegionalId]:
        """Get regional carbon intensity data 24 hours in the past for region (async)."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        from_str = self._format_datetime(from_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/pt24h/regionid/{region_id}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    def get_regional_intensity_between_datetimes(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str]
    ) -> List[RegionalFromTo]:
        """Get regional carbon intensity data between datetimes."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = self._client.get(f"/regional/intensity/{from_str}/{to_str}")
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    async def aget_regional_intensity_between_datetimes(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str]
    ) -> List[RegionalFromTo]:
        """Get regional carbon intensity data between datetimes (async)."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/{to_str}"
        )
        data = self._handle_response(response)
        return RegionalFromToResponse.model_validate(data).data

    def get_regional_intensity_between_datetimes_postcode(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str], postcode: str
    ) -> List[RegionalId]:
        """Get regional carbon intensity data between datetimes for postcode."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = self._client.get(
            f"/regional/intensity/{from_str}/{to_str}/postcode/{postcode}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_regional_intensity_between_datetimes_postcode(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str], postcode: str
    ) -> List[RegionalId]:
        """Get regional carbon intensity data between datetimes for postcode (async)."""
        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/{to_str}/postcode/{postcode}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    def get_regional_intensity_between_datetimes_region(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str], region_id: int
    ) -> List[RegionalId]:
        """Get regional carbon intensity data between datetimes for region."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = self._client.get(
            f"/regional/intensity/{from_str}/{to_str}/regionid/{region_id}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data

    async def aget_regional_intensity_between_datetimes_region(
        self, from_dt: Union[datetime, str], to_dt: Union[datetime, str], region_id: int
    ) -> List[RegionalId]:
        """Get regional carbon intensity data between datetimes for region (async)."""
        if not 1 <= region_id <= 18:
            raise ValueError(_REGION_ID_ERROR)

        from_str = self._format_datetime(from_dt)
        to_str = self._format_datetime(to_dt)
        response = await self.async_client.get(
            f"/regional/intensity/{from_str}/{to_str}/regionid/{region_id}"
        )
        data = self._handle_response(response)
        return RegionalIdResponse.model_validate(data).data
