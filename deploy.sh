#!/bin/sh
cd ~/blockdeals
git pull
docker stop blockdeals
docker rm blockdeals
docker build -t blockdeals . && docker run -p 127.0.0.1:5000:8000 -d --name blockdeals blockdeals
