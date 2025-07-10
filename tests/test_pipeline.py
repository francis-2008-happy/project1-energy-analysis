import pandas as pd
from src.data_fetcher import fetch_weather_data, fetch_energy_data
from src.data_processor import clean_merged_data


def test_weather_data_format():
    # Provide a date range for the fetch function
    df = fetch_weather_data("2024-01-01", "2024-01-10")
    # Example assertions, adjust according to your data structure
    assert not df.empty, "Weather data should not be empty"
    assert "temp_max" in df.columns, "Dataframe should have temp_max column"
    assert "date" in df.columns, "Dataframe should have date column"


def test_energy_data_format():
    # Provide a date range for the fetch function
    df = fetch_energy_data("2024-01-01", "2024-01-10")
    # Example assertions, adjust according to your data structure
    assert not df.empty, "Energy data should not be empty"
    assert "energy_usage_mwh" in df.columns, (
        "Dataframe should have energy_usage_mwh column"
    )
    assert "date" in df.columns, "Dataframe should have date column"


def test_clean_merged_data():
    raw_data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02"]
            ),  # Convert to datetime here
            "city": ["New York", "New York"],
            "temp_max": [32, None],
            "temp_min": [20, 21],
            "energy_usage_mwh": [300, None],
        }
    )

    cleaned = clean_merged_data(raw_data)

    assert cleaned["temp_max"].isnull().sum() == 0, "temp_max should not have nulls"
    assert cleaned["energy_usage_mwh"].isnull().sum() == 0, (
        "energy_usage_mwh should not have nulls"
    )
    assert isinstance(cleaned["date"].iloc[0], pd.Timestamp), (
        "date column should be datetime type"
    )
