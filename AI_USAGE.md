# 🤖 AI Collaboration Report - US Weather + Energy Analysis

## 🧠 Tools Used

- **ChatGPT (OpenAI GPT-4o)**: For design, code generation, bug fixing, and Streamlit dashboard ideas.
- **Python + pytest**: Tested logic like API fetching, data cleaning.
- **Streamlit**: Dashboard UI for visualizing trends and correlation.

## 📝 Prompts Examples

> "Guide me step-by-step through a data science pipeline project. I’m a beginner."

> "Add a city dropdown and a date range slider to a Streamlit heatmap."

> "Fix `ModuleNotFoundError: No module named 'src'` in pytest."

## 💡 What AI Helped With

- Understanding the flow of a typical data pipeline
- Modifying the  `fetch_weather_data` and `fetch_energy_data` functions
- Handling errors (e.g., `.env` setup, retry logic)
- Modifying interactive dashboards with Plotly + Streamlit
- Writing and fixing automated tests
- Debugging issues like `PYTHONPATH` and `TypeError`

## ⚠️ Mistakes Made

- forgot to install some of the project dependecies which cause lot of problem for me while running the codes
- Initially forgot to pass arguments to `fetch_weather_data()` during tests
- Didn’t convert date strings to `datetime` before checking `isinstance`
- Missed setting `PYTHONPATH=.`, which broke relative imports in tests

## 🎓 Lessons Learned

- Install all dependecies before running my porject
- Always verify function signatures when testing
- AI can help debug, but you must interpret errors carefully
- Set `PYTHONPATH=.` or use editable install (`pip install -e .`) when testing packages
- Writing small test cases improves understanding of each module

---

## 🏁 Summary

Using AI helped speed up development, clarify design goals, and troubleshoot faster—especially for a first-time data science project. It’s like pair programming with a patient assistant.
