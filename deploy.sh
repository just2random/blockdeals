#!/bin/sh
cd ~/fomodeals
git pull https://github.com/just2random/fomodeals.git \
  && docker build -t fomodeals . \
  && docker stop fomodeals \
  && docker rm fomodeals \
  && docker run -v /fomodeals.cfg:/fomodeals/fomodeals.cfg:ro --link=fomomongo:mongodb -p 127.0.0.1:5000:8000 -d --name=fomodeals --restart=unless-stopped fomodeals
