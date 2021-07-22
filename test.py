# -*- encoding: utf-8 -*-
from bilibili_dynamic import DynamicRender
import asyncio

# 导入数据示例
from dylist import dylist


Render = DynamicRender.DynamicPictureRendering(path="./tmp")
async def test():
    for element in dylist:
        await Render.ReneringManage(element)
        # 您可以在实例化的类中的 ReprenderIMG 获得图片对象
        Render.ReprenderIMG.show()
        break

# 运行协程函数需要在事件循环中运行
loop = asyncio.get_event_loop()
loop.run_until_complete(test())

