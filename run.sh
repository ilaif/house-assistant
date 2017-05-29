#!/usr/bin/env bash

cd /home/pi/

amixer cset numid=3 1  # Switch to aux
sudo /usr/bin/python3 /home/pi/house-assistant/main.py

cd /