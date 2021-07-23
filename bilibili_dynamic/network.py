# -*- encoding: utf-8 -*-
import aiohttp
from io import BytesIO
from PIL import Image

class Networks:
    def __init__(self) -> None:
        self.HeadImg = {}
        self.EmojiImg = {}
        self.Pendant = {}
        
    async def fetch(self,session, url):
        """实现GET请求"""
        async with session.get(url) as response:
            return await response.read()

    async def getPage(self, url, type = None, name = None):
        """下载图片"""
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, url)

            pic = Image.open(BytesIO(data))

            if type == 1:
                self.HeadImg[name] = pic
                return pic,1
            elif type == 2:
                self.EmojiImg[name] = pic
                return pic,name
            elif type == 3:
                self.Pendant[name] = pic
                return pic,3
            else:
                return pic
