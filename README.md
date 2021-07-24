# 几乎一致的动态样式渲染！
<div align=center> 
    <img src="https://data.ngworks.cn/github/b3.jpg"/>
</div>

## 一、项目介绍

### 1、介绍

形象担当：[@禾咕咕](https://space.bilibili.com/254397112 )


### 2、基本功能
本项目实现了将哔哩哔哩返回的数据渲染为类似与B站APP官方的分享图片。
如下图所示：


<div align=center>
    <img src="https://data.ngworks.cn/github/t.jpg" width = 30% />
    <img src="https://data.ngworks.cn/github/t2.jpg" width = 35% />
</div>
<div align=center>
    <img src="https://data.ngworks.cn/github/t3.jpg" width = 35% />
    <img src="https://data.ngworks.cn/github/t6.jpg" width = 25% />
</div>


### 3、环境
本项目基于**Python3.9.0**开发，**在其他版本的运行状态未知**。本项目使用2021年7月的哔哩哔哩API接口，**不保证**后续接口与数据结构不会发生变化。

### 4、依赖
|  Package  |  Version  |
|-----------|   ------  |
|Pillow     |      8.0.1|
|aiohttp    |    3.7.2  |
|qrcode     |    6.1    |
|pydantic   |    1.7.3  |
|pathlib    |    1.0.1  |
|matplotlib |    3.4.0  |
|urllib3    |    1.25.11|
|fonttools  |    4.24.4 |

### 5、项目结构
本项目结构如下：
```
├─ bilibili_dynamic
│  │
│  │  DynamicRender.py                 主要的程序文件
│  │  format.py                        进行数据验证的程序文件
│  │  initialize.py                    进行初始化的程序文件
│  │  network.py                       进行网络通信的程序文件
│  │  textTools.py                     进行渲染的部分文字工具
│  │  __init__.py                      __init__.py
│  │  _version.py                      版本信息
│  ├─ typeface                         字体文件夹
│  │  │ Unifont.ttf                    Unifont字体
│  │  │ CODE2000.ttf                   CODE2000字体
│  │  │ NotoColorEmoji.ttf             Noto emoji字体
│  │  │ NotoSansCJKsc-Regular.otf      思源黑体
│  │  │ NONT LICENSE                   Noto字体 LICENSE
│  │  ├─ reserve                       后备字体
│  │  
│  ├─ element                          图片组件文件夹
│  
│  README.md         自述文件
│  LICENSE           LICENSE
│  test.py           示例       

```
### 6、交流
外联群QQ:781665797

# 二、使用
## 1、安装
### (1)、pip安装(推荐）
您可以使用pip快速的安装
```
pip install bilibili-dynamic
```
> 目前 pip 源中的0.0.7版本存在问题。请根据(3)、使用releases中的版本  安装 我们会在0.0.8修复
### (2)、自行构建
* 克隆仓库中的代码。
* 您可以使用 `poetry` 工具，如果您没有，可以执行下列pip 命令。
```
pip install poetry
```
* 在项目根目录执行以下命令bulid
```
poetry publish --build
```
* ./dist 中是构建完成的项目，然后执行（3） 所述的方法安装。
### (3)、使用releases中的版本
请您前往[releases](https://github.com/NGWORKS/DynamicRender/releases/)页面，自行下载后缀名为`.whl`的文件，并牢记文件名称。然后使用：
```
pip install 下载下来的文件名称
```

## 2、使用
* 传入 API返回数据中的`data`下的`card` 或与结构之一样的数据。
```python
from bilibili_dynamic import DynamicRender
import asyncio

# 导入数据示例
from dylist import dylist


Render = DynamicRender.DynamicPictureRendering(path="./tmp")
async def test():
    for element in dylist:
        await Render.ReneringManage(element)
        # 您可以在实例化的类中的 ReprenderIMG 获得图片对象
        Render.ReprenderIMG.show()
        break

# 运行协程函数需要在事件循环中运行
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
```
> **注意：** 这个写法只适用于 `0.0.7` （含）以上的版本。

> 我们在 `test.py` 中准备了一个小示例，您可以参考其使用。


# 三、如何工作
我们将动态的渲染分为五大部分，每部分独立渲染：

**`头部信息`、`文字部分`、`功能块`（图片动态的图片、视频的视频等）、`附加卡片`（相关游戏、直播预约等）、`转发信息`（转发内容）**
每部分根据动态的内容渲染，如果**没有该部分则不渲染**。
每个模块渲染是**异步**的，其关系您可以根据下图理解：
<div align=center> <img src="https://data.ngworks.cn/github/1.png" width = 150%/> </div>

此图仅供参考，在使用过程中有诸多因素会影响渲染的流程。

> **附加卡片**通常不会下载图片，除了卡片展示游戏相关时。

> **转发信息**就是将上述流程嵌套了一次，只是不渲染头部信息，其余基本一致，故不赘述。

## 1、头部信息
这个模块的实现是在`DynamicRender.py`中的`DynamicPictureRendering`类中的`headRendering`方法。
如项目介绍图片当中的一致，本模块实现了将头像、挂件缓存与渲染，同时本模块可以对该动态发布的时间、账号是否大会员、认证账号进行详细的渲染。

## 2、文字部分
该部分是本项目的核心模块，主要实现了将动态文字进行富文本化。实现是在`DynamicRender.py`中的`DynamicPictureRendering`类中的`NGSSTrcker`方法。
为了方便您更好对这个理解这个模块的运作方式，下图介绍了该模块的工作细节：
<div align=center> <img src="https://data.ngworks.cn/github/2.png" width = 150%/> </div>

* `NGSS`识别了特殊文本的样式，和在字符串中的位置，是后续文本处理的指导性数据。
* `RenderList`包含了以特殊文本为分隔符的所有文本信息。
* `rl` 包含了以`字符`为单位的文本渲染信息。
* `pl` 包含了以`bilibili表情包`为单位的渲染信息。
* `tl` 包含了以`特殊功能图片`的渲染信息，如动态抽奖前的小礼物，投票的柱状图，网页链接的链接图标。

## 3、功能块
这个模块的实现是在`DynamicRender.py`中的`DynamicPictureRendering`类中的`FunctionBlock`方法。
它实现了渲染九宫格与专栏封面，视频封面，与直播封面。

## 4、附加卡片
这个模块的实现是在`DynamicRender.py`中的`DynamicPictureRendering`类中的`AddCard`方法。
它实现了渲染投票，视频预约，直播预约，游戏信息等。

## 5、转发信息
这个模块的实现是在`DynamicRender.py`中的`DynamicPictureRendering`类中的`Reprender`方法。
渲染源动态内容，原理与总动态基本一致，差别仅在字体颜色和对于头部信息渲染的省略。
这个模块调用了上述除过`头部信息`以外的三个模块。

# 四、贡献 - 特别感谢 - license
## 1、贡献
如果您发现了更好的使用方法，不妨分享出来！你可以使用pr功能提交请求，我会审阅。或者在使用中出现了什么问题，都可以提交issue，或者加入我们的`外联群（QQ:781665797）`交流。

## 2、特别感谢
- [`bilibili-API-collect`](https://github.com/SocialSisterYi/bilibili-API-collect)：非常详细的 B站 api 文档
- [`HarukaBot`](https://github.com/SK-415/HarukaBot)：非常nb的机器人
- [`Google Noto Fonts`](https://www.google.cn/get/noto/)：适用于所有语言的漂亮且免费的字体！
- [`unifont`](http://www.unifont.org/new/)：伟大的字体项目
## 3、license
AGPL-3.0 许可证
