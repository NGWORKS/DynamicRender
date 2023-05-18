# -*- encoding: utf-8 -*-
"""
基于PIL的哔哩哔哩动态渲染器
~~~~~~~~~~~~~~~~~~~~~~~~~

这个模块可以用来渲染绝大多数的B站动态，目前对于其他样式还在开发中。

特色：可以实现b站富文本的渲染，图片自适应，挂件，大会员，认证号，投稿，专栏的渲染

    * 绝大数下载使用Aiohttp异步下载（我异步写的很烂不排除有问题）
    * 一堆shit（这是什么特色啊喂）

基本用法:
    * 传入 API返回数据中的`data`下的`card` 或与结构之一样的数据。

   >>> from BiliBili_dynamic import DynamicRender
   >>> import asyncio
   >>> # data 是上述数据，tmp_path是缓存路径，默认工作路径下的 tmp目录
   >>> Render = DynamicRender.DynamicPictureRendering(data,tmp_path =r"tmp")
   >>> loop = asyncio.get_event_loop()
   >>> loop.run_until_complete(Render.ReneringManage())
   >>> Render.ReprenderIMG.show()

BUG emoji不被字符计数，导致偏差。（可能占用字符数目不一样）

copyright: (c) 2021 by NGWORKS.

"""
import asyncio
import os
import re
import time
from asyncio.tasks import Task
from io import BytesIO
from urllib.parse import urlparse

import aiohttp
from PIL import Image, ImageDraw, ImageFont
from requests.api import head

from .format import Display, Dynamic, DynamicCard
from .initialize import (CODE2000, NotoColorEmoji, NotoSansCJK, Unifont,
                         bsepth, cuniMap, euniMap, fontList, link, muniMap,
                         workpath)
from .textRender import renderStely
from .textTools import AoutLine, KeyWordsCut, get_font_render_size, makeQRcode

faceMark = Image.open(bsepth + 'element/hm.png')
userauth = Image.open(bsepth + 'element/user-auth.png')


def set_tmp(tmp=None):
    if tmp == False:
        return False

    if tmp is None:
        path = './tmp'
    else:
        path = tmp

    if os.path.isabs(path):
        tmp = path
    else:
        os.chdir(workpath)
        tmp = os.path.abspath(path)
    tmp = tmp + '/'
    tmp_path = tmp
    pathlist = [tmp_path + 'face/', tmp_path + 'pendant/', tmp_path + 'emoji/']
    for p in pathlist:
        if not os.path.isdir(p):
            os.makedirs(p)
    return tmp_path


class DynamicPictureRendering:
    """动态渲染器
       --------
    """

    def __init__(self, path=None):
        self.HeadImg = []
        self.EmojiImg = []
        self.DynamicData = None
        self.DynamicId = None
        self.tmp_path = set_tmp(path)

    async def headRendering(self, desc):
        """
        头部信息渲染器：
        -------------

        :param data: 动态的数据，为一个`实例化后的类`。
        :returns:  输出为一个150*300的`图片`。

        这个函数通过数据进行头部`头像、名称、大会员、认证、时间戳、浏览量`进行渲染。

        """
        cpx = 150
        fpx = int(cpx/2)
        ppx = int((fpx/48)*82)
        ico = int((fpx/48)*16)
        user_profile = desc.user_profile
        userinfo = user_profile.info
        vip = user_profile.vip
        official = user_profile.card.official_verify
        pendant = user_profile.pendant

        fm = urlparse(userinfo.face).path[10:]
        pid = pendant.pid
        facePath = f'{self.tmp_path}face/{fm}'
        pendantPath = f'{self.tmp_path}pendant/{pid}.png'
        """这里对头像与挂件进行了判断，生成了tasks的任务列表，对头像、挂件进行下载"""

        tasks = []

        if fm in link.HeadImg:
            # 查看缓存中是否存在图片
            face = link.HeadImg[fm]
        elif self.tmp_path != False and os.path.exists(facePath):
            # 查看硬盘中是否存在图片
            face = Image.open(facePath).resize((fpx, fpx), Image.ANTIALIAS)
            link.HeadImg[fm] = face
        else:
            tasks.append(link.getPage(userinfo.face+'@150w.webp', 1, fm))

        if pid == 0:
            # pendant.pid = 0 时 用户没有装备头像框
            pendant = None
        elif pid in link.Pendant:
            # 查看缓存中是否存在图片
            pendant = link.Pendant[pid]
        elif self.tmp_path != False and os.path.exists(pendantPath):
            # 查看硬盘中是否存在图片
            pendant = Image.open(pendantPath)
            link.Pendant[pid] = pendant
        else:
            tasks.append(link.getPage(
                pendant.image+'@180w.webp', 3, pendant.pid))

        if len(tasks) != 0:
            # 如果有下载任务
            imgs = await asyncio.gather(*tasks)
            for img in imgs:
                pic, type = img
                if type == 1:
                    savePath = facePath
                    face = pic
                else:
                    savePath = pendantPath
                    pendant = pic
                if self.tmp_path != False:
                    pic.save(savePath)

        # 新建头像渲染画布
        HeadRender = Image.new("RGB", (cpx, cpx), "#FFFFFF")

        facem = faceMark.resize((fpx, fpx), Image.ANTIALIAS)
        HeadRender.paste(face.resize((fpx, fpx), Image.ANTIALIAS),
                         (int((cpx-fpx)/2), int((cpx-fpx)/2)), mask=facem)

        # 存在没有头像框的情况
        if pendant:
            pendant = pendant.resize(
                (ppx, ppx), Image.ANTIALIAS).convert('RGBA')
            HeadRender.paste(pendant, (int((cpx-ppx)/2),
                             int((cpx-ppx)/2)), mask=pendant)

        if official.type != -1 or vip.vipType != 0:
            # 是 大会员 或者 认证号
            if vip.vipType != 0:
                box = (69, 16, 94, 41)
            # 认证号的优先级高，会覆盖大会员
            if official.type == 0:
                box = (35, 16, 60, 41)
            elif official.type == 1:
                box = (1, 16, 26, 41)
            # 根据上面的BOX剪裁
            officialimg = userauth.crop(box).resize(
                (ico, ico), Image.ANTIALIAS).convert('RGBA')
            # 粘贴
            HeadRender.paste(officialimg, (fpx+int(ico/2),
                             fpx+int(ico/2)), mask=officialimg)
        # 名字颜色
        if vip.nickname_color == "":
            nickname_color = (34, 34, 34)
        else:
            nickname_color = (251, 114, 153)

        # 创建主画布准备写字
        main = Image.new("RGB", (cpx*3, cpx), "#FFFFFF")
        main.paste(HeadRender)
        # 写昵称
        ttf_path = NotoSansCJK
        nicknameFont = ImageFont.truetype(ttf_path, int(cpx/6))
        img_draw = ImageDraw.Draw(main)
        img_draw.text((cpx-8, int(cpx/2-30)), userinfo.uname,
                      font=nicknameFont, fill=nickname_color)
        # 写时间
        timeFont = ImageFont.truetype(ttf_path, int(cpx/8))
        timeArray = time.localtime(desc.timestamp)
        otherStyleTime = time.strftime("%m-%d %H:%M", timeArray)

        timeText = f'{otherStyleTime}'

        img_draw.text((cpx-8, int(cpx/2+10)), timeText,
                      font=timeFont, fill=(153, 162, 170))
        return main

    async def NGSSTrcker(
        self,
        card,
        display,
        Background='#ffffff',
        FountColor='#000000',
        HightLightFountColor="#168bce",
        MainFontPath=NotoSansCJK,
        EmojiFontPath=NotoColorEmoji
    ):
        """
        文字渲染器
        ---------
        根据数据中的信息生成`样式描述信息`(NGSS)与渲染动态文字照片：

        :param data: 动态的数据。
        :returns:  输出为一个渲染好的`PIL图片`。

        这个函数可以自动的识别、分割出来文字中的艾特、投票、抽奖、标签功能、同时可以渲染表情包，生成指导渲染的信息：

            `NGSS`识别了特殊文本的样式，和在字符串中的位置，是后续文本处理的指导性数据。

            `RenderList`包含了以特殊文本为分隔符的所有文本信息。

            `rl` 包含了以`字符`为单位的文本渲染信息。

            `pl` 包含了以`bilibili表情包`为单位的渲染信息。

            `tl` 包含了以`特殊功能图片`的渲染信息，如动态抽奖前的小礼物，投票的柱状图，网页链接的链接图标。


        """
        try:
            # 找文字块
            if card.item != None:
                if card.item.description != None:
                    Text = card.item.description
                elif card.item.content != None:
                    Text = card.item.content

            elif card.dynamic != None and card.dynamic != "":
                Text = card.dynamic
            elif card.vest != None:
                Text = card.vest.content
            else:
                return None

            # 找艾特 抽奖 投票 干饭
            at_control = None
            ctrls = None
            if card.item != None:
                if card.item.at_control != None and card.item.at_control != "":
                    at_control = card.item.at_control

                if card.item.ctrl != None and card.item.ctrl != []:
                    ctrls = card.item.ctrl

            # 表情包 话题标签
            if display.topic_info != None:
                topics = display.topic_info.topic_details
            else:
                topics = None

            if display.emoji_info != None:
                emojis = display.emoji_info.emoji_details
            else:
                emojis = None
            del display, card

            # 分割方案生成器
            division = []
            if at_control != None:
                for control in at_control:
                    """艾特 分割方案器"""

                    if control['type'] != 1:
                        # 如果不是普通的艾特信息 艾特 1 互动抽奖 2 投票 3
                        control['length'] = int(control['data'])
                    msg = {"start": control['location'], "end": control['location']+control['length'],
                           "len": control['length'], "type": 2, "data": {"control": control['type']}}
                    division.append(msg)

            if ctrls != None:
                for ctrl in ctrls:
                    """淘宝 艾特 抽奖 投票分割方案器"""

                    if ctrl['type'] != 1:
                        # 如果不是普通的艾特信息 艾特 1 互动抽奖 2 投票 3
                        ctrl['length'] = int(ctrl['data'])
                    msg = {"start": ctrl['location'], "end": ctrl['location']+ctrl['length'],
                           "len": ctrl['length'], "type": 2, "data": {"control": ctrl['type']}}
                    division.append(msg)

            if emojis != None:
                for emoji in emojis:
                    """表情包分割方案器"""
                    emojiName = emoji.emoji_name
                    wlen = len(emojiName)
                    worldstarList = KeyWordsCut(emojiName, Text)
                    for w in worldstarList:
                        msg = {"start": w, "end": w+wlen, "len": wlen,
                               "type": 0, "data": {"url": emoji.url, "id": emoji.id}}
                        division.append(msg)

            if topics != None:
                for topic in topics:
                    """话题 活动 分割方案器"""
                    topicTag = f'#{topic.topic_name}#'
                    taglen = len(topicTag)
                    worldstarList = KeyWordsCut(topicTag, Text)
                    for w in worldstarList:
                        msg = {"start": w, "end": w+taglen,
                               "len": taglen, "type": 1, "data": None}
                        division.append(msg)

            # 识别超链接

            reg = r'https?:[0-9a-zA-Z.?#&=_@(-/\d]+'
            url = re.findall(reg, Text)
            url = list(set(url))
            if len(url) != 0:
                for i in url:
                    n = urlparse(i).netloc
                    reg = r'(.*).bilibili.com'
                    if re.match(reg, n) or n == 'b23.tv':
                        urllen = len(i)
                        worldstarList = KeyWordsCut(i, Text)
                        for w in worldstarList:
                            msg = {"start": w, "end": w+urllen, "len": urllen,
                                   "type": 2, "data": {"control": 5}}
                            division.append(msg)
            del reg, url

            # 排列分割方案，根据分割起点大小排列
            indexdict = {}
            for element in division:
                indexdict[element['start']] = element
            items = list(indexdict.items())
            items.sort()
            NGSS = [value for key, value in items]

            # 分割方案生成完毕，这里根据NGSS对字符串分割 开始生成RenderList
            count = 0
            RenderList = []
            pyl = 0
            while count != len(NGSS):
                if count == 0 and NGSS[count]['start'] != 0:
                    data = {'type': -1, 'text': Text[0:NGSS[count]['start']]}
                    RenderList.append(data)

                if NGSS[count]['type'] == 2 and NGSS[count]['data']['control'] == 2:
                    data = {
                        'type': 3, 'text': Text[:NGSS[count]['start']], "data": bsepth + 'element/box.png'}
                    RenderList.append(data)
<<<<<<< HEAD
                    data = {'type': NGSS[count]['type'], 'text': Text[NGSS[count]['start']+1:NGSS[count]['end']], "data": NGSS[count]['data']}
=======
                    data = {'type': NGSS[count]['type'], 'text': Text[NGSS[count]
                                                                      ['start']+1:NGSS[count]['end']], "data": NGSS[count]['data']}
>>>>>>> 61b4b3f6be7c2f406c5e95ca20e4c4949f474954
                elif NGSS[count]['type'] == 2 and NGSS[count]['data']['control'] == 3:
                    data = {
                        'type': 3, 'text': Text[:NGSS[count]['start']], "data": bsepth + 'element/tick.png'}
                    RenderList.append(data)
<<<<<<< HEAD
                    data = {'type': NGSS[count]['type'], 'text': Text[NGSS[count]['start']+1:NGSS[count]['end']], "data": NGSS[count]['data']}
=======
                    data = {'type': NGSS[count]['type'], 'text': Text[NGSS[count]
                                                                      ['start']+1:NGSS[count]['end']], "data": NGSS[count]['data']}
>>>>>>> 61b4b3f6be7c2f406c5e95ca20e4c4949f474954
                elif NGSS[count]['type'] == 2 and NGSS[count]['data']['control'] == 4:
                    data = {
                        'type': 3, 'text': Text[:NGSS[count]['start']], "data": bsepth + 'element/tb.png'}
                    RenderList.append(data)
<<<<<<< HEAD
                    data = {'type': NGSS[count]['type'], 'text': Text[NGSS[count]['start']+1:NGSS[count]['end']], "data": NGSS[count]['data']}
=======
                    data = {'type': NGSS[count]['type'], 'text': Text[NGSS[count]
                                                                      ['start']+1:NGSS[count]['end']], "data": NGSS[count]['data']}
>>>>>>> 61b4b3f6be7c2f406c5e95ca20e4c4949f474954
                elif NGSS[count]['type'] == 2 and NGSS[count]['data']['control'] == 5:
                    data = {'type': 3, 'text': '',"data": bsepth + 'element/link.png'}
                    RenderList.append(data)
                    data = {'type': NGSS[count]['type'],'text': '网页链接', "data": NGSS[count]['data']}
                else:
<<<<<<< HEAD
                    data = {'type': NGSS[count]['type'], 'text': Text[NGSS[count]['start']-pyl:NGSS[count]['end']-pyl], "data": NGSS[count]['data']}
=======
                    data = {'type': NGSS[count]['type'], 'text': Text[NGSS[count]
                                                                      ['start']-pyl:NGSS[count]['end']-pyl], "data": NGSS[count]['data']}
>>>>>>> 61b4b3f6be7c2f406c5e95ca20e4c4949f474954

                RenderList.append(data)

                if count != len(NGSS)-1 and NGSS[count]['end'] != NGSS[count+1]['start']:
                    end = NGSS[count+1]['start']
                    data = {'type': -1,'text': Text[NGSS[count]['end']-pyl:end-pyl]}
                    RenderList.append(data)

                if count == len(NGSS)-1 and NGSS[count]['end'] != len(Text):
                    data = {'type': -1,
                            'text': Text[NGSS[count]['end']:len(Text)]}
                    RenderList.append(data)
                count += 1

            if NGSS == []:
                RenderList = [{'type': -1, 'text': Text}]
            del NGSS, Text
            # 实现换行符的识别与分割
            for element in RenderList:
                type = element['type']
                text = element['text']
                if type == -1:
                    if len(text.split('\n')) > 1:
                        element['text'] = text.split('\n')
            del type, text, element

            # RenderList 最终样式规定器 计算宽度，分割，细化最初的NGSS
            # 第一个起点的起点 x,y 字符间距
            START_X, START_Y, SZ = (0, 0, 0)
            # 字符大小  行距  一行最长限制
            FOUNT_SIZE, LINE_HIGHT, LINE_LIMT = (30, 15, 675)
<<<<<<< HEAD
            rl ,pl ,tl = ([], [] ,[])
=======
            rl, pl, tl = ([], [], [])
>>>>>>> 61b4b3f6be7c2f406c5e95ca20e4c4949f474954
            for element in RenderList:
                type = element['type']
                text = element['text']
                if type == 0:
                    if START_X >= LINE_LIMT:
                        START_X = 0
                        START_Y += FOUNT_SIZE + LINE_HIGHT + 10
                    pl.append({"id": element['data']['id'], "d": (START_X, START_Y), "u": element['data']['url']})
                    START_X += FOUNT_SIZE + SZ + 10
                elif type == 3:
                    tl.append(
                        {"id": -1, "d": (START_X, START_Y), "u": element['data']})
                    START_X += FOUNT_SIZE + SZ + 8
                else:
                    if isinstance(text, list):
                        pp = 1
                        for t in text:
                            for s in t:
                                if s in ['\u200d', '\u200b', '\r', '\n']:
                                    continue
                                if START_X >= LINE_LIMT:
                                    START_X = 0
                                    START_Y += FOUNT_SIZE + LINE_HIGHT

                                if ord(s) in muniMap.keys():
                                    f = MainFontPath
                                    wihdt = get_font_render_size(f, FOUNT_SIZE, s)[0]
                                elif ord(s) in euniMap.keys():
                                    f = EmojiFontPath
                                    wihdt = FOUNT_SIZE
                                elif ord(s) in cuniMap.keys():
                                    f = CODE2000
                                    wihdt = get_font_render_size(f, FOUNT_SIZE, s)[0]
                                else:
                                    f = Unifont
                                    for ppp in fontList:
                                        try:
                                            if ord(s) in ppp[0].keys():
                                                f = ppp[1]
                                                break
                                        except:
                                            pass
                                    wihdt = get_font_render_size(f, FOUNT_SIZE, s)[0]
                                rl.append({"t": s, "d": (START_X, START_Y), "c": FountColor, "f": f})
                                START_X += wihdt + SZ

                            if pp != len(text):
                                START_X = 0
                                START_Y += FOUNT_SIZE + LINE_HIGHT
                            pp += 1
                    else:
                        for i in text:
                            if i in ['\u200d', '\u200b', '\r', '\n']:
                                continue
                            if START_X >= LINE_LIMT:
                                START_X = 0
                                START_Y += FOUNT_SIZE + LINE_HIGHT
                            if type == -1:
                                c = FountColor
                            else:
                                c = HightLightFountColor

                            if ord(i) in muniMap.keys():
                                f = MainFontPath
                                wihdt = get_font_render_size(
                                    f, FOUNT_SIZE, i)[0]
                            elif ord(i) in euniMap.keys():
                                f = EmojiFontPath
                                wihdt = FOUNT_SIZE
                            elif ord(i) in cuniMap.keys():
                                f = CODE2000
                                wihdt = get_font_render_size(
                                    f, FOUNT_SIZE, i)[0]
                            else:
                                f = Unifont
                                for ppp in fontList:
                                    try:
                                        if ord(i) in ppp[0].keys():
                                            f = ppp[1]
                                            break
                                    except:
                                        pass

                                wihdt = get_font_render_size(
                                    f, FOUNT_SIZE, i)[0]

                            rl.append(
                                {"t": i, "d": (START_X, START_Y), "c": c, "f": f})
                            START_X += wihdt + SZ

            Render = Image.new("RGB", (700, START_Y+FOUNT_SIZE+LINE_HIGHT), Background)
            img_draw = ImageDraw.Draw(Render)
            # 正文字体
            MainFont = ImageFont.truetype(MainFontPath, FOUNT_SIZE)
            EmojiFont = ImageFont.truetype(EmojiFontPath, 109)
            # 文字emoji处理
            for el in rl:
                if el['f'] == EmojiFontPath:
                    emojiRender = Image.new("RGBA", (130, 130), Background)
                    emg_draw = ImageDraw.Draw(emojiRender)
                    emg_draw.text((0, 0), el['t'],
                                  font=EmojiFont, embedded_color=True)
                    emojiRender = emojiRender.resize((30, 30), Image.ANTIALIAS)
                    Render.paste(
                        emojiRender, (el['d'][0], el['d'][1]+5), emojiRender)
                elif el['f'] == MainFont:
                    img_draw.text(el['d'], el['t'],
                                  font=MainFont, fill=el['c'])
                else:
                    try:
                        oFont = ImageFont.truetype(el['f'], FOUNT_SIZE)
                        img_draw.text(el['d'], el['t'],
                                      font=oFont, fill=el['c'])
                    except:
                        print(f"字库中不存在字符{el['t']}，请检查字库是否完整")
                        oFont = ImageFont.truetype(CODE2000, FOUNT_SIZE)
                        img_draw.text(el['d'], "⎕", font=oFont, fill=el['c'])

            # ISDO 异步下载表情包
            # TODO 复用下载后的对象，下载了之后直接调用，就不要在去磁盘里打开了

            # 图片元素处理
            if len(tl) != 0:
                for el in tl:
                    gimg = Image.open(el['u']).resize(
                        (FOUNT_SIZE+5, FOUNT_SIZE+5), Image.ANTIALIAS).convert('RGBA')
                    Render.paste(gimg, (el['d'][0], el['d'][1]+5), mask=gimg)
                del gimg, tl

            # 原生表情包处理
            if len(pl) != 0:
                # 取表情包图片缓存
                emojiPicDict = {}
                tasks = []
                for emoji in pl:
                    id = emoji['id']

                    imgpath = f'{self.tmp_path}emoji/{id}.png'

                    if id in link.EmojiImg:
                        # 下载缓存中存在图片
                        emojiPicDict[id] = link.EmojiImg[id]
                    elif self.tmp_path != False and os.path.exists(imgpath):
                        # 本地硬盘中存在
                        emojiPicDict[id] = Image.open(imgpath)
                    else:
                        tasks.append(link.getPage(emoji['u'], 2, id))

                if len(tasks) != 0:
                    imgs = await asyncio.gather(*tasks)
                    for img in imgs:
                        pic, id = img
                        if self.tmp_path != False:
                            imgpath = f'{self.tmp_path}emoji/{id}.png'
                            pic.save(imgpath)
                        emojiPicDict[id] = pic

                for emoji in pl:
                    id = emoji['id']
                    emimg = emojiPicDict[id].resize(
                        (FOUNT_SIZE+10, FOUNT_SIZE+10), Image.ANTIALIAS).convert('RGBA')

                    Render.paste(emimg, emoji['d'], mask=emimg)

                del pl, tasks
            return Render
        except Exception as e:
            print(f"{self.DynamicId}渲染错误!,错误是：{e}")
            return None

    async def FunctionBlock(self, type, card, background="#FFFFFF"):
        """
        功能块渲染器
        -----------
        用来渲染功能块，如 视频封面 专栏投稿 相册图片等等

        """
        ttf_path = NotoSansCJK
        nicknameFont = ImageFont.truetype(ttf_path, 25)
        sFont = ImageFont.truetype(ttf_path, 20)
        # TODO 4302 付费课程
        # 投稿视频 直播 电视剧
        if type in [4098, 4099, 4101, 4308, 8, 4098, 512, 4302]:
            # 电视剧-电影-番剧/国漫-纪录片
            if type in [4098, 4099, 512, 4101, 4302]:
                pic = card.cover + '@480w.webp'
                title = card.new_desc
                if not card.new_desc:
                    title = card.title
                if not card.title:
                    title = self.DynamicData.card.origin["apiSeasonInfo"]["title"]
            elif type == 4308:
                pic = self.DynamicData.card.origin['live_play_info']['cover'] + '@480w.webp'
                title = self.DynamicData.card.origin['live_play_info']['title']
            else:
                pic = card.pic + '@480w.webp'
                title = card.title

            pic = await link.getPage(pic)
            picsize = pic.size
            # 根据图片实际大小剪裁为16*9
            box = (0, int((picsize[1]-(picsize[0]/16*9))/2), picsize[0],
                   int(((picsize[1]-(picsize[0]/16*9))/2)+(picsize[0]/16*9)))
            pic = pic.crop(box)
            # 重置大小
            pic = pic.resize((720, 405), Image.ANTIALIAS)
            if type == 8:
                tvlogo = Image.open(bsepth + 'element/tv.png')
                BBox = Image.open(bsepth + 'element/box-b.png')
                jianbian = Image.open(bsepth + 'element/jianbian.png')
                pic.paste(jianbian, (0, 300), mask=jianbian)
                pic.paste(tvlogo, (613, 311), mask=tvlogo)
                pic.paste(BBox, (13, 350), mask=BBox)
                img_draw = ImageDraw.Draw(pic)
                vtime = card.duration
                m, s = divmod(vtime, 60)
                h, m = divmod(m, 60)

                def pat0(number):
                    if number < 10:
                        return f"0{number}"
                    else:
                        return number
                img_draw.text((21, 353), f"{pat0(h)}:{pat0(m)}:{pat0(s)}",
                              font=nicknameFont, fill="#FFFFFF")

            picsize = pic.size
            img = Image.new("RGB", (740, picsize[1]+10 + 30 + 15), background)
            mark = Image.open(bsepth + 'element/fm.png')
            img.paste(pic, (10, 10), mask=mark)
            img_draw = ImageDraw.Draw(img)
            textcount, allwidth = (0, 0)
            for t in title:
                wihdt = get_font_render_size(NotoSansCJK, 25, t)[0]
                textcount += 1
                allwidth += wihdt
                if allwidth > 675:
                    title = title[:textcount] + '...'
                    break
            img_draw.text((10, picsize[1]+20), title,
                          font=nicknameFont, fill="#000000")
            return img
        # 相册
        elif type == 2:
            pictures = card.item.pictures
            piccount = len(pictures)
            # 根据图片数量生成渲染规则
            if piccount == 1:
                lm = 1
                w, h = (518, None)
            elif piccount in [2, 4]:
                # 当 图片数量 等于2 或等于4时
                # 图片是两个一排 宽度平均分
                lm = 2
                w, h = (int((720-10)/lm), int((720-10)/lm))
            else:
                # 否则一律三个一排 宽度平均分
                lm = 3
                w, h = (int((720-20)/lm), int((720-20)/lm))

            tasks = []
            for pic in pictures:
                if lm == 1:
                    cutrule = ""
                elif pic.img_height/pic.img_width >= 3:
                    # 当图片长宽比大于 3 时 图片从头部剪裁
                    cutrule = "_!header"
                else:
                    # 居中剪裁出 1:1 的方形图片
                    cutrule = "_1e_1c"

                if h:
                    url = pic.img_src+f'@{w}w_{h}h{cutrule}.webp'
                else:
                    # 如果h为None
                    url = pic.img_src+f'@{w}w{cutrule}.webp'
                tasks.append(link.getPage(url))

            # 等待结果返回

            img = await asyncio.gather(*tasks)

            if lm == 1:
                pic = img[0]
                w, h = pic.size
                w, h = (720, int(700/(w/h)))
                pic = pic.resize((720, h), Image.ANTIALIAS)
                img = [pic]

            count = 1
            # 起始位置
            x, y = (10, 10)
            # 处理后的图片信息
            fulren = []

            for pic in img:
                if count > lm:
                    # 当 图片的行计数大于上面的规则时，另起一行并且重新计算行计数
                    x = 10
                    y += w + 10
                    count = 1
                # 根据渲染规则重设图片 和得到计算的位置

                fulren.append([pic, (x, y)])
                # 图片之间的间隙
                x += w+10
                count += 1

            # 生成画布 根据上面的信息 贴图片
            img = Image.new("RGB", (740, y+h+10), background)
            for el in fulren:
                img.paste(el[0], el[1])

            return img
        elif type == 64:
            """专栏"""
            image_urls = card.image_urls
            summary = card.summary
            if len(summary) > 52:
                summary = summary[:52] + '...'
            title = card.title
            # ISDO 计算标题文字高度
            titlestly = AoutLine(
                675, title, 30, color='#000000', fount=NotoSansCJK)
            lasttitle = titlestly[len(titlestly)-1]['d'][1] + 30
            tasks = []
            i = 0
            piccount = len(image_urls)
            for pic in image_urls:
                if piccount != 1:
                    tasks.append(link.getPage(pic+'@104w_104h_1e_1c.webp'))
                else:
                    tasks.append(link.getPage(pic+'@520w_120h_1e_1c.webp'))
                i += 1

            res = await asyncio.gather(*tasks)

            fulren = []
            x = 10
            y = lasttitle + 25
            for pic in res:
                if piccount != 1:
                    w = int((700-20)/3)
                    fulren.append(
                        [pic.resize((w, w), Image.ANTIALIAS), (x, y)])
                    x += w+10
                else:
                    h = int(700/(520/120))
                    fulren.append(
                        [pic.resize((700, h), Image.ANTIALIAS), (x, y)])
                    w = h
            lastpic = fulren[len(fulren)-1][1][1] + w
            if summary != '':
                summstly = AoutLine(
                    675, summary, 25, color='#666666', fount=NotoSansCJK, y=lastpic+20)
                lastsumm = summstly[len(summstly)-1]['d'][1] + 30
            else:
                lastsumm = lastpic
            # isdo 计算描述文字高度
            img = Image.new("RGB", (740, lastsumm + 20), background)
            img_draw = ImageDraw.Draw(img)
            for el in titlestly:
                nicknameFont = ImageFont.truetype(ttf_path, 30)
                img_draw.text(el['d'], el['t'],
                              font=nicknameFont, fill="#000000")
            if summary != '':
                for el in summstly:
                    nicknameFont = ImageFont.truetype(ttf_path, 25)
                    img_draw.text(el['d'], el['t'],
                                  font=nicknameFont, fill="#666")
            for pic in fulren:
                img.paste(pic[0], pic[1])
            return img
        elif type == 4200:
            # 条形带图片方形文字描述 直播
            # 图片 @203w_127h_1e_1c.webp
            title = card.title
            url = card.cover + '@203w_127h_1e_1c.webp'
            cover = await link.getPage(url)
            area = card.area_v2_name

            img = Image.new("RGB", (740, 127), background)
            img_draw = ImageDraw.Draw(img)
            img.paste(cover, (20, 0))
            img_draw.text((240, 20), title, font=nicknameFont, fill="#000000")
            img_draw.text((240, 90), area, font=sFont, fill="#666")
            return img

    async def AddCard(self, display):
        """附加卡片渲染器
           -------------
           渲染附加卡片，如 投票 视频预约 游戏

        """
        if display.add_on_card_info:
            ttf_path = NotoSansCJK
            nicknameFont = ImageFont.truetype(ttf_path, 25)
            sFont = ImageFont.truetype(ttf_path, 20)
            type = display.add_on_card_info[0].add_on_card_show_type
            if type == 2:
                data = display.add_on_card_info[0].attach_card
                cover_url = data.cover_url + '@110w_110h_1e_1c.webp'
                cover = await link.getPage(cover_url)
                title = data.title
                desc_first = data.desc_first
                desc_second = data.desc_second

                img = Image.new("RGB", (700, 150), "#f4f5f7")
                img.paste(cover, (30, 20))
                img_draw = ImageDraw.Draw(img)
                img_draw.text((160, 20), title,
                              font=nicknameFont, fill="#000000")
                img_draw.text((160, 60), desc_first, font=sFont, fill="#666")
                img_draw.text((160, 90), desc_second, font=sFont, fill="#666")
                return img
            if type == 6:
                data = display.add_on_card_info
                title = data[0].reserve_attach_card.title
                desc_first = data[0].reserve_attach_card.desc_first.text
                desc_second = data[0].reserve_attach_card.desc_second
                desc = desc_first+'   '+desc_second
                img = Image.new("RGB", (700, 150), "#f4f5f7")
                img_draw = ImageDraw.Draw(img)
                nicknameFont = ImageFont.truetype(NotoSansCJK, 25)
                img_draw.text((40, 35), title,
                              font=nicknameFont, fill="#000000")
                nicknameFont = ImageFont.truetype(NotoSansCJK, 20)
                img_draw.text((40, 90), desc, font=nicknameFont, fill="#999")

                return img
            if type == 3:
                img = Image.new("RGB", (700, 170), "#FFFFFF")
                img_draw = ImageDraw.Draw(img)
                vote_card = display.add_on_card_info[0].vote_card
                nicknameFont = ImageFont.truetype(NotoSansCJK, 25)
                tick_b = Image.open(
                    bsepth + 'element/tick_B.png').resize((140, 140))
                img.paste(tick_b)
                img_draw.text(
                    (180, 30), vote_card['desc'], font=nicknameFont, fill="#000000")
                nicknameFont = ImageFont.truetype(NotoSansCJK, 20)
                img_draw.text(
                    (180, 80), f"{vote_card['join_num']}人参与", font=nicknameFont, fill="#999")
                return img
        else:
            return None

    async def Reprender(self, desc, card, display):
        """
        源动态渲染器
        ---------
        渲染源动态内容，原理与总动态基本一致，差别仅在字体颜色和对于头部信息渲染的省略。
        """
        type = desc.type
        if type == 1:
            # 组装信息
            card = card.origin
            display = display.origin
            if card is None:
                return None
            card = Dynamic(**card)

            if display:
                display = Display(**display)
            else:
                display = {}

            # 给任务清单中添加 文字 功能块 附加卡片
            tasks = [
                self.NGSSTrcker(
                    card, display, Background="#f4f4f4", FountColor="#757575"),
                self.FunctionBlock(desc.orig_type, card, background="#f4f4f4"),
                self.AddCard(display)
            ]

            # 返回结果
            res = await asyncio.gather(*tasks)
            # 这个列表用于储存上述渲染结果的排版定位
            hblist = []
            h = 60
            # 进行预排版，生成排版信息 文字 功能块 附加卡片
            if res[0]:
                hblist.append([res[0], (20, h)])
                h += res[0].size[1]
            if res[1]:
                hblist.append([res[1], (0, h)])
                h += res[1].size[1]
            if res[2]:
                hblist.append([res[2], (25, h)])
                h += res[2].size[1]
            # 新建图片底板，进行绘图
            img = Image.new("RGB", (740, h+20), "#F4F4F4")
            img_d = ImageDraw.Draw(img)
            # 添加简略头部信息 如 “ @NGWORKS ” 样式
            if self.DynamicData.card.origin_user.info.uname:
                name = '@'+self.DynamicData.card.origin_user.info.uname
            elif card.apiSeasonInfo:
                # 这里一般是番剧、电视剧、影视等等
                name = card.apiSeasonInfo.title
            elif self.DynamicData.card.origin["up_info"]:
                name = '@'+self.DynamicData.card.origin["up_info"]["name"]

            # 头部信息字体
            MainFont = ImageFont.truetype(NotoSansCJK, 28)
            img_d.text((20, 10), name, font=MainFont, fill="#178bcf")

            # 利用预渲染信息和渲染返回结果进行渲染
            for i in hblist:
                img.paste(i[0], i[1])
            return img

    async def ReneringManage(self, Dynamicdata):
        """渲染任务管理
           ----------
        """
        # 获取数据
        self.DynamicData = DynamicCard(**Dynamicdata)
        self.DynamicId = self.DynamicData.desc.dynamic_id
        card = self.DynamicData.card
        desc = self.DynamicData.desc
        display = self.DynamicData.display
        tasks = [
            makeQRcode(f'https://t.bilibili.com/{self.DynamicId}'),
            self.headRendering(desc),
            self.NGSSTrcker(card, display),
            self.FunctionBlock(desc.type, card),
            self.AddCard(display),
            self.Reprender(desc, card, display)
        ]

        res = await asyncio.gather(*tasks)

        officialModle = Image.open(bsepth + r'element/om.png')
        top = officialModle.crop((0, 0, 1080, 263))
        w, h = top.size
        top = top.resize((740, int(740/(w/h))))
        booten = officialModle.crop((0, 750, 1080, 974))
        w, h = booten.size
        booten = booten.resize((740, int(740/(w/h))))
        officialModle.close()

        hblist = []
        hblist.append([top, (0, 0)])
        h = top.size[1]-50
        hblist.append([res[1], (-8, h)])
        h += res[1].size[1]

        if desc.user_profile.info.uid in [1974708000, 153373112]:
            h = h-20
            off = Image.open(bsepth+'element/off.png')
            w = (740 - off.size[0])/2
            hblist.append([off, (int(w), h)])
            h += off.size[1] + 20

        if res[2]:
            hblist.append([res[2], (20, h)])
            h += res[2].size[1]
        if res[3]:
            hblist.append([res[3], (0, h)])
            h += res[3].size[1] + 10
        if res[5]:
            hblist.append([res[5], (0, h)])
            h += res[5].size[1]
        if res[4]:
            hblist.append([res[4], (25, h)])
            h += res[4].size[1]
        hblist.append([booten, (0, h)])
        h += booten.size[1]

        img = Image.new("RGB", (740, h), "#FFFFFF")
        for i in hblist:
            img.paste(i[0], i[1])
        img.paste(res[0], (590, h-booten.size[1]+30))
        # img.save('t.jpg')
        # img.save(f'./test/{self.DynamicId}.jpg')
<<<<<<< HEAD
        self.ReprenderIMG = img
=======
        self.ReprenderIMG = img


# def main(Dynamicdata):
#     DynamicData = DynamicCard(**Dynamicdata)
#     DynamicId = DynamicData.desc.dynamic_id
#     card = DynamicData.card
#     desc = DynamicData.desc
#     display = DynamicData.display
#     head = ThreadCli(headRendering,(desc,),"face_threading")
#     head.start()
#     head.join()
#     return head.getResult()
>>>>>>> 61b4b3f6be7c2f406c5e95ca20e4c4949f474954
