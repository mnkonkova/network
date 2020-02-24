#!/bin/bash
if [[ "$HW1_MODE" = "server" ]]; then
  python3 server.py
elif [[ "$HW1_MODE" = "tests" ]]; then
  python3 client.py
fi