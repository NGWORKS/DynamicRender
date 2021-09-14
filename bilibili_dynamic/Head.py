from .network import pictmp,request_img
from .ThreadCli import ThreadCli
from .tmppath import set_tmp,bsepth
from urllib.parse import urlparse
from PIL import Image, ImageFont, ImageDraw
from .textTools import NotoSansCJK
import os,time


faceMark = Image.open(bsepth + 'element/hm.png')
userauth = Image.open(bsepth + 'element/user-auth.png')

def headRendering(desc,cpx = 150,path = None):
    # 头像大小 边长
    fpx = int(cpx/2)
    # 头像框图片边长
    ppx = int((fpx/48)*82)
    # 认证、大会员图标 边长
    ico = int((fpx/48)*16)
    tmppath = set_tmp(path)
    user_profile = desc.user_profile
    userinfo = user_profile.info
    vip = user_profile.vip
    official = user_profile.card.official_verify
    pendant = user_profile.pendant

    fm = urlparse(userinfo.face).path[10:]
    pid = pendant.pid
    facePath = f'{tmppath}face/{fm}'
    pendantPath = f'{tmppath}pendant/{pid}.png'


    if fm in pictmp :
        # 查看缓存中是否存在图片 存在直接读取
        face = pictmp[fm]
    elif os.path.exists(facePath):
        # 查看硬盘中是否存在图片 存在存到缓存并直接读取
        face = Image.open(facePath)
        pictmp[fm] = face
    else:
        # 通过本地尝试获取头像失败 置为 false
        face = False
        # 开启线程从服务器下载
        face_threading = ThreadCli(request_img,(f"{userinfo.face}@150w.webp",),"face_threading")
        face_threading.start()

    if pid == 0:
        # pendant.pid = 0 时 用户没有装备头像框
        pendant = None
    elif pid in pictmp:
        # 查看缓存中是否存在图片 存在直接读取
        pendant = pictmp[pid]
    elif os.path.exists(pendantPath):
        # 查看硬盘中是否存在图片 存在存到缓存并直接读取
        pendant = Image.open(pendantPath)
        pictmp[pid] = pendant
    else:
        # 通过本地尝试获取头像失败 置为 false
        # 没有则开启线程下载
        pendant_threading = ThreadCli(request_img,(f"{pendant.image}@180w.webp",),"pendant_threading")
        pendant_threading.start()
        pendant = False
    
    # 现在线程里面正在下载 先处理文字部分

    # 准备渲染用户名的颜色
    if vip.nickname_color == "":
        nickname_color = (34, 34, 34)
    else:
        nickname_color = (251, 114, 153)

    # 创建主画布准备写字 稍后统一粘贴头像组
    main = Image.new("RGB", (cpx*3, cpx), "#FFFFFF")
    # 写昵称
    ttf_path = NotoSansCJK
    nicknameFont = ImageFont.truetype(ttf_path, int(cpx/6))
    img_draw = ImageDraw.Draw(main)
    img_draw.text((cpx-8, int(cpx/2-30)), userinfo.uname,font=nicknameFont, fill=nickname_color)
    # 写时间
    timeFont = ImageFont.truetype(ttf_path, int(cpx/8))
    timeArray = time.localtime(desc.timestamp)
    otherStyleTime = time.strftime("%m-%d %H:%M", timeArray)
    timeText = f'{otherStyleTime}'
    img_draw.text((cpx-8, int(cpx/2+10)), timeText,font=timeFont, fill=(153, 162, 170))


    # 头像组包括 一个裁切成圆形的头像图片 覆盖的头像框（如有） 认证标志与大会员（如有）
    # 新建头像组渲染画布
    HeadRender = Image.new("RGBA", (cpx, cpx), "#ffffff00")
    # 打开头像蒙版
    facem = faceMark.resize((fpx, fpx), Image.ANTIALIAS)
    # 粘贴头像
    # 要使用头像了 先看看下载了没有
    if face == False:
        # 确定是去下载了 等待线程结束
        face_threading.join()
        # 读取线程返回值
        face = face_threading.getResult()
        # 重置大小并存入缓存
        pictmp[fm] = face
        face.save(facePath)

    HeadRender.paste(face.resize((fpx, fpx), Image.ANTIALIAS),(int((cpx-fpx)/2), int((cpx-fpx)/2)), mask=facem)

    # 存在没有头像框的情况,如果不存在头像框 pendant 是None
    if pendant != None:
        if pendant == False:
            # 确定是去下载了 等待线程结束
            pendant_threading.join()
            # 读取线程返回值
            pendant = pendant_threading.getResult()
            # 重置大小并存入缓存
            pictmp[fm] = pendant
            pendant.save(pendantPath)

        pendant = pendant.resize((ppx, ppx), Image.ANTIALIAS).convert('RGBA')
        HeadRender.paste(pendant, (int((cpx-ppx)/2),int((cpx-ppx)/2)), mask=pendant)

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
        officialimg = userauth.crop(box).resize((ico, ico), Image.ANTIALIAS).convert('RGBA')
        # 粘贴
        HeadRender.paste(officialimg, (fpx+int(ico/2),fpx+int(ico/2)), mask=officialimg)

    main.paste(HeadRender,mask=HeadRender)

    return main

