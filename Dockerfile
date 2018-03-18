FROM python:alpine3.6

ADD . /blockdeals
WORKDIR /blockdeals

RUN set -x \
  && apk add -U build-base openssl-dev \
  && pip install -r requirements.txt

ENTRYPOINT ["gunicorn"]
CMD ["-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]
