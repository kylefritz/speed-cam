import asyncio


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
    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    loop.run_until_complete(asyncio.gather(
        publisher(q),
        worker(q),
    ))
    loop.close()
