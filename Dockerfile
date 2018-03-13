FROM python:alpine3.6

ADD . /blockdeals
WORKDIR /blockdeals

RUN set -x \
  && pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["config.py"]
