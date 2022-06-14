from aiohttp_retry import RetryClient, FibonacciRetry
from aiohttp import TCPConnector
import logging


def setup_logging():
    logging.basicConfig(
        format="[%(levelname)s] %(message)s", level=logging.INFO)


def create_client(request_limit, *args, **kwargs):
    return RetryClient(
        raise_for_status=False, retry_options=FibonacciRetry(
            attempts=5, statuses=[429, 500, 502, 503, 504]), connector=TCPConnector(limit=request_limit), *args, **kwargs)
