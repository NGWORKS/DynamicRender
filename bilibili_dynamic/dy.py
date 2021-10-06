from .DynamicRender import DynamicCard
from .ThreadCli import ThreadCli
from .Head import headRendering
from .article import tr
from PIL import Image


def main(Dynamicdata):
    DynamicData = DynamicCard(**Dynamicdata)
    DynamicId = DynamicData.desc.dynamic_id
    card = DynamicData.card
    desc = DynamicData.desc
    display = DynamicData.display
    head = ThreadCli(headRendering,(desc,),"face_threading")
    t = ThreadCli(tr,(card,display),"tr")
    t.start()
    head.start()
    head.join()
    t.join()
    head = head.getResult()
    tesxt = t.getResult()
    hblist = []
    hblist.append([head, (0, 0)])
    h = head.size[1]
    hblist.append([tesxt, (0, h)])
    h += tesxt.size[1]

    img = Image.new("RGB", (740, h), "#FFFFFF")
    for i in hblist:
        img.paste(i[0], i[1])
    img.show()
    return img