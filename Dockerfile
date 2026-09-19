# EcoVision — deployment image
# Build:  docker build -t ecovision .
# Run:    docker run -p 8501:8501 ecovision
# Then open http://localhost:8501

FROM python:3.11-slim

WORKDIR /app

# curl is needed only for the HEALTHCHECK below (to ping Streamlit's
# own health endpoint); nothing else in this image needs system
# packages, which is part of why it stays small.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# torch/torchvision are installed FROM THE CPU-ONLY WHEEL INDEX,
# separately from requirements.txt. The default PyPI torch wheel
# bundles CUDA libraries for GPU support — several hundred MB to a
# few GB depending on version — which are dead weight here, since
# this container only ever runs inference on a CPU. The CPU-only
# wheel is a fraction of the size and installs faster, directly
# serving Day 5's goal of a small, fast container.
RUN pip install --no-cache-dir --retries 10 --timeout 120 \
    torch==2.3.1 torchvision==0.18.1 \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir --retries 10 --timeout 120 -r requirements.txt

# Only what the running app actually needs — .dockerignore already
# excludes the dataset and training scripts, but listing intent here
# via COPY . . plus that ignore file (rather than one giant COPY of
# everything with no ignore file) is what keeps this reproducible if
# the ignore file is ever edited by mistake: the image still only
# grows if a real project file is added, not if a training artifact
# reappears.
COPY . .

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0"]