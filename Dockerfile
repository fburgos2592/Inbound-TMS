FROM python:3.12-slim

RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Always use --chown on COPY!
COPY --chown=appuser:appuser pyproject.toml requirements.txt inbound_tms_diagram_app.py ./
COPY --chown=appuser:appuser README.md ./

# Clean up possible leftover egg-info, and extra safety chown
RUN rm -rf inbound_tms_diagram.egg-info && chown -R appuser:appuser /home/appuser/app

USER appuser

RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir .

ENV PATH="/home/appuser/.local/bin:${PATH}"

EXPOSE 8501

CMD ["streamlit", "run", "inbound_tms_diagram_app.py", "--server.port=8501", "--server.address=0.0.0.0"]