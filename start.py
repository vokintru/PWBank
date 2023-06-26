import asyncio
import sys

SCRIPTS = [
    'PWBank.py',
    'HotLine.py'
]


async def waiter(sc, p):
    await p.wait()
    return sc, p


async def main():
    waiters = []

    # Запуск
    for sc in SCRIPTS:
        p = await asyncio.create_subprocess_exec(sys.executable, sc)
        waiters.append(asyncio.create_task(waiter(sc, p)))

    # Ожидание
    while waiters:
        done, waiters = await asyncio.wait(waiters, return_when=asyncio.FIRST_COMPLETED)
        for w in done:
            sc, p = await w


if __name__ == "__main__":
    asyncio.run(main())
