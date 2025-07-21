# project1-energy-analysis
# README.md file

## 🔌 US Weather + Energy Analysis Pipeline

This project builds a data pipeline that combines **daily weather data** from the NOAA API and **daily electricity consumption data** from the EIA API for five U.S. cities. It helps visualize how temperature affects energy usage to improve forecasting and efficiency.

---

## 📊 Key Features

### ✅ Data Pipeline

* Fetches high/low temperature and energy usage for:

* New York, Chicago, Houston, Phoenix, Seattle
* Supports 90 days of historical data for analysis
* Handles API failures gracefully (error logging, retry logic, etc.)
* Uses `.env` and `config.yaml` for secrets and configuration

### ✅ Data Quality Checks

* Detects missing values
* Flags extreme outliers (e.g., >130°F, < -50°F, negative energy usage)
* Tracks data freshness

### ✅ Streamlit Dashboard

* **Geographic Overview:** Map with current stats per city
* **Time Series:** Temp + energy trends with city selection
* **Correlation Scatter Plot:** Trendline + r² and hover info
* **Usage Patterns Heatmap:** Day-of-week vs temperature ranges

### ✅ AI Collaboration

* Documented in `AI_USAGE.md` (tool usage, prompts, mistakes, lessons)

---

## 🏗️ Project Structure

```
project1-energy-analysis/
├── README.md                 # This file
├── AI_USAGE.md              # AI interaction report
├── pyproject.toml           # Python dependencies (use uv or poetry)
├── config/
│   └── config.yaml          # Cities, station IDs, API keys
├── src/
│   ├── data_fetcher.py      # NOAA + EIA API handlers
│   ├── data_processor.py    # Cleaning + merging logic
│   ├── analysis.py          # Correlation & patterns (optional)
│   └── pipeline.py          # Main orchestrator
├── dashboards/
│   └── app.py               # Streamlit dashboard
├── logs/
│   └── pipeline.log         # Daily log outputs
├── data/
│   ├── raw/                 # Unprocessed API data
│   └── processed/           # Cleaned + merged data
├── tests/
│   └── test_pipeline.py     # Basic validation tests
└── video_link.md            # URL to final presentation
```

---

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/project1-energy-analysis.git
cd project1-energy-analysis
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
uv pip install
pip install -r requirements.txt
```

### 4. Configure secrets

* Add your API keys to `.env`
* Edit `config/config.yaml` to list the cities/stations

### 5. Run the pipeline

```bash
python -m src.pipeline
```

### 6. Launch the dashboard

```bash
streamlit run dashboards/app.py
```

### 7. Texts/test_pineline 

```bash
PYTHONPATH=. pytest tests/test_pipeline.py
```
---

## 📈 Example Insight

> In Phoenix, energy usage sharply increases once temperatures rise above 85°F, showing a strong positive correlation (r² = 0.81). This confirms the cooling demand hypothesis.

---

## 📹 Final Presentation

See [`video_link.md`](video_link.md) for the demo walkthrough (3 mins).

---

## 👥 Author & Credits

* Created by: **Francis Happy**
* Project from: **Pioneer Artificia Intelligent Academy**
* Guided by: **IBM Data Science Course** , **OpenAI ChatGPT** + **Coursera template (BYU-Idaho Pathway)**, 
* Partner: **hmhmhm**
* Libraries: `pandas`, `plotly`, `streamlit`, `requests`, `statsmodels`, `pyyaml`

---

## ✅ Checklist

*
## ✅ Link to the Streamlit Dashboard
https://francis-2008-happy-project1-energy-analysi-dashboardsapp-bshewp.streamlit.app/