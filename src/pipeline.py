from src.data_fetcher import fetch_weather_data, fetch_energy_data
from src.data_processor import (
    merge_weather_energy,
    clean_merged_data,
    save_clean_data,
    generate_data_quality_report
)
from datetime import date, timedelta
import os

os.makedirs("data/raw", exist_ok=True)

if __name__ == "__main__":
    today = date.today()
    start = today - timedelta(days=90)  # Historical range
    end = today

    print("Fetching weather data...")
    weather_df = fetch_weather_data(
        start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    )
    weather_df.to_csv("data/raw/weather_raw.csv", index=False)

    print("Fetching energy data...")
    energy_df = fetch_energy_data(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    energy_df.to_csv("data/raw/energy_raw.csv", index=False)

    print("Merging and cleaning data...")
    merged_df = merge_weather_energy(weather_df, energy_df)
    clean_df = clean_merged_data(merged_df)

    save_clean_data(clean_df)
    print("✅ Cleaned data saved to data/processed/merged_data.csv")

    generate_data_quality_report(clean_df)



