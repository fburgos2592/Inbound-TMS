FROM python:3.12-slim

# Create user and set working directory
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Copy files (as root, default)
COPY pyproject.toml requirements.txt inbound_tms_diagram_app.py ./
COPY README.md ./

# Fix permissions for non-root install/build steps:
RUN chown -R appuser:appuser /home/appuser/app

# Switch to non-root user
USER appuser

# Install dependencies and your package
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir .

ENV PATH="/home/appuser/.local/bin:${PATH}"

EXPOSE 8501

CMD ["streamlit", "run", "inbound_tms_diagram_app.py", "--server.port=8501", "--server.address=0.0.0.0"]