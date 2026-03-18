# Inbound-TMS

Interactive viewer/editor for PlantUML diagrams used in the Inbound TMS project.

## Requirements

- Python 3.11+ (tested with 3.12)
- [Streamlit](https://streamlit.io/)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run inbound_tms_diagram_app.py
```

Then open the URL shown in the console (typically `http://localhost:8501`).

## Notes

- The app renders PlantUML diagrams by generating a PlantUML server URL (no local PlantUML/JVM required).
- If rendering fails, try switching the PlantUML server in the sidebar or switching to PNG format.
