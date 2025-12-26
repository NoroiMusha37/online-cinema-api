import asyncio


def run_async_task(coro):
    try:
        asyncio.run(coro)
    except Exception as e:
        print(f"Task failed: {e}")
