import pytest
from unittest.mock import Mock

from src.core.retry import retry_read_operation


def test_retry_success_after_failure():

    operation = Mock(
        side_effect=[
            ConnectionError("Temporary failure"),
            {"stock": 25}
        ]
    )

    result = retry_read_operation(
        operation,
        max_attempts=3,
        delay=0
    )

    assert result == {"stock": 25}
    assert operation.call_count == 2


def test_retry_max_attempts():

    operation = Mock(
        side_effect=ConnectionError("Network unavailable")
    )

    with pytest.raises(ConnectionError):
        retry_read_operation(
            operation,
            max_attempts=3,
            delay=0
        )

    assert operation.call_count == 3


def test_no_retry_for_http_400():

    import httpx

    response = httpx.Response(400, request=httpx.Request("GET", "https://example.com"))

    operation = Mock(
        side_effect=httpx.HTTPStatusError(
            "Bad request",
            request=response.request,
            response=response
        )
    )

    with pytest.raises(httpx.HTTPStatusError):
        retry_read_operation(
            operation,
            max_attempts=3,
            delay=0
        )

    assert operation.call_count == 1