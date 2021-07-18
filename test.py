# -*- encoding: utf-8 -*-
from bilibili_dynamic import DynamicRender
import asyncio
from dylist import dylist

dylist = [{
        "desc": {
            "uid": 26366366,
            "type": 2048,
            "rid": 533520352262464800,
            "acl": 0,
            "view": 433322,
            "repost": 29,
            "comment": 38,
            "like": 2182,
            "is_liked": 0,
            "dynamic_id": 533520352186713000,
            "timestamp": 1623058287,
            "pre_dy_id": 0,
            "orig_dy_id": 0,
            "orig_type": 0,
            "user_profile": {
                "info": {
                    "uid": 26366366,
                    "uname": "哔哩哔哩活动",
                    "face": "https://i0.hdslb.com/bfs/face/1e711421fdd158a0cadc1c4351ca19a75ea712ec.jpg"
                },
                "card": {
                    "official_verify": {
                        "type": 1,
                        "desc": "哔哩哔哩活动相关官方账号"
                    }
                },
                "vip": {
                    "vipType": 2,
                    "vipDueDate": 1921507200000,
                    "vipStatus": 1,
                    "themeType": 0,
                    "label": {
                        "path": "",
                        "text": "十年大会员",
                        "label_theme": "ten_annual_vip",
                        "text_color": "#FFFFFF",
                        "bg_style": 1,
                        "bg_color": "#FB7299",
                        "border_color": ""
                    },
                    "avatar_subscript": 1,
                    "nickname_color": "#FB7299",
                    "role": 7,
                    "avatar_subscript_url": "https://i0.hdslb.com/bfs/vip/icon_Certification_big_member_22_3x.png"
                },
                "pendant": {
                    "pid": 3860,
                    "name": "2021拜年纪",
                    "image": "https://i2.hdslb.com/bfs/garb/item/7f8aa8ef1eed8c2dce0796801ddc82552a4164f9.png",
                    "expire": 0,
                    "image_enhance": "https://i2.hdslb.com/bfs/garb/item/7f8aa8ef1eed8c2dce0796801ddc82552a4164f9.png",
                    "image_enhance_frame": ""
                },
                "decorate_card": {
                    "mid": 26366366,
                    "id": 3861,
                    "card_url": "https://i0.hdslb.com/bfs/garb/item/4a21a6e2ce58e28b4b14b808d47f22b3705764a1.png",
                    "card_type": 2,
                    "name": "2021拜年纪粉丝专属",
                    "expire_time": 0,
                    "card_type_name": "免费",
                    "uid": 26366366,
                    "item_id": 3861,
                    "item_type": 3,
                    "big_card_url": "https://i0.hdslb.com/bfs/garb/item/4a21a6e2ce58e28b4b14b808d47f22b3705764a1.png",
                    "jump_url": "https://www.bilibili.com/h5/mall/fans/recommend/3898?navhide=1&mid=26366366&from=dynamic",
                    "fan": {
                            "is_fan": 1,
                            "number": 13307,
                            "color": "#ec3d39",
                            "num_desc": "013307"
                    },
                    "image_enhance": "https://i0.hdslb.com/bfs/garb/item/4a21a6e2ce58e28b4b14b808d47f22b3705764a1.png"
                },
                "rank": "10000",
                "sign": "哔哩哔哩活动相关账号。（仔细看我~~是不是还挺可爱的？不信你多看两眼）",
                "level_info": {
                        "current_level": 6
                }
            },
            "uid_type": 1,
            "stype": 0,
            "r_type": 0,
            "inner_id": 0,
            "status": 1,
            "dynamic_id_str": "533520352186712994",
            "pre_dy_id_str": "0",
            "orig_dy_id_str": "0",
            "rid_str": "533520352262464738"
        },
        "card": "{\"item\":{\"at_control\":\"\"},\"rid\":533520352262464738,\"sketch\":{\"biz_type\":1,\"cover_url\":\"https:\\/\\/i0.hdslb.com\\/bfs\\/activity-plat\\/static\\/8a3e1fa14e30dc3be9c5324f604e5991\\/l2FtqGO65x_w350_h350.jpg\",\"desc_text\":\"超高奖金+出版机会，下一个科幻作家就是你\",\"sketch_id\":533520352215409496,\"tags\":[{\"color\":\"7D75F2\",\"name\":\"活动\",\"type\":1}],\"target_url\":\"https:\\/\\/www.bilibili.com\\/blackboard\\/activity-sci-fi.html?share_source=bili&share_medium=web&bbid=E49CA4BE-580F-4B81-B073-4EC416EA8B1118557infoc&ts=1623058054779\",\"title\":\"刘慈欣喊你写科幻-专栏征文活动\"},\"user\":{\"face\":\"https:\\/\\/i2.hdslb.com\\/bfs\\/face\\/1e711421fdd158a0cadc1c4351ca19a75ea712ec.jpg\",\"uid\":26366366,\"uname\":\"哔哩哔哩活动\"},\"vest\":{\"content\":\"大刘喊你来写科幻小说啦！即日起至7月11日，在B站专栏投稿1万字以内的原创科幻小说，就能参加由刘慈欣全程参与指导的读客科幻文学奖征文大赛，优秀作品还将获得刊登出版机会哟！\",\"ctrl\":\"\",\"uid\":26366366}}",
        "extend_json": "{\"from\":{\"up_close_comment\":0},\"like_icon\":{\"action\":\"\",\"action_url\":\"\",\"end\":\"\",\"end_url\":\"\",\"start\":\"\",\"start_url\":\"\"}}",
        "display": {
                "relation": {
                    "status": 2,
                    "is_follow": 1,
                    "is_followed": 0
                }
        }
    }]

async def test():
    for element in dylist:
        # 这里实例化了 DynamicPictureRendering 类
        # data 为动态数据，tmp_path 为 缓存文件夹的位置（绝对路径相对路径均可）
        Render = DynamicRender.DynamicPictureRendering(element, tmp_path=r"tmp")
        await Render.ReneringManage()
        # 您可以在实例化的类中的
        print(Render.DynamicId)
        Render.ReprenderIMG.show()

# 运行协程函数需要在事件循环中运行
loop = asyncio.get_event_loop()
loop.run_until_complete(test())

