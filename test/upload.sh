#!/usr/bin/env bash
cd /Robot/CurrentArduinoCode/test
git add -A
git commit -m "new uploaded arduino code for test"
git push
pio run -t upload
