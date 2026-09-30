FROM mambaorg/micromamba:2.3.3
USER root
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3 \
    && rm -rf /var/lib/apt/lists/*
USER $MAMBA_USER
