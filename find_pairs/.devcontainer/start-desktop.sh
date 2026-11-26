#!/bin/bash

if ! pgrep -x Xvfb >/dev/null; then
    Xvfb :0 -screen 0 1280x800x24 &
    sleep 2
fi

export DISPLAY=:0

if ! pgrep -x fluxbox >/dev/null; then
    fluxbox &
fi

if ! pgrep -x x11vnc >/dev/null; then
    x11vnc -display :0 -forever -shared -nopw -rfbport 5900 -bg
fi

if ! pgrep -f "websockify.*6080" >/dev/null; then
    websockify --web=/usr/share/novnc 6080 localhost:5900 &
fi

echo "Royal Purple desktop is ready!"
