
import argparse
import asyncio
import statistics
import time

import httpx


async def send_request(client, url, payload=None):
    start = time.perf_counter()

    try:
        if payload:
            response = await client.post(url, json=payload)
        else:
            response = await client.get(url)

        latency = (time.perf_counter() - start) * 1000

        return {
            "success": response.is_success,
            "latency": latency,
            "status": response.status_code,
        }

    except httpx.HTTPError as exc:
        latency = (time.perf_counter() - start) * 1000

        return {
            "success": False,
            "latency": latency,
            "status": str(exc),
        }


async def run_benchmark(args):
    url = f"{args.base_url.rstrip('/')}{args.endpoint}"

    payload = None

    if args.endpoint == "/chat":
        payload = {
            "message": args.message
        }

    limits = httpx.Limits(
        max_connections=args.concurrency,
        max_keepalive_connections=args.concurrency,
    )

    timeout = httpx.Timeout(120.0)

    async with httpx.AsyncClient(
        limits=limits,
        timeout=timeout
    ) as client:

        print(f"\nBenchmark URL: {url}")
        print(f"Total requests: {args.requests}")
        print(f"Concurrency: {args.concurrency}")
        print("\nRunning benchmark...\n")

        start_time = time.perf_counter()

        semaphore = asyncio.Semaphore(args.concurrency)

        async def limited_request():
            async with semaphore:
                return await send_request(
                    client,
                    url,
                    payload
                )

        results = await asyncio.gather(
            *[
                limited_request()
                for _ in range(args.requests)
            ]
        )

        total_time = time.perf_counter() - start_time

    successful = [
        item for item in results if item["success"]
    ]

    failed = [
        item for item in results if not item["success"]
    ]

    latencies = [
        item["latency"] for item in successful
    ]

    print("=" * 50)
    print("LATENCY BENCHMARK RESULTS")
    print("=" * 50)

    print(f"Total requests       : {len(results)}")
    print(f"Successful requests  : {len(successful)}")
    print(f"Failed requests      : {len(failed)}")
    print(f"Total duration       : {total_time:.3f} seconds")

    if latencies:
        sorted_latencies = sorted(latencies)

        def percentile(values, percent):
            index = round((len(values) - 1) * percent / 100)
            return values[index]

        print(f"Minimum latency      : {min(latencies):.2f} ms")
        print(f"Maximum latency      : {max(latencies):.2f} ms")
        print(f"Average latency      : {statistics.mean(latencies):.2f} ms")
        print(f"Median latency (P50) : {percentile(sorted_latencies, 50):.2f} ms")
        print(f"P95 latency          : {percentile(sorted_latencies, 95):.2f} ms")
        print(f"P99 latency          : {percentile(sorted_latencies, 99):.2f} ms")

    print(
        f"Requests per second : "
        f"{len(successful) / total_time:.2f}"
    )

    print("=" * 50)

    if failed:
        print("\nFailed request details:")
        for item in failed[:5]:
            print(f"Status: {item['status']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI microservice latency benchmark"
    )

    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000"
    )

    parser.add_argument(
        "--endpoint",
        choices=["/health", "/chat"],
        default="/health"
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=100
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=10
    )

    parser.add_argument(
        "--message",
        default="What products are available?"
    )

    args = parser.parse_args()

    if args.requests < 1 or args.concurrency < 1:
        parser.error("Requests and concurrency must be positive.")

    asyncio.run(run_benchmark(args))
