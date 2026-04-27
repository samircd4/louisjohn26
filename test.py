import asyncio
import aiohttp
import time
from collections import deque
from rich import print

RATE_PER_SECOND = 17   # ~1000/min
TOTAL_REQUESTS = 1000
URL = "http://127.0.0.1:8080/extract-zara?product_url=https%3A%2F%2Fwww.zara.com%2Fuk%2Fen%2Fz-05-high-waist-mom-fit-jeans-p04083022.html%3Fv1%3D496001520"


class RateLimiter:
    def __init__(self, rate):
        self.rate = rate
        self.timestamps = deque()

    async def wait(self):
        while len(self.timestamps) >= self.rate:
            now = time.monotonic()
            if now - self.timestamps[0] > 1:
                self.timestamps.popleft()
            else:
                await asyncio.sleep(0.01)
        self.timestamps.append(time.monotonic())


async def fetch(session, limiter, attempt):
    await limiter.wait()
    try:
        async with session.get(URL, timeout=10) as response:
            data = await response.json()
            print(f"Attempt {attempt}: Status {response.status}")
            print(data)
            return {
                "success": response.status == 200,
                "status": response.status
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def main():
    limiter = RateLimiter(RATE_PER_SECOND)
    connector = aiohttp.TCPConnector(limit=100)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            fetch(session, limiter, i + 1)
            for i in range(TOTAL_REQUESTS)
        ]
        results = await asyncio.gather(*tasks)

    return results


if __name__ == "__main__":
    start = time.time()
    results = asyncio.run(main())
    end = time.time()

    # ✅ SUMMARY
    success_count = sum(1 for r in results if r.get("success"))
    fail_count = len(results) - success_count

    print("\n=== FINAL SUMMARY ===")
    print(f"Total Requests : {len(results)}")
    print(f"Successful     : {success_count}")
    print(f"Failed         : {fail_count}")
    print(f"Success Rate   : {(success_count / len(results)) * 100:.2f}%")

    print(f"\nCompleted in {end - start:.2f} seconds")