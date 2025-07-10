import os
import requests
import time
import logging
import pandas as pd
from dotenv import load_dotenv
import yaml

load_dotenv()

# Setup Logging
logging.basicConfig(
    filename="logs/pipeline.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

NOAA_TOKEN = os.getenv("NOAA_TOKEN")
NOAA_BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"


def load_city_config(config_path="config/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)["cities"]


def fetch_weather_for_city(station_id, start_date, end_date, max_retries=5):
    headers = {"token": NOAA_TOKEN}
    params = {
        "datasetid": "GHCND",
        "stationid": station_id,
        "startdate": start_date,
        "enddate": end_date,
        "datatypeid": "TMAX,TMIN",
        "units": "metric",
        "limit": 1000,
    }

    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(NOAA_BASE_URL, headers=headers, params=params)
            if response.status_code == 429:  # Rate limit
                wait = 2**retries
                logging.warning(f"Rate limited. Retrying in {wait} seconds...")
                time.sleep(wait)
                retries += 1
                continue
            response.raise_for_status()
            data = response.json().get("results", [])
            return data
        except Exception as e:
            logging.error(f"Failed to fetch data for {station_id}: {e}")
            retries += 1
            time.sleep(2**retries)
    return []


def fetch_weather_data(start_date, end_date):
    cities = load_city_config()
    all_data = []

    for city in cities:
        raw_data = fetch_weather_for_city(city["noaa_station_id"], start_date, end_date)
        for entry in raw_data:
            all_data.append(
                {
                    "city": city["name"],
                    "date": entry["date"][:10],
                    "datatype": entry["datatype"],
                    "value": entry["value"],  # In tenths of °C
                }
            )

    df = pd.DataFrame(all_data)

    # Pivot to get TMAX and TMIN in same row
    df = df.pivot_table(
        index=["city", "date"], columns="datatype", values="value"
    ).reset_index()
    df.rename(columns={"TMAX": "temp_max", "TMIN": "temp_min"}, inplace=True)

    # Convert to Fahrenheit from tenths of °C
    df["temp_max"] = df["temp_max"] / 10 * 9 / 5 + 32
    df["temp_min"] = df["temp_min"] / 10 * 9 / 5 + 32

    return df


#Energy usage example


EIA_API_KEY = os.getenv("EIA_API_KEY")
EIA_BASE_URL = "https://api.eia.gov/v2/electricity/rto/daily-region-data/data/"


def fetch_energy_for_region(region_code, start_date, end_date, max_retries=5):
    params = {
        "api_key": EIA_API_KEY,
        "start": start_date,
        "end": end_date,
        "facets[respondent][]": region_code,
        "data[]": "value",
    }

    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(EIA_BASE_URL, params=params)
            if response.status_code == 429:
                wait = 2**retries
                logging.warning(
                    f"EIA rate limited. Retrying {region_code} in {wait}s..."
                )
                time.sleep(wait)
                retries += 1
                continue
            response.raise_for_status()
            data = response.json().get("response", {}).get("data", [])
            return data
        except Exception as e:
            logging.error(f"Failed to fetch energy data for {region_code}: {e}")
            retries += 1
            time.sleep(2**retries)
    return []


def fetch_energy_data(start_date, end_date):
    cities = load_city_config()
    all_energy = []

    for city in cities:
        region = city["eia_region_code"]
        city_name = city["name"]

        raw_data = fetch_energy_for_region(region, start_date, end_date)

        for entry in raw_data:
            all_energy.append(
                {
                    "city": city_name,
                    "date": entry.get("period"),
                    "energy_usage_mwh": entry.get("value"),
                }
            )

    df = pd.DataFrame(all_energy)
    return df
