# -*- encoding: utf-8 -*-
import aiohttp
from io import BytesIO
from PIL import Image

async def fetch(session, url):
    """实现GET请求"""
    async with session.get(url) as response:
        return await response.read()

async def getPage(url):
    """下载图片"""
    async with aiohttp.ClientSession() as session:
        data = await fetch(session, url)
        pic = Image.open(BytesIO(data))
        return pic
