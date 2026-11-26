import time
import httpx


def retry_read_operation(operation, max_attempts=3, delay=1):

    for attempt in range(1, max_attempts + 1):

        try:
            return operation()

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.HTTPStatusError,
            ConnectionError,
            TimeoutError
        ) as error:

            # Do not retry client-side HTTP errors (4xx)
            if (
                isinstance(error, httpx.HTTPStatusError)
                and error.response.status_code < 500
            ):
                raise

            if attempt == max_attempts:
                raise

            print(
                f"[RETRY] Attempt {attempt} failed: "
                f"{error}. Retrying..."
            )

            time.sleep(delay)