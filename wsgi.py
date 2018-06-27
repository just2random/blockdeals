import logging
from fomodeals import app
from steem import Steem

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(logging.INFO)
