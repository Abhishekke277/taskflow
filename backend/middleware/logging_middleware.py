import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware #BaseHTTPMiddleware is a base class for creating custom middleware in Starlette/FastAPI. It provides a convenient way to define middleware that can process requests and responses.
from starlette.requests import Request

# Basic logger setup — prints to console
logging.basicConfig(level=logging.INFO, format="%(message)s") #this configures the logging module to log messages at the INFO level or higher, and it sets the format of the log messages to just display the message itself without any additional metadata like timestamps or log levels.
logger = logging.getLogger("taskflow")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware that runs on every request. Logs the HTTP
    method, path, and processing time in milliseconds.
    Satisfies Section 1, Task 7.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time_ms = (time.time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} - "
            f"completed in {process_time_ms:.2f}ms - "
            f"status {response.status_code}"
        )

        return response