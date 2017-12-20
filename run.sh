#!/bin/bash
cd static_web
sudo python3 -m http.server 80 >/dev/null &
cd ..
cd tflsgo_comp
python app.py
