#!/usr/bin/env bash
cd /Robot/CurrentArduinoCode/stage2
git add -A
git commit -m "new uploaded arduino code for stage2"
git push
pio run -t upload
