FROM python:alpine3.6

ADD . /blockdeals
WORKDIR /blockdeals

RUN set -x \
  && apk add -U build-base openssl-dev git \
  && pip install -r requirements.txt

ENV BLOCKDEALS_SETTINGS="/blockdeals/blockdeals.cfg" UNLOCK="blockdeals"

EXPOSE 8000

ENTRYPOINT ["gunicorn"]
CMD ["-w", "1", "-b", "0.0.0.0:8000", "wsgi:app"]
