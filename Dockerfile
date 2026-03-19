FROM python:3.12-slim

RUN useradd --create-home appuser
WORKDIR /home/appuser/app
USER appuser

COPY --chown=appuser:appuser pyproject.toml requirements.txt inbound_tms_diagram_app.py ./

RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "inbound_tms_diagram_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
