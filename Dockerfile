# Dockerfile for running the Inbound TMS diagram viewer
# Build:
#   docker build -t inbound-tms-diagram .
# Run:
#   docker run --rm -p 8501:8501 inbound-tms-diagram

FROM python:3.12-slim

# Keep image small and set up a non-root user.
RUN useradd --create-home appuser
WORKDIR /home/appuser/app
USER appuser

# Copy only what we need.
COPY --chown=appuser:appuser pyproject.toml requirements.txt inbound_tms_diagram_app.py ./

# Install dependencies via pip. Use --no-cache-dir to reduce image size.
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir .

# Expose Streamlit default port.
EXPOSE 8501

CMD ["inbound-tms-diagram"]
