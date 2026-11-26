FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*
