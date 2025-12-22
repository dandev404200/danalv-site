"""Middleware for logging and request tracking."""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

logger = logging.getLogger("app.middleware")


class RequestLoggingRoute(APIRoute):
    """Custom route class that logs all requests and responses.

    Automatically tracks:
    - Unique request ID for correlation
    - Request method, path, and query parameters
    - Response status code
    - Request duration in milliseconds
    - Errors with full stack traces
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # Generate unique request ID for tracking
            request_id = str(uuid.uuid4())[:8]
            request.state.request_id = request_id

            # Log incoming request
            logger.info(
                f"[{request_id}] Incoming: {request.method} {request.url.path} "
                f"- Query: {dict(request.query_params)}"
            )

            # Track timing
            start_time = time.time()

            try:
                # Call the actual route handler
                response = await original_route_handler(request)

                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log successful response
                logger.info(
                    f"[{request_id}] Completed: {request.method} {request.url.path} "
                    f"- Status: {response.status_code} - Duration: {duration_ms:.2f}ms"
                )

                return response

            except Exception as e:
                # Calculate duration even for errors
                duration_ms = (time.time() - start_time) * 1000

                # Log error with full stack trace
                logger.error(
                    f"[{request_id}] Failed: {request.method} {request.url.path} "
                    f"- Error: {type(e).__name__}: {str(e)} - Duration: {duration_ms:.2f}ms",
                    exc_info=True,
                )
                raise

        return custom_route_handler
