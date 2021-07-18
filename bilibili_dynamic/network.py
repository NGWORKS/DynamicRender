# -*- encoding: utf-8 -*-
import aiohttp
from io import BytesIO
from PIL import Image

class HttpRequest:
    async def fetch(self, session, url, jsont=True):
        """实现GET请求"""
        async with session.get(url) as response:
            if jsont:
                data = await response.json()
                self.DynamicData = data
                return data
            else:
                return await response.read()

    async def getPage(self, url, count=0, tp=0, sz=0):
        """下载图片"""
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, url, jsont=False)
            pic = Image.open(BytesIO(data))
            if tp == 0:
                return pic
            elif tp == 1:
                self.HeadImg.append({"data": pic, "path": count, "type": sz})
            else:
                self.EmojiImg.append({"data": pic, "path": count, "id": sz})
            return pic