FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl bash git build-essential libssl-dev pkg-config nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Install DFINITY SDK (dfx)
ENV DFXVM_INIT_YES=1
RUN curl -fsSL https://internetcomputer.org/install.sh | bash

# Add dfx to PATH
ENV PATH="/root/.local/share/dfx/bin:${PATH}"

WORKDIR /work
