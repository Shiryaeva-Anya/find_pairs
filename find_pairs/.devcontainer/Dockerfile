FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*
