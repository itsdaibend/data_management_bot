import logging

from utils import LOGGING_FORMAT

config = logging.basicConfig(
    level=logging.INFO, format=LOGGING_FORMAT, handlers=[logging.StreamHandler()]
)
