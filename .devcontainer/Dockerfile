FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

# Install system packages
RUN sudo apt-get update && sudo apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    zip \
    build-essential \
    ffmpeg \
    ripgrep \
    fd-find \
    tree \
    jq \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir -U \
    uv \
    pytest \
    ruff \
    black \
    mypy

# Install latest Node.js LTS
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && \
    sudo apt-get install -y nodejs

# Make sure locally-installed MCP executables are found
ENV PATH="/home/vscode/.local/bin:${PATH}"

WORKDIR /workspace