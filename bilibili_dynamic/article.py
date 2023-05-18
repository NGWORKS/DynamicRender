"""
动态富文本
~~~~~~~~~

这个文件主要进行动态的富文本进行梳理、渲染

copyright: (c) 2021 by NGWORKS.

"""

import re
import time
from typing import Dict, List, Type, Union
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont

from .format import Display, Dynamic, division
from .textTools import (CODE2000, KeyWordsCut, NotoColorEmoji, NotoSansCJK,
                        Unifont, cuniMap, euniMap, get_font_render_size,
                        muniMap)
from .ThreadCli import ThreadCli
from .tmppath import bsepth


def content(card: Dynamic) -> Union[str, None]:
    Text = None
    if card.item:
        if card.item.description:
            Text = card.item.description
        elif card.item.content:
            Text = card.item.content

    elif card.dynamic != "" and card.dynamic:
        Text = card.dynamic
    elif card.vest:
        Text = card.vest.content
    return Text


def at_control(card: Dynamic) -> division :
    at_control, ctrls = (None, None)
    division = []
    if card.item != None:
        if card.item.at_control and card.item.at_control != "":
            at_control = card.item.at_control

        if card.item.ctrl and card.item.ctrl != []:
            ctrls = card.item.ctrl

    for controls in [at_control, ctrls]:
        if controls:
            for control in controls:
                start = control['location']
                length = control['length']
                type = control['type']
                if type != 1:
                    length = int(control['data'])

                data = {"control": type}

                msg = {"start": start, "end": start + length,
                       "len": length, "type": 2, "data": data}
                division.append(msg)
    return division


def emojis_topics(display: Display) ->List:
    topics, emojis = (None, None)

    if display.topic_info:
        topics = display.topic_info.topic_details

    if display.emoji_info:
        emojis = display.emoji_info.emoji_details

    return emojis, topics


def emojis_topics_division(emojis: List, topics: List, Text: str) -> division:
    print(type(emojis))
    division = []
    if emojis:
        for emoji in emojis:
            emojiName = emoji.emoji_name
            wlen = len(emojiName)
            worldstarList = KeyWordsCut(emojiName, Text)
            for w in worldstarList:
                msg = {"start": w, "end": w+wlen, "len": wlen,
                       "type": 0, "data": {"url": emoji.url, "id": emoji.id}}
                division.append(msg)
    if topics:
        for topic in topics:
            topicTag = f'#{topic.topic_name}#'
            taglen = len(topicTag)
            worldstarList = KeyWordsCut(topicTag, Text)
            for w in worldstarList:
                msg = {"start": w, "end": w+taglen,
                       "len": taglen, "type": 1, "data": None}
                division.append(msg)
    return division


def url_division(Text: str) -> division:
    division = []
    reg = r'https?:[0-9a-zA-Z.?#&=_@(-/\d]+'
    url = re.findall(reg, Text)
    if url := list(set(url)):
        reg = r'(.*).bilibili.com'
        for i in url:
            n = urlparse(i).netloc
            if re.match(reg, n) or n == 'b23.tv':
                urllen = len(i)
                worldstarList = KeyWordsCut(i, Text)
                for w in worldstarList:
                    msg = {"start": w, "end": w+urllen, "len": urllen,
                           "type": 2, "data": {"control": 5}}
                    division.append(msg)
    return division


def RendingList(NGSS: List, Text: str) -> List:
    count = 0
    RenderList = []
    pyl = 0
    while count != len(NGSS):
        type = NGSS[count]['type']
        start = NGSS[count]['start']
        if count == 0 and NGSS[count]['start'] != 0:
            data = {'type': -1, 'text': Text[:NGSS[count]['start']]}
            RenderList.append(data)

        if type == 2 and NGSS[count]['data']['control'] != 1:
            control = NGSS[count]['data']['control']
            type = NGSS[count]['type']
            start = NGSS[count]['start']
            end = NGSS[count]['end']
            data = NGSS[count]['data']
            if control == 2:
                img = f"{bsepth}element/box.png"
                text = Text[start+1:end]
            elif control == 3:
                img = f"{bsepth}element/tick.png"
                text = Text[start+1:end]
            elif control == 4:
                img = f"{bsepth}element/tb.png"
                text = Text[start+1:end]
            elif control == 5:
                img = f"{bsepth}element/link.png"
                text = '网页链接'

            dataico = {'type': 3, 'text': "", "data": img}
            data = {'type': type, 'text': text, "data": data}
            RenderList.append(dataico)
        else:
            data = {'type': type, 'text': Text[NGSS[count]['start'] -
                                               pyl:NGSS[count]['end']-pyl], "data": NGSS[count]['data']}
        RenderList.append(data)

        if count != len(NGSS)-1 and NGSS[count]['end'] != NGSS[count+1]['start']:
            end = NGSS[count+1]['start']
            data = {'type': -1, 'text': Text[NGSS[count]['end']-pyl:end-pyl]}
            RenderList.append(data)

        if count == len(NGSS)-1 and NGSS[count]['end'] != len(Text):
            data = {'type': -1, 'text': Text[NGSS[count]['end']:]}
            RenderList.append(data)
        count += 1
    if len(NGSS) == 0:
        RenderList = [{'type': -1, 'text': Text}]
    for element in RenderList:
        type = element['type']
        text = element['text']
        if type == -1 and len(text.split('\n')) > 1:
            element['text'] = text.split('\n')
    newlist = []
    for el in RenderList:
        type = el['type']
        text = el['text']
        if isinstance(text, list):
            for ct, lt in enumerate(text):
                data = {'type': type, 'text': lt, 'enter': ct != 0}
                newlist.append(data)
        else:
            el['enter'] = False
            newlist.append(el)

    return newlist


def tap(RenderList,
        FountColor='#000000',
        HightLightFountColor="#168bce",
        MainFontPath=NotoSansCJK,
        EmojiFontPath=NotoColorEmoji
        ):
    # RenderList 最终样式规定器 计算宽度，分割，细化最初的NGSS
    # 第一个起点的起点 x,y 字符间距
    START_X, START_Y, SZ = (0, 0, 0)
    # 字符大小  行距  一行最长限制
    FOUNT_SIZE, LINE_HIGHT, LINE_LIMT = (30, 15, 675)
    rl, pl, tl = ([], [], [])
    for element in RenderList:
        type = element['type']
        texts = element['text']
        if type == 0:
            if START_X >= LINE_LIMT:
                START_X = 0
                START_Y += FOUNT_SIZE + LINE_HIGHT + 10
            pl.append({"id": element['data']['id'], "d": (
                START_X, START_Y), "u": element['data']['url']})
            START_X += FOUNT_SIZE + SZ + 10
        elif type == 3:
            tl.append(
                {"id": -1, "d": (START_X, START_Y), "u": element['data']})
            START_X += FOUNT_SIZE + SZ + 8
        else:
            for text in texts:
                if text in ['\u200d', '\u200b', '\r', '\n']:
                    # 这里杀掉一些常见的奇怪的东西
                    continue

                # 判断目前写的长度有没有接近最大极限 
                # 也判断这一部分要不要另起一行 之前有判断 \n 的
                if START_X >= LINE_LIMT or element['enter']:
                    # x距离置零
                    START_X = 0
                    # 另起一行 y
                    START_Y += FOUNT_SIZE + LINE_HIGHT
                if element['enter']:
                    # 避免反复换行 拨回去
                    element['enter'] = False

                c = FountColor if type == -1 else HightLightFountColor
                if ord(text) in muniMap.keys():
                    f = MainFontPath
                    # 主要性能损失（wtm这里一个字一个字跑，很讨厌）
                    wihdt = get_font_render_size(f, FOUNT_SIZE, text)
                elif ord(text) in euniMap.keys():
                    f = EmojiFontPath
                    wihdt = FOUNT_SIZE
                elif ord(text) in cuniMap.keys():
                    f = CODE2000
                    wihdt = get_font_render_size(f, FOUNT_SIZE, text)[0]
                else:
                    f = Unifont
                    # 这里应该使用 计算机字库去寻找合适字体
                    wihdt = get_font_render_size(f, FOUNT_SIZE, text)[0]

                rl.append({"t": text, "d": (START_X, START_Y), "c": c, "f": f})

                # 下一个字的起始位置
                START_X += wihdt + SZ

    y = START_Y+FOUNT_SIZE+LINE_HIGHT
    return rl, pl, tl, y


def tr(card, display,
        MainFontPath=NotoSansCJK,
        EmojiFontPath=NotoColorEmoji):
    go = time.time()
    Text = ThreadCli(content, (card,), "Text")
    emo = ThreadCli(emojis_topics, (display,), "emoji_topic")
    frist_tasks = [Text, emo]
    for task in frist_tasks:
        task.start()
    for task in frist_tasks:
        task.join()
    Text = frist_tasks[0].getResult()
    if Text is None:
        print("没有文字")
        return None
    emojis, topics = frist_tasks[1].getResult()
    at = ThreadCli(at_control, (card,), "division_at")
    emoji_topic = ThreadCli(emojis_topics_division,
                            (emojis, topics, Text), "division_emoji_topic")
    url = ThreadCli(url_division, (Text,), "division_url")
    tasks = [at, emoji_topic, url]
    for task in tasks:
        task.start()
    for task in tasks:
        task.join()
    division = tasks[0].getResult() + tasks[1].getResult() + \
        tasks[2].getResult()
    indexdict = {element['start']: element for element in division}
    items = sorted(indexdict.items())
    NGSS = [value for key, value in items]
    RenderList = RendingList(NGSS, Text)
    print(Text)
    rl, pl, tl, y = tap(RenderList)
    FOUNT_SIZE = 30
    Render = Image.new("RGB", (700, y), "#ffffff")
    img_draw = ImageDraw.Draw(Render)
    # 正文字体
    MainFont = ImageFont.truetype(MainFontPath, FOUNT_SIZE)
    EmojiFont = ImageFont.truetype(EmojiFontPath, 109)

    for el in rl:
        if el['f'] == EmojiFontPath:
            emojiRender = Image.new("RGBA", (130, 130), "#ffffff00")
            emg_draw = ImageDraw.Draw(emojiRender)
            emg_draw.text((0, 0), el['t'],font=EmojiFont, embedded_color=True)
            emojiRender = emojiRender.resize((30, 30), Image.ANTIALIAS)
            Render.paste(emojiRender, (el['d'][0], el['d'][1]+5),mask=emojiRender)
        elif el['f'] == MainFont:
            img_draw.text(el['d'], el['t'], font=MainFont, fill=el['c'])
        else:
            try:
                oFont = ImageFont.truetype(el['f'], FOUNT_SIZE)
                img_draw.text(el['d'], el['t'],
                                font=oFont, fill=el['c'])
            except:
                print(f"字库中不存在字符{el['t']}，请检查字库是否完整")
                oFont = ImageFont.truetype(CODE2000, FOUNT_SIZE)
                img_draw.text(el['d'], "⎕", font=oFont, fill=el['c'])
    print(f"结束算字，用时{time.time() -go}")
    return Render
