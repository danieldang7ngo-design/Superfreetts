import asyncio
import concurrent.futures

async def my_coro():
    await asyncio.sleep(0.1)
    return "success"

def test_async():
    coro = my_coro() # Coroutine created in main thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # Try to run it in a different thread using asyncio.run
        # This occurs when anki GUI thread has its own loop (aqt hook)
        try:
            res = executor.submit(asyncio.run, coro).result()
            print("Result:", res)
        except Exception as e:
            print("CRASHED:", e)

# Simulate Anki's running loop in the main thread
async def main():
    test_async()

if __name__ == '__main__':
    asyncio.run(main())
