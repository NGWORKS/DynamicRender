# -*- encoding: utf-8 -*-
from bilibili_dynamic import DynamicRender,textTools,initialize
import asyncio

# 导入数据示例
from dylist import dylist

# `path`参数用于指定缓存文件夹路径 
# 不定义则默认为`工作路径`下的`tmp`文件夹
# 您可以为其指定正确的`绝对路径`或`相对路径`以自定义缓存文件夹
# 当然您也可以指定布尔值`False`，即不缓存。
Render = DynamicRender.DynamicPictureRendering(path="./tmp")

async def test():
    i = 0
    for element in dylist:
        await Render.ReneringManage(element)
        # 您可以在实例化的类中的 ReprenderIMG 获得图片对象
        Render.ReprenderIMG.show()
        i += 1
        if i == 1:
            break
        

# 运行协程函数需要在事件循环中运行
loop = asyncio.get_event_loop()
loop.run_until_complete(test())

