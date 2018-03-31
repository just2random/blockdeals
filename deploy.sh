#!/bin/sh
cd ~/blockdeals
git pull \
  && docker build -t blockdeals . \
  && docker stop blockdeals \
  && docker rm blockdeals \
  && docker run -v /blockdeals.cfg:/blockdeals/blockdeals.cfg:ro --link mongo:mongodb -p 127.0.0.1:5000:8000 -d --name blockdeals blockdeals
