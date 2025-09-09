"""Simple test to verify the package works."""

import sys
import os

# Add the src directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from uk_grid_intensity import CarbonIntensityClient, CarbonIntensityAPIError


def test_import():
    """Test that imports work correctly."""
    print("✓ Import test passed")


def test_client_creation():
    """Test that we can create a client."""
    client = CarbonIntensityClient()
    assert client is not None
    print("✓ Client creation test passed")


def test_exception():
    """Test that we can create the exception."""
    exc = CarbonIntensityAPIError("Test error", 400)
    assert exc.message == "Test error"
    assert exc.status_code == 400
    print("✓ Exception test passed")


if __name__ == "__main__":
    print("Running basic tests...")

    try:
        test_import()
        test_client_creation()
        test_exception()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
