from PIL import ImageFont
from .initialize import muniMap,euniMap,cuniMap,fontList,CODE2000,Unifont

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

def renderStely(
    texts,
    outlist,
    MainFontPath,
    EmojiFontPath,
    FountColor,
    START_X = 0,
    START_Y = 0,
    LINE_LIMT = 675,
    FOUNT_SIZE = 30,
    LINE_HIGHT= 15,
    SZ = 0
):
    for text in texts:
        if text in ['\u200d', '\u200b', '\r', '\n']:
            continue
        if START_X >= LINE_LIMT:
            START_X = 0
            START_Y += FOUNT_SIZE + LINE_HIGHT

        word = ord(text)
        if word in muniMap.keys():
            f = MainFontPath
            wihdt = get_font_render_size(
                f, FOUNT_SIZE, text)[0]
        elif word in euniMap.keys():
            f = EmojiFontPath
            wihdt = FOUNT_SIZE
        elif word in cuniMap.keys():
            f = CODE2000
            wihdt = get_font_render_size(f, FOUNT_SIZE, text)[0]
        else:
            f = Unifont
            for BackFont in fontList:
                try:
                    if word in BackFont[0].keys():
                        f = BackFont[1]
                        break
                except:
                    pass
            wihdt = get_font_render_size(
                f, FOUNT_SIZE, text)[0]
        outlist.append({"t": text, "d": (START_X, START_Y), "c": FountColor, "f": f})
        START_X += wihdt + SZ