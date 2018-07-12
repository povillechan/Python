#__author:  Administrator
#date:  2017/2/15
import asyncio

import asyncio


@asyncio.coroutine
def func1():
    print('before...func1......')
    yield from asyncio.sleep(5)
    print('end...func1......')


tasks = [func1(), func1()]

# 事件循环
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*tasks))
loop.close()