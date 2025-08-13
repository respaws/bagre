#!/usr/bin/env bash
set -e
# Start all five apps on different ports in background tabs
(
  cd app_bagre && python app.py --port 5001
) &
(
  cd app_bagre2 && python app.py --port 5002
) &
(
  cd app_bagre3 && python app.py --port 5003
) &
(
  cd app_bagre4 && python app.py --port 5004
) &
(
  cd app_bagre5 && python app.py --port 5005
) &
echo "Apps iniciados. Acesse: http://localhost:5001 ... 5005"
wait
