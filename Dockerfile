# Use a lightweight Python image
FROM python:3.12.1-slim

# Set up environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    SAVE_DIR="/app/outputs" \
    DATA_LOCATIONS="/app/data" \
    MODEL="gpt-4o"

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        software-properties-common \
        binutils \
        python3-pip \
        python3-dev \
        python3-launchpadlib \
        gdal-bin \
        libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL include paths for compilation
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# Copy all files to the container
COPY . .

# Create necessary directories
RUN mkdir -p ${SAVE_DIR} ${DATA_LOCATIONS}

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the API port
EXPOSE 8000

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "llm_geo_api:app", "--host", "0.0.0.0", "--port", "8000"]
