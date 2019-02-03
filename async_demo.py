import asyncio


async def main():
    q = asyncio.Queue()
    tasks = [
        asyncio.create_task(worker(q)),
        asyncio.create_task(publisher(q)),
    ]

    # Wait until all worker tasks are cancelled
    await asyncio.gather(*tasks, return_exceptions=True)


async def publisher(q):
    while True:
        print('enqueued thing')
        q.put_nowait({'a': 'thing'})
        await asyncio.sleep(0.5)


async def worker(queue):
    while True:
        # Get a "work item" out of the queue.
        my_dict = await queue.get()

        print(f'processed {my_dict}')

        # Notify the queue that the "work item" has been processed.
        queue.task_done()


if __name__ == "__main__":
    asyncio.run(main())
