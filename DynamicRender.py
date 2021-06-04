# -*- encoding: utf-8 -*-
import os
from typing import Optional,Union,List
from pydantic import BaseModel,Json
from PIL import Image,ImageFont,ImageDraw
import aiohttp,asyncio,requests,time,re
from urllib.parse import urlparse
from io import BytesIO

"""
    写在前面：
        这是我第一次使用pydantic与pil，当时看很多机器人使用无头浏览器截图，但是不知道什么原因。
    会经常截图失败，慢（实名Diss hb）所以就“艺高人胆大”（艺高个鬼啊）的写了这个东西~

        特色：可以实现b站富文本的渲染，图片自适应，挂件，大会员，认证号，投稿，专栏的渲染
            绝大数下载使用Aiohttp异步下载（我异步写的很烂不排除有问题）
            一堆shit（这是什么特色啊喂）
            对于速度我还是很有信心，cpu和网络不是那种差的很离谱的基本最长2秒左右（头像挂件均未缓存）
            平均 0.7 秒 ，有缓存个别 0.2s
            
    【直接run就行】

        ISDO 富文本
        ISDO 相册
        ISDO 视频
        ISDO 下载异步
        ISDO 专栏
        TODO 转发动态渲染
        TODO 做个配置文件，修改样式起来更方便
        TODO 再拆的细节一点，好维护
        TODO 组件异步渲染 是区块
        TODO 优化代码，改的优雅一点（？

"""

class info(BaseModel):
    """用户信息"""
    uid : int
    uname : str
    face : str

class level_info(BaseModel):
    """等级"""
    current_level: int

class pendant(BaseModel):
    """挂件"""
    pid:int
    name:str
    image:str

class official_verify(BaseModel):
    """认证用户情况"""
    type:int
    desc:str


class inofcard(BaseModel):
    official_verify:official_verify

class vip(BaseModel):
    """大会员情况"""
    vipType:int
    nickname_color:str

class user_profile(BaseModel):
    info : info
    level_info : level_info
    pendant:pendant
    card:inofcard
    vip:vip

class desc(BaseModel):
    type:int
    timestamp:int
    view:int
    orig_dy_id:Optional[int] = None
    orig_type:int
    user_profile : user_profile

class topic_details(BaseModel):
    topic_name:str
    is_activity: bool

class emoji_details(BaseModel):
    emoji_name:str
    id:int
    text:str
    url:str

class Topic_info(BaseModel):
    topic_details : List[topic_details]

class Emoji_details(BaseModel):
    emoji_details : List[emoji_details]

class at_control(BaseModel):
    data:int
    length:int
    location:int
    type:int
class pictures(BaseModel):
    img_src : str
    img_height : int
    img_width : int

# 动态内容整理
class DynamicItem(BaseModel):
    at_control: Optional[Union[Json,str]] = None
    description : Optional[str] = None
    upload_time : Optional[int] = None
    content: Optional[str] = None
    ctrl: Optional[Union[Json,str]] = None
    pictures:Optional[Union[str,List[pictures]]]


class Dynamic(BaseModel):
    item : Optional[DynamicItem] = None
    dynamic:Optional[str] = None
    pic:Optional[str] = None
    title : Optional[str] = None
    origin: Optional[Json] = None
    image_urls: Optional[List] = None
    summary:Optional[str] = None


class Display(BaseModel):
    topic_info:Optional[Topic_info] = None
    emoji_info:Optional[Emoji_details] = None
class DynamicCard(BaseModel):
    """
    详细信息的card
        :desc 动态基本信息
        :card 动态的内容
    """
    desc : desc
    card : Json[Dynamic]
    display:Display

class DynamicData(BaseModel):
    """动态详细信息data"""
    card : DynamicCard

class DynamicDetail(BaseModel):
    """动态详细信息接口返回"""
    code : int
    data : DynamicData

class DynamicPictureRendering:
    def __init__(self,DynamicId) -> int :
       self.DynamicId = DynamicId
       self.DynamicImg = {}
       self.HeadImg = []
       self.EmojiImg = []
       self.FunctionBlockImg = None
       self.headRenderingImg = None
       self.NGSSTrckerImg = None


    async def fetch(self,session, url,jsont = True):
        """实现GET请求"""
        async with session.get(url) as response:
            if jsont:
                return await response.json()
            else:
                return await response.read()

    async def load(self,session, url,jsont = True):
        """实现下载图片"""
        async with session.get(url) as response:

            return await response.json()

    async def getDynamicData(self):
        """获取动态的数据"""
        url =f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={self.DynamicId}'
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, url)
        return DynamicDetail(**data)

    async def getPage(self,url,count,tp = 0):
        """下载图片"""
        async with aiohttp.ClientSession() as session:
            data = await self.fetch(session, url,jsont=False)
            pic = Image.open(BytesIO(data))
            if tp == 0:
                self.DynamicImg[count] = pic
            elif tp == 1:
                self.HeadImg.append({"data":pic,"path":count})
            else:
                self.EmojiImg.append({"data":pic,"path":count})
            return pic

    def get_font_render_size(self,FOUNT,fontsize,text):
        """获取字符精准宽度"""
        try:
            font = ImageFont.truetype(FOUNT, fontsize, 0)
            width, height = font.getsize(text)
            return (width, height)
        except:
            print("hfd")
            return (fontsize,fontsize)

    def convert_image_to_circle(self,pic):
        """裁剪圆形"""
        ima = pic
        size = ima.size
        # 因为是要圆形，所以需要正方形的图片
        r2 = min(size[0], size[1])
        if size[0] != size[1]:
            imb = Image.new('RGBA', (r2, r2), (100, 100, 100, 0))
            pima = ima.load()  # 像素的访问对象
            pimb = imb.load()
            for i in range(r2):
                for j in range(r2):
                    pimb[i, j] = pima[(size[0] - r2) / 2 + i, (size[1] - r2) / 2 + j]
        else:
            imb = ima

        # 最后生成圆形图片
        r3 = int(r2 / 2)  # 圆心横坐标 圆的半径
        imc = Image.new('RGBA', (r3 * 2, r3 * 2), (100, 100, 100, 0)) #这是生成了一张透明图片 500*500
        pimb = imb.load()  # 像素的访问对象  要裁切的图片
        pimc = imc.load()    #透明图片

        for i in range(r2):
            for j in range(r2):
                lx = abs(i - r3)  # 到圆心距离的横坐标
                ly = abs(j - r3)  # 到圆心距离的纵坐标
                l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径

                if l < r3:
                    pimc[i, j] = pimb[i, j]   #这里就是替换了 把彩色的 替换到透明中
        return imc

    def isEmoji(self,t):
        res = re.compile(u'[\U00010000-\U0010ffff\\uD800-\\uDBFF\\uDC00-\\uDFFF]')
        if re.search(res,t):
            return True
        else:
            return False
    def AoutLine(self,limt,text,size,color = '#000000',fount= 'WeiRuanYaHei-1.ttf',x = 15,y = 0):
        """非富文本样式计算"""
        START_X = x
        START_Y = y
        SZ = 0
        FOUNT_SIZE = size
        LINE_HIGHT = 15
        LINE_LIMT = limt
        pl = []
        for i in text:
            if START_X >= LINE_LIMT:
                START_X = x
                START_Y += FOUNT_SIZE + LINE_HIGHT
            wihdt = self.get_font_render_size(fount,FOUNT_SIZE,i)[0]
            pl.append({"t":i,"d":(START_X,START_Y),"c":color,"f":fount})
            START_X += wihdt
        return pl


    async def headRendering(self,data):
        """
        头部信息渲染器：
        
        :param data: 动态的数据，为一个`实例化后的类`。
        :returns:  输出为一个150*300的`图片`。
        
        这个函数通过数据进行头部`头像、名称、大会员、认证、时间戳、浏览量`进行渲染。

        """
        cpx = 150
        fpx = int(cpx/2)
        ppx = int((fpx/48)*82)
        ico = int((fpx/48)*16)
        desc = data.data.card.desc
        user_profile = data.data.card.desc.user_profile
        userinfo = user_profile.info
        vip = user_profile.vip
        official = user_profile.card.official_verify
        pendant = user_profile.pendant

        # ISDO 下载照片实现异步，一次干完
        # ISDO 缓存
        # TODO 复用下载后的对象，下载了之后直接调用，就不要在去磁盘里打开了

        tasks = []
        fm = urlparse(userinfo.face).path[10:]
        facePath = f'./face/{fm}'
        pendantPath = f'./pendant/{pendant.pid}.png'
        if not os.path.exists(facePath):
            tasks.append(asyncio.create_task(self.getPage(userinfo.face+'@150w.webp',facePath,1)))
        if not os.path.exists(pendantPath) and pendant.image != "":
            tasks.append(asyncio.create_task(self.getPage(pendant.image+'@180w.webp',pendantPath,1)))    
        if len(tasks)  != 0:
            await asyncio.wait(tasks)
            for n in self.HeadImg:
                n['data'].save(n['path'])

        # 新建头像渲染画布
        HeadRender= Image.new("RGB", (cpx, cpx), "#FFFFFF")
        face = Image.open(facePath).resize((fpx,fpx),Image.ANTIALIAS)
        # 剪裁 
        face = self.convert_image_to_circle(face)
        HeadRender.paste(face, (int((cpx-fpx)/2),int((cpx-fpx)/2)),mask=face)    

        if pendant.image != "":
            """渲染头像框"""
            pendant = Image.open(f'./pendant/{pendant.pid}.png').resize((ppx,ppx),Image.ANTIALIAS).convert('RGBA')
            HeadRender.paste(pendant,(int((cpx-ppx)/2),int((cpx-ppx)/2)),mask=pendant)

        if official.type != -1 or vip.vipType != 1:
            """渲染小闪电和大会员标"""
            if vip.vipType != 1:
                box = (69,16,94,41)
            if official.type == 0:
                box = (35,16,60,41)
            elif official.type == 1: 
                box = (1,16,26,41)
            officialimg = Image.open('user-auth.png')
            officialimg = officialimg.crop(box).resize((ico,ico),Image.ANTIALIAS).convert('RGBA')
            HeadRender.paste(officialimg,(fpx+int(ico/2),fpx+int(ico/2)),mask=officialimg)
            officialimg.close()
        # 名字颜色
        if vip.nickname_color == "":
            nickname_color = (34,34,34)
        else:
            nickname_color = (251, 114, 153)

        # 创建主画布准备写字
        main = Image.new("RGB", (cpx*3,cpx), "#FFFFFF")
        main.paste(HeadRender)
        # 写昵称
        ttf_path = "WeiRuanYaHei-1.ttf"
        nicknameFont = ImageFont.truetype(ttf_path,int(cpx/6))
        img_draw = ImageDraw.Draw(main)
        img_draw.text((cpx-8,int(cpx/2-30)), userinfo.uname, font=nicknameFont, fill=nickname_color)
        # 写时间
        timeFont = ImageFont.truetype(ttf_path,int(cpx/8))
        timeArray = time.localtime(desc.timestamp)
        otherStyleTime = time.strftime("%y-%m-%d %H:%M", timeArray)
        # 浏览量
        if desc.view == 0:
            view ='-'
        elif desc.view < 10000:
            view = desc.view
        else:
            view = f'{round(desc.view/10000,1)}万'

        timeText = f'{otherStyleTime} · {view}浏览'

        img_draw.text((cpx-8,int(cpx/2+10)), timeText, font=timeFont, fill=(153,162,170))
        return main
    
    async def NGSSTrcker(self,data):
        """
        根据数据中的信息生成`样式描述信息`(NGSS)与渲染动态文字照片：
        
        :param data: 动态的数据，为一个`实例化后的类`。
        :returns:  输出为一个渲染好的`图片`。
        
        这个函数可以自动的识别、分割出来文字中的艾特、投票、抽奖、标签功能、同时可以渲染表情包，生成`NGSS List`：
            NGSS包含了这段文字的样式，颜色与其相应的位置，一个NGSS信息由以下结构构成:
                :param text : 文字部分
                :param emoji : 表情包部分

                NGSS描述了文字的渲染方法，是NGBOT实现伪富文本的重要组件。
        """
        card = data.data.card.card
        display = data.data.card.display
        # 找文字块
        if card.item.description !=None:
            Text = card.item.description
        elif card.item.content !=None:
            Text = card.item.content
        elif card.dynamic !=None and card.dynamic != "":
            Text = card.dynamic
        else:
            return None
        # 找艾特 抽奖 投票
        if card.item.at_control !=None:
            at_control = card.item.at_control
        elif card.item.ctrl !=None:
            at_control = card.item.ctrl
        else:
            at_control = None
        # 表情包 话题标签
        if display.topic_info !=None:
            topics = display.topic_info.topic_details
        else:
            topics = None
        if display.emoji_info !=None:
            emojis = display.emoji_info.emoji_details
        else:
            emojis = None

        # 生成分割方案与样式描述 NGSS
        fangan = []
        if at_control != None:
            for control in at_control:
                """艾特 抽奖 投票分割方案器"""
                if control['type'] == 2:
                    msg = {"start":0,"end":5,"len":5,"type":2,"data":{"control":control['type']}}
                else:
                    msg = {"start":control['location'],"end":control['location']+control['length'],"len":control['length'],"type":2,"data":{"control":control['type']}}
                fangan.append(msg)

        if emojis != None:
            for emoji in emojis:
                """表情包分割方案器"""
                emojiName = emoji.text
                taglen = len(emojiName)
                t = Text.count(emojiName)
                Textc = Text
                i = 0
                while i != t:
                    if i == 0:
                        start = Textc.index(emojiName)
                        end = start+taglen
                    else:
                        Textc = Textc[0:end]
                        start = Textc.index(emojiName)+end
                        end = start+taglen
                    msg = {"start":start,"end":end,"len":taglen,"type":0,"data":{"url":emoji.url,"id":emoji.id}}
                    fangan.append(msg)
                    i+=1

        if topics != None:
            for topic in topics:
                """话题 活动 分割方案器"""
                topicTag = f'#{topic.topic_name}#'
                taglen = len(topicTag)
                t = Text.count(topicTag)
                Textc = Text
                i = 0
                while i != t:
                    if i == 0:
                        start = Textc.index(topicTag)
                        end = start+taglen
                    else:
                        Textc = Textc[0:end]
                        start = Textc.index(topicTag)+end
                        end = start+taglen+end
                    msg = {"start":start,"end":end,"len":taglen,"type":1,"data":None}
                    fangan.append(msg)
                    i+=1
        indexlist = []
        for fong in fangan:
            indexlist.append(fong['start'])
        indexlist.sort()
        NGSS = []
        for r in indexlist:
            for i in fangan:
                if i['start'] == r:
                    NGSS.append(i)

        # NGSS是渲染方案的描述数据，其规定了文本的分割，样式，类型颜色，以及表情包对应的图片
        count = 0
        RenderList = []
        while count != len(NGSS):
            if count == 0 and NGSS[count]['start'] !=0:
                data = {'type':-1,'text':Text[0:NGSS[count]['start']]}
                RenderList.append(data)
            data = {'type':NGSS[count]['type'],'text':Text[NGSS[count]['start']:NGSS[count]['end']],"data":NGSS[count]['data']}
            RenderList.append(data)

            if count != len(NGSS)-1 and NGSS[count]['end'] != NGSS[count+1]['start']:
                data = {'type':-1,'text':Text[NGSS[count]['end']:NGSS[count+1]['start']]}
                RenderList.append(data)

            if count == len(NGSS)-1 and NGSS[count]['end'] != len(Text):
                data = {'type':-1,'text':Text[NGSS[count]['end']:len(Text)]}
                RenderList.append(data)
            count +=1
        if NGSS == []:
            RenderList = [{'type':-1,'text':Text}]

        # 实现换行符的识别与分割
        for element in RenderList:
            type = element['type']
            text = element['text']
            if type == -1:
                if len(text.split('\n')) > 1:
                    element['text'] = text.split('\n')
        # RenderList 最终样式规定器 计算宽度，分割，细化最初的NGSS
        START_X = 0
        START_Y = 0
        SZ = 1
        FOUNT_SIZE = 30
        LINE_HIGHT = 15
        LINE_LIMT = 675
        rl = []
        pl = []
        for element in RenderList:
            type = element['type']
            text = element['text']
            if type == 0:
                if START_X >= LINE_LIMT:
                    START_X = 0
                    START_Y += FOUNT_SIZE + LINE_HIGHT + 10
                pl.append({"id":element['data']['id'],"d":(START_X,START_Y),"u":element['data']['url']})
                START_X += FOUNT_SIZE + SZ + 10
            else:
                # 如果不是list 就没有换行
                if isinstance(text,list):
                    pp = 1
                    for t in text:
                        for s in t:
                            if START_X >= LINE_LIMT:
                                START_X = 0
                                START_Y += FOUNT_SIZE + LINE_HIGHT
                            if self.isEmoji(s):
                                f = 'NotoColorEmoji.ttf'
                                wihdt = FOUNT_SIZE
                            else:
                                f = 'WeiRuanYaHei-1.ttf'
                                wihdt = self.get_font_render_size(f,FOUNT_SIZE,s)[0]
                            if s =='\u200b':
                                wihdt = FOUNT_SIZE + 5
                            rl.append({"t":s,"d":(START_X,START_Y),"c":"#000000","f":f})
                            START_X += wihdt + SZ
                        if pp != len(text):
                            START_X = 0
                            START_Y += FOUNT_SIZE + LINE_HIGHT
                        pp +=1
                else:
                    for i in text:
                        if START_X >= LINE_LIMT:
                            START_X = 0
                            START_Y += FOUNT_SIZE + LINE_HIGHT
                        if type == -1:
                            c =  "#000000"
                        else:
                            c = "#178bcf"
                        if self.isEmoji(i):
                            f = 'NotoColorEmoji.ttf'
                            wihdt = FOUNT_SIZE
                        else:
                            f = 'WeiRuanYaHei-1.ttf'
                            wihdt = self.get_font_render_size(f,FOUNT_SIZE,i)[0]
                        if i =='\u200b':
                            wihdt = FOUNT_SIZE + 5
                        rl.append({"t":i,"d":(START_X,START_Y),"c":c,"f":f})
                        START_X += wihdt + SZ
        NGSS = {
            "text":rl,
            "emoji":pl
        }
        Render= Image.new("RGB", (700, START_Y+FOUNT_SIZE+LINE_HIGHT), "#FFFFFF")
        img_draw = ImageDraw.Draw(Render)
        for el in rl:
            if el['f'] == 'NotoColorEmoji.ttf':
                emojiRender = Image.new("RGBA",(130,130),(0,0,0,0))
                Font = ImageFont.truetype('NotoColorEmoji.ttf',109)
                emg_draw = ImageDraw.Draw(emojiRender)
                emg_draw.text((0,0),el['t'], font=Font, embedded_color = True)
                emojiRender = emojiRender.resize((30,30),Image.ANTIALIAS)
                Render.paste(emojiRender,(el['d'][0],el['d'][1]+5),emojiRender)
            elif el['t'] =='\u200b':
                gimg = Image.open(f'./bp-svg-icon.png')
                gimg = gimg.crop((0,335,16,351)).resize((FOUNT_SIZE,FOUNT_SIZE),Image.ANTIALIAS).convert('RGBA')
                Render.paste(gimg,(el['d'][0],el['d'][1]+5),mask=gimg)
            if el['t'] == '\r':
                continue
            else:
                nicknameFont = ImageFont.truetype(el['f'],FOUNT_SIZE)
                img_draw.text(el['d'], el['t'], font=nicknameFont, fill=el['c'])

        # ISDO 异步下载表情包
        # TODO 复用下载后的对象，下载了之后直接调用，就不要在去磁盘里打开了

        if len(pl) != 0:
            # 先检查本地有没有
            tasks = []
            for emoji in pl:
                id=emoji['id']
                if not os.path.exists(f'./emoji/{id}.png'):
                    emojiurl = emoji['u']
                    tasks.append(asyncio.create_task(self.getPage(emojiurl,f'./emoji/{id}.png',2)))
            if len(tasks) !=0:
                await asyncio.wait(tasks)
                for n in self.EmojiImg:
                    n['data'].save(n['path'])
            for emoji in pl:
                id=emoji['id']                
                emimg = Image.open(f'./emoji/{id}.png').resize((FOUNT_SIZE+10,FOUNT_SIZE+10),Image.ANTIALIAS).convert('RGBA')
                Render.paste(emimg,emoji['d'],mask=emimg)
                emimg.close()
        return Render

    async def FunctionBlock(self,data):
        type = data.data.card.desc.type
        ttf_path = "WeiRuanYaHei-1.ttf"
        nicknameFont = ImageFont.truetype(ttf_path,25)
        if type == 8:
            
            # TODO 时间和播放按钮

            pic = data.data.card.card.pic + '@720w.webp'
            pic = Image.open(requests.get(pic, stream=True).raw)
            picsize = pic.size
            box = (0,int((picsize[1]-(picsize[0]/16*9))/2),picsize[0],int(((picsize[1]-(picsize[0]/16*9))/2)+(picsize[0]/16*9)))
            pic = pic.crop(box)
            picsize = pic.size
            title = data.data.card.card.title
            img = Image.new("RGB",(740,picsize[1]+10 + 30 + 15),"#FFFFFF")
            img.paste(pic,(10,10))
            img_draw = ImageDraw.Draw(img)
            if len(title) > 36:
                title = title[:36] + '...'
            img_draw.text((10,picsize[1]+20),title, font=nicknameFont, fill="#000000")
            return img
        elif type == 2:
            pictures = data.data.card.card.item.pictures
            piccount = len(pictures)
            if piccount == 1:
                pic = Image.open(requests.get(pictures[0].img_src+'@480w.webp', stream=True).raw)
                h = pictures[0].img_height
                w = pictures[0].img_width
                h = 720/(w/h)
                pic = pic.resize((720,int(h)))
                img = Image.new("RGB",(740,int(h)+40),"#FFFFFF")
                img.paste(pic,(10,20))
                return img
            else:
                picrender  = []

                tasks = []
                i = 0
                for pic in pictures:

                    print(pic.img_height/pic.img_width)

                    url = pic.img_src+'@104w_104h_1e_1c.webp'
                    
                    if pic.img_height/pic.img_width >= 3:
                        url = pic.img_src+'@104w_104h_!header.webp'
                    tasks.append(asyncio.create_task(self.getPage(url,i)))
                    i +=1
                await asyncio.wait(tasks)    

                items = list(self.DynamicImg.items())
                items.sort() 
                self.DynamicImg = [value for key, value in items]

                for pic in self.DynamicImg:
                    w,h = (104,104)
                    picrender.append(pic)
                fulren = []
                if piccount <=2 or piccount == 4:
                    lm = 2
                    w = int((720-10)/lm)
                else:
                    lm = 3
                    w = int((720-20)/lm)
                count = 1
                x = 10
                y = 10
                for pic in picrender:
                    if count > lm:
                        x = 10
                        y += w + 10
                        count = 1
                    fulren.append([pic.resize((w,w),Image.ANTIALIAS),(x,y)])
                    x+= w+10
                    count +=1
                img = Image.new("RGB",(740,y+w+10),"#FFFFFF")
                for el in fulren:
                    img.paste(el[0],el[1])          
                return img

        # IDDO 专栏模块
        elif type == 64:
            """专栏"""  
            image_urls = data.data.card.card.image_urls
            summary = data.data.card.card.summary
            if len(summary) > 52:
                summary = summary[:52] + '...'
            title = data.data.card.card.title
            # ISDO 计算标题文字高度
            titlestly =self.AoutLine(675,title,30,color = '#000000',fount= 'WeiRuanYaHei-1.ttf')
            lasttitle = titlestly[len(titlestly)-1]['d'][1] + 30
            tasks = []
            i = 0
            piccount = len(image_urls)
            for pic in image_urls:
                if piccount !=1:
                    tasks.append(asyncio.create_task(self.getPage(pic+'@104w_104h_1e_1c.webp',i)))
                else:
                    tasks.append(asyncio.create_task(self.getPage(pic+'@520w_120h_1e_1c.webp',i)))
                i +=1
            await asyncio.wait(tasks)    

            items = list(self.DynamicImg.items())
            items.sort() 
            self.DynamicImg = [value for key, value in items]
            fulren = []
            x = 10
            y = lasttitle + 25
            for pic in self.DynamicImg:
                if piccount != 1:
                    w = int((700-20)/3)
                    fulren.append([pic.resize((w,w),Image.ANTIALIAS),(x,y)])
                    x += w+10
                else:
                    h = int(700/(520/120))
                    fulren.append([pic.resize((700,h),Image.ANTIALIAS),(x,y)])
                    w = h
            lastpic = fulren[len(fulren)-1][1][1] + w
            if summary != '':
                summstly =self.AoutLine(675,summary,25,color = '#666666',fount= 'WeiRuanYaHei-1.ttf',y = lastpic+20)
                lastsumm = summstly[len(summstly)-1]['d'][1] + 30
            else:
                lastsumm = lastpic
            # isdo 计算描述文字高度
            img = Image.new("RGB",(740,lastsumm +20),"#FFFFFF")
            img_draw = ImageDraw.Draw(img)
            for el in titlestly:
                nicknameFont = ImageFont.truetype(ttf_path,30)
                img_draw.text(el['d'],el['t'], font=nicknameFont, fill="#000000")
            if summary != '':
                for el in summstly:
                    nicknameFont = ImageFont.truetype(ttf_path,25)
                    img_draw.text(el['d'],el['t'], font=nicknameFont, fill="#666")
            for pic in fulren:
                img.paste(pic[0],pic[1])
            return img

        # TODO 带转发内容判断
        elif type ==1:
            print(data.data.card.card.origin)


    async def ReneringManage(self):
        """渲染任务管理"""
        # 获取数据
        data = await self.getDynamicData()
        head = await self.headRendering(data)
        fount = await self.NGSSTrcker(data)
        function = await self.FunctionBlock(data)
        si1 = head.size
        if fount:
            si = fount.size
        else:
            si = (0,0)
        if function:
            fsize = function.size
        else:
            fsize = (0,0)
        

        img= Image.new("RGB", (740, si[1]+150 + fsize[1]), "#FFFFFF")
        img.paste(head,(-8,0))
        try:
            img.paste(fount,(20,si1[1] - 10))
        except:
            pass
        try:
            img.paste(function,(0,si1[1] - 10 + si[1]))
        except:
            pass

        img.save('./t.jpg')
        

# TODO 含有转发的嵌套与渲染

# 动态id
dynamic_id = 531154173090955046


start = time.perf_counter()

result = DynamicPictureRendering(dynamic_id).ReneringManage()
loop = asyncio.get_event_loop()
loop.run_until_complete(result)

end = time.perf_counter()
print('CPU执行时间: ',end - start)

