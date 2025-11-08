FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for building Pyfhel/SEAL cleanly
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3-dev \
    build-essential cmake ninja-build git \
    zlib1g-dev libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip toolchain
RUN python3 -m pip install --upgrade pip setuptools wheel

# ---- Build deps FIRST (so our flags and headers are visible during build)
# Pyfhel 3.4.x expects these present at build time.
RUN pip3 install "cython<3.1" pybind11 toml "numpy==1.24.3"

# Install Pyfhel from PyPI (source build, no wheel URL)
# We disable build isolation so it sees the cython/numpy/pybind11 we just installed.
RUN pip3 install --no-build-isolation --verbose "pyfhel==3.4.2"

# Now install the rest of your requirements (without re-pinning pyfhel/numpy)
# --- if your requirements.txt currently contains those, remove those two lines.
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy your project
COPY external_program.py player.py server.py demo.py demo_2.py blockchain_interface.py deployment_ganache.json F1AIRacing.sol deploy_contract.py ./

RUN mkdir -p /app/output

CMD ["python3", "demo.py"]
