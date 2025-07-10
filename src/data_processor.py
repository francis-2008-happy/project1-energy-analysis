import pandas as pd
import os
from datetime import datetime
import json


def merge_weather_energy(weather_df, energy_df):
    # Make sure date columns are proper datetime
    weather_df["date"] = pd.to_datetime(weather_df["date"])
    energy_df["date"] = pd.to_datetime(energy_df["date"])

    # Merge on city and date
    merged_df = pd.merge(weather_df, energy_df, on=["city", "date"], how="outer")

    # Sort by city and date for better readability
    merged_df = merged_df.sort_values(["city", "date"])

    return merged_df



def clean_merged_data(df):
    # Fix deprecation warning for fillna
    df["temp_max"] = df["temp_max"].ffill()
    df["temp_min"] = df["temp_min"].ffill()
    df["energy_usage_mwh"] = df["energy_usage_mwh"].ffill()

    # Ensure numeric data types (especially for energy column)
    df["temp_max"] = pd.to_numeric(df["temp_max"], errors="coerce")
    df["temp_min"] = pd.to_numeric(df["temp_min"], errors="coerce")
    df["energy_usage_mwh"] = pd.to_numeric(df["energy_usage_mwh"], errors="coerce")

    # Drop any rows that still have NaNs
    df.dropna(inplace=True)

    # Round for presentation
    df["temp_max"] = df["temp_max"].round(1)
    df["temp_min"] = df["temp_min"].round(1)
    df["energy_usage_mwh"] = df["energy_usage_mwh"].round(2)

    return df



def save_clean_data(df, output_path="data/processed/merged_data.csv"):
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_path, index=False)


# these functions below cleaning the functions by adding data quality checks

def check_missing_values(df):
    missing = df.isnull().sum()
    total_rows = len(df)
    report = {
        col: {
            "missing_count": int(missing[col]),
            "missing_percent": round(100 * missing[col] / total_rows, 2),
        }
        for col in df.columns
        if missing[col] > 0
    }
    return report


def check_outliers(df):
    outliers = []

    for _, row in df.iterrows():
        if row["temp_max"] > 130 or row["temp_min"] < -50:
            outliers.append(
                {
                    "city": row["city"],
                    "date": row["date"],
                    "type": "Temperature",
                    "value": f"{row['temp_max']}/{row['temp_min']}",
                }
            )
        if row["energy_usage_mwh"] < 0:
            outliers.append(
                {
                    "city": row["city"],
                    "date": row["date"],
                    "type": "Energy",
                    "value": row["energy_usage_mwh"],
                }
            )

    return outliers


def check_data_freshness(df):
    latest_date = pd.to_datetime(df["date"]).max().date()
    today = datetime.utcnow().date()
    days_old = (today - latest_date).days

    if days_old > 2:
        return {"fresh": False, "latest_date": str(latest_date), "days_old": days_old}
    else:
        return {"fresh": True, "latest_date": str(latest_date), "days_old": days_old}


def generate_data_quality_report(df, output_dir="data/processed"):
    print("🧪 DATA QUALITY REPORT")
    print("=" * 30)

    # Run checks
    missing_report = check_missing_values(df)
    outliers = check_outliers(df)
    freshness = check_data_freshness(df)

    # Console output
    if missing_report:
        print("🚨 Missing Values Found:")
        for col, vals in missing_report.items():
            print(
                f" - {col}: {vals['missing_count']} missing ({vals['missing_percent']}%)"
            )
    else:
        print("✅ No missing values.")

    if outliers:
        print(f"🚨 Outliers Found: {len(outliers)}")
        for o in outliers[:5]:
            print(f" - {o['type']} outlier in {o['city']} on {o['date']}: {o['value']}")
    else:
        print("✅ No outliers found.")

    if freshness["fresh"]:
        print(f"✅ Data is fresh. Latest date: {freshness['latest_date']}")
    else:
        print(
            f"⚠️ Data might be stale. Latest date: {freshness['latest_date']} ({freshness['days_old']} days old)"
        )

    print("=" * 30)

    # Save to files
    os.makedirs(output_dir, exist_ok=True)

    # Save as .txt
    with open(os.path.join(output_dir, "data_quality_report.txt"), "w") as f:
        f.write("DATA QUALITY REPORT\n")
        f.write("=" * 30 + "\n")
        if missing_report:
            f.write("Missing Values:\n")
            for col, vals in missing_report.items():
                f.write(
                    f" - {col}: {vals['missing_count']} missing ({vals['missing_percent']}%)\n"
                )
        else:
            f.write("No missing values.\n")

        if outliers:
            f.write(f"\nOutliers Found: {len(outliers)}\n")
            for o in outliers[:5]:
                f.write(
                    f" - {o['type']} outlier in {o['city']} on {o['date']}: {o['value']}\n"
                )
        else:
            f.write("\nNo outliers found.\n")

        if freshness["fresh"]:
            f.write(f"\nData is fresh. Latest date: {freshness['latest_date']}\n")
        else:
            f.write(
                f"\nData might be stale. Latest date: {freshness['latest_date']} ({freshness['days_old']} days old)\n"
            )

    # Save as .json
    full_report = {
        "missing_values": missing_report,
        "outliers": outliers,
        "freshness": freshness,
    }

    with open(os.path.join(output_dir, "data_quality_report.json"), "w") as f:
        json.dump(full_report, f, indent=4, default=str)