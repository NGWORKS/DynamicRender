# -*- encoding: utf-8 -*-
"""
初始化
~~~~~

copyright: (c) 2021 by NGWORKS.

license: MIT.
"""

import os
from fontTools.ttLib.ttFont import TTFont
from matplotlib.font_manager import fontManager
from pathlib import Path
from .network import Networks

link = Networks()

workpath = os.getcwd()
bsepth = f'{os.path.dirname(__file__)}/'

NotoSansCJK = f'{bsepth}typeface/NotoSansCJKsc-Regular.otf'
NotoColorEmoji = f'{bsepth}typeface/NotoColorEmoji.ttf'
CODE2000 = f'{bsepth}typeface/CODE2000.ttf'
Unifont = f'{bsepth}typeface/Unifont.ttf.ttf'
arial = f'{bsepth}typeface/reserve/arial.ttf'
himalaya = f'{bsepth}typeface/reserve/himalaya.ttf'


muniMap = TTFont(NotoSansCJK)['cmap'].tables[0].ttFont.getBestCmap()
euniMap = TTFont(NotoColorEmoji)['cmap'].tables[0].ttFont.getBestCmap()
cuniMap = TTFont(CODE2000)['cmap'].tables[0].ttFont.getBestCmap()

# tfl = [[f.fname, f.name, f.style] for f in fontManager.ttflist]
# f = fontManager.ttflist
fontList = [[TTFont(arial)['cmap'].tables[0].ttFont.getBestCmap(), arial]]

fontList.append([TTFont(himalaya)['cmap'].tables[0].ttFont.getBestCmap(), himalaya])

# 加入系统所有字体
# for f in tfl:
#     f_path = Path(f[0])
#     try:
#         if f_path.suffix not in ['.ttf', '.TTF', '.otf', '.OTF']:
#             print(f'字体{f[0]}不符合样式需求，已经排除。')
#             continue
#         oofont = TTFont(f[0])
#         oouniMap = oofont['cmap'].tables[0].ttFont.getBestCmap()
#         fontList.append([oouniMap, f[0]])
#     except:
#         print(f'导入{f[0]}失败，无需处理')




