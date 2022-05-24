from pathlib import Path
from typing import List, Set, Union
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib.ttFont import TTFont
import time
import json

from haruka_bot.utils import get_path
from haruka_bot.dynamic import Dynamic


class Fonts:
    def __init__(self,
                 size = 14,
                 main = 'NotoSansCJKsc-Regular.otf',
                 sub = 'CODE2000.TTF',
                #  sub = 'unifont-13.0.05.ttf',
                 emoji = 'NotoColorEmoji.ttf') -> None:
        self.size = size
        self.px, remain = divmod(self.size * 4, 3)
        self.px = self.px + 1 if remain else 0
        self.main = self._load_font(main)
        self.sub = self._load_font(sub)
        self.emoji = self._load_font(emoji, size=109)
        self.fonts = {
            'main': self.main,
            'sub': self.sub,
            'emoji': self.emoji
        }

    def _load_font(self, name: str, size = None) -> ImageFont.FreeTypeFont:
        if not size:
            size = self.size
        font_path = get_path('fonts', name)
        print(font_path)
        font: ImageFont.FreeTypeFont = ImageFont.truetype(font_path, size=size)
        font.range = self._font_range(font_path)
        font.ascent, font.descent = font.getmetrics()
        return font

    def char_size(self, char: str, font=None):
        name = font or self.char_type(char)
        if name == 'emoji':
            return self.px, self.px
        font = self.get_font(name)
        return font.getsize(char)

    def char_type(self, char: str):
        code = ord(char)
        if code in self.main.range:
            return 'main'
        elif code in self.emoji.range:
            return 'emoji'
        else:
            return 'sub'

    def _font_range(self, font_path):
        font = TTFont(font_path)
        return set(font.getBestCmap().keys())
    
    def get_font(self, name: str):
        return self.fonts[name]


class Phrase:
    def __init__(self, font = None) -> None:
        self.font = font
        self.length = 0
        self.width = 0
        self.text = ''

class Line:
    def __init__(self) -> None:
        self.phrase = Phrase()
        self.phrases = [self.phrase]
        self.width = 0
        self.length = 0
    
    def new_phrase(self, font = None):
        self.phrase = Phrase(font)
        self.phrases.append(self.phrase)
        return self.phrase


class Lines:
    def __init__(self, max_length, fonts = Fonts()) -> None:
        self.max_length = max_length
        self.line = Line()
        self.lines = [self.line]
        self.fonts: Fonts = fonts

    def new_line(self):
        self.line = Line()
        self.lines.append(self.line)
        return self.line
    
    def add_char(self, char):
        line = self.line
        phrase = line.phrase
        font = self.fonts.char_type(char)
        length, width = self.fonts.char_size(char, font)
        if length > self.max_length - line.length - phrase.length or char == '\n':
            line.length += phrase.length
            line.width = max(line.width, phrase.width)
            line = self.new_line()
            phrase = line.phrase
        if char == '\n':
            return
        if not phrase.font:
            phrase.font = font
        if phrase.font != font:
            line.length += phrase.length
            line.width = max(line.width, phrase.width)
            phrase = line.new_phrase(font)
        phrase.length += length
        phrase.width = max(phrase.width, width)
        phrase.text += char
    
    def get(self, text):
        for c in text:
            self.add_char(c)


class DynamicBuilder:
    def __init__(self, text) -> None:
        self.length = 500
        self.width = 500
        self.img = Image.new('RGB', size=(self.length, self.width), color=(255, 255, 255))
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.img)
        self.fonts = Fonts()
        self.text = text
        self.lines = Lines(max_length=self.length, fonts=self.fonts)
    
    def get_lines(self):
        return self.lines.get(self.text)

    def get_emoji_img(self, emojis: str, size = None):
        if not size:
            size = self.fonts.px
        img = Image.new('RGB', size=(self.fonts.emoji.getsize(emojis)), color=(255, 255, 255))
        d: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        d.text((0, 0), emojis, (0, 0, 0), self.fonts.get_font('emoji'), embedded_color = True)
        return img.resize((size * len(emojis), size))

    def draw_text(self):
        left, top = 0, 0
        for line in self.lines.lines:
            for phrase in line.phrases:
                if phrase.font == 'emoji':
                    self.img.paste(self.get_emoji_img(phrase.text, line.width), (left, top))
                else:
                    self.draw.text((left, top), text = phrase.text, fill = (0, 0, 0), font = self.fonts.get_font(phrase.font), embedded_color = True)
                left += phrase.length
            top += line.width
            left = 0
    

if __name__ == "__main__":
    with open(get_path('dynamics.json'), encoding='utf-8') as f:
        dynamics = json.loads(f.read())['data']['cards']
    dynamic = Dynamic(dynamics[0])
    # start = time.time()
    dyb = DynamicBuilder(dynamic.content)
    dyb.get_lines()
    # for line in ti.lines.lines:
    #     for phrase in line.phrases:
    #         print(phrase.text, end='')
    #     print()
    dyb.draw_text()
    dyb.img.show()
    # print(time.time() - start)

