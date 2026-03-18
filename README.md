# Inbound-TMS

[![Build](https://github.com/fburgos2592/Inbound-TMS/actions/workflows/build.yml/badge.svg)](https://github.com/fburgos2592/Inbound-TMS/actions/workflows/build.yml)

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

## Install as a Python package (optional)

From a fresh checkout, you can install and run the app like a normal Python package:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .

# then run
inbound-tms-diagram
```

## Single-file executable (optional)

A convenient single-file archive can be built with `shiv` and run directly with Python (no install required):

```bash
./build_executable.sh
python dist/inbound-tms-diagram.pyz
```

This produces `dist/inbound-tms-diagram.pyz`, which starts the Streamlit app the same as running `streamlit run`.

> ✅ A GitHub Actions workflow is configured to build and upload `dist/inbound-tms-diagram.pyz` on every push/PR to `main`.

## Docker (optional)

If you prefer running the app in a container, build and run via Docker:

```bash
docker build -t inbound-tms-diagram .
docker run --rm -p 8501:8501 inbound-tms-diagram
```

Then visit `http://localhost:8501` in your browser.

## Notes

- The app renders PlantUML diagrams by generating a PlantUML server URL (no local PlantUML/JVM required).
- If rendering fails, try switching the PlantUML server in the sidebar or switching to PNG format.
