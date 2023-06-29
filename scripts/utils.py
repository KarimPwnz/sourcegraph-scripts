import logging

from aiohttp import TCPConnector
from aiohttp_retry import FibonacciRetry, RetryClient


def setup_logging():
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)


def create_client(request_limit, *args, **kwargs):
    return RetryClient(
        raise_for_status=False,
        retry_options=FibonacciRetry(attempts=float("inf"), statuses=[429, 500, 502, 503, 504], max_timeout=float("inf")),
        connector=TCPConnector(limit=request_limit),
        *args,
        **kwargs
    )
