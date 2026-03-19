FROM python:3.12-slim

# Create user and set working directory
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Copy files and set ownership immediately
COPY --chown=appuser:appuser pyproject.toml requirements.txt inbound_tms_diagram_app.py ./
COPY --chown=appuser:appuser README.md ./

# Switch to the appuser to avoid permission issues
USER appuser

# Install pip dependencies and the Python package (as the regular user)
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir .

# Ensure user can run installed console scripts.
ENV PATH="/home/appuser/.local/bin:${PATH}"

EXPOSE 8501

CMD ["streamlit", "run", "inbound_tms_diagram_app.py", "--server.port=8501", "--server.address=0.0.0.0"]