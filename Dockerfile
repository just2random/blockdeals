FROM python:alpine3.6

ENV FOMODEALS_SETTINGS="/fomodeals/fomodeals.cfg"
EXPOSE 8000

RUN set -x \
  && apk add -U build-base openssl-dev git musl-dev linux-headers \
  && addgroup uwsgi \
  && adduser -D -G uwsgi uwsgi

ADD . /fomodeals
WORKDIR /fomodeals

RUN set -x \
  && pip install -r requirements.txt

USER uwsgi
ENTRYPOINT [ "uwsgi" ]
CMD [ "--http", "0.0.0.0:8000", "--module", "wsgi:app", "--processes", "1", "--threads", "8", "--enable-threads"]
