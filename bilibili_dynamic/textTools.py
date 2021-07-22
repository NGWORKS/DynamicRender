# -*- encoding: utf-8 -*-

from PIL import ImageFont
import  qrcode
from .initialize import NotoSansCJK

def get_font_render_size(FOUNT, fontsize, text):
    """
    获取字符精准宽度
    :param data: 字库 字体大小 字符对象
    :returns: 字符的 width, height
    """
    try:
        font = ImageFont.truetype(FOUNT, fontsize, 0)
        width, height = font.getsize(text)
        return (width, height)
    except:
        print(f'字符{text}宽度计算失败，已使用默认值')
        return (fontsize, fontsize)

def KeyWordsCut(KeyWord, paragraph):
    """
    字符串位置检测
    :param data: 关键词 文章
    :returns: 这个关键词在文章从出现位置的起点的list

    """
    keywordslen = len(KeyWord)
    wordsList = []
    i = 0
    while True:
        l = paragraph.find(KeyWord)
        if l == -1:
            break
        paragraph = paragraph[l+keywordslen:]
        if len(wordsList) != 0:
            b = wordsList[i]
            l = b + l + keywordslen
            i += 1
        wordsList.append(l)
    wordsList = list(set(wordsList))
    wordsList.sort()
    return wordsList

def AoutLine(limt, text, size, color='#000000', fount=NotoSansCJK, x=15, y=0):
        """非富文本样式计算"""
        START_X ,START_Y = (x,y)
        FOUNT_SIZE = size
        LINE_HIGHT = 15
        LINE_LIMT = limt
        pl = []
        for i in text:
            if START_X >= LINE_LIMT:
                START_X = x
                START_Y += FOUNT_SIZE + LINE_HIGHT
            wihdt = get_font_render_size(fount, FOUNT_SIZE, i)[0]
            pl.append({"t": i, "d": (START_X, START_Y), "c": color, "f": fount})
            START_X += wihdt
        return pl

async def makeQRcode(data):
    """制作二维码"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=4
    )
    # 传入数据
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image()