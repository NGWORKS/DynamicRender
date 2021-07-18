# -*- encoding: utf-8 -*-
from bilibili_dynamic import DynamicRender
import asyncio


data = {
    "desc": {
        "uid": 1974708000,
        "type": 4,
        "rid": 534541240140255858,
        "acl": 0,
        "view": 96,
        "repost": 3,
        "comment": 0,
        "like": 0,
        "is_liked": 0,
        "dynamic_id": 534541240138138083,
        "timestamp": 1623295981,
        "pre_dy_id": 0,
        "orig_dy_id": 0,
        "orig_type": 0,
        "user_profile": {
            "info": {
                "uid": 1974708000,
                "uname": "NGBOT2",
                "face": "https://i0.hdslb.com/bfs/face/8244afb8b300e4a99bdcac684153bbb6d15ec126.jpg"
            },
            "card": {
                "official_verify": {
                    "type": -1,
                    "desc": ""
                }
            },
            "vip": {
                "vipType": 0,
                "vipDueDate": 0,
                "vipStatus": 0,
                "themeType": 0,
                "label": {
                    "path": "",
                            "text": "",
                            "label_theme": "",
                            "text_color": "",
                            "bg_style": 0,
                            "bg_color": "",
                            "border_color": ""
                },
                "avatar_subscript": 0,
                "nickname_color": "",
                "role": 0,
                "avatar_subscript_url": ""
            },
            "pendant": {
                "pid": 0,
                "name": "",
                        "image": "",
                        "expire": 0,
                        "image_enhance": "",
                        "image_enhance_frame": ""
            },
            "rank": "10000",
                    "sign": "不要回应！！！✨✨NG的超智能bot！✨✨这是二号机。联系我ad@vup. link",
                    "level_info": {
                        "current_level": 2
            }
        },
        "uid_type": 1,
        "stype": 0,
        "r_type": 1,
        "inner_id": 0,
        "status": 1,
        "dynamic_id_str": "534541240138138083",
        "pre_dy_id_str": "0",
        "orig_dy_id_str": "0",
        "rid_str": "534541240140255858"
    },
    "card": "{ \"user\": { \"uid\": 1974708000, \"uname\": \"NGBOT2\", \"face\": \"https:\/\/i0.hdslb.com\/bfs\/face\/8244afb8b300e4a99bdcac684153bbb6d15ec126.jpg\" }, \"item\": { \"rp_id\": 534541240140255858, \"uid\": 1974708000, \"content\": \"♛(¦3【▓▓】_(≧∇≦」∠)_(ಡωಡ)✿ヽ(°▽°)ノ✿（⌒▽⌒）_(:з」∠)_( ゜- ゜)つロ(=・ω・=)(*°▽°*)八(*°▽°*)♪눈_눈(｀・ω・´)(￣3￣)✧(≖ ◡ ≖✿)(･∀･)━━━∑(ﾟ□ﾟ*川━_(≧∇≦」∠)_(ಡωಡ)(〜￣△￣)〜→_→(°∀°)ﾉ╮(￣▽￣)╭(ﾟДﾟ≡ﾟдﾟ)!?(;¬_¬)←_←( ´_ゝ｀)( ´･･)ﾉ(._.`)Σ(ﾟдﾟ;)Σ( ￣□￣||)<(´；ω；`)(●￣(ｴ)￣●)(｡･ω･｡)(^・ω・^ )（\/TДT)\/ε=ε=(ノ≧∇≦)ノ(´･_･`)(-_-#)（￣へ￣）(\\\"▔□▔)\/ヽ(`Д´)ﾉ(╯°口°)╯(┴—┴(￣ε(#￣) Σ(￣ε(#￣) Σ(╯°口°)╯(┴—┴ヽ(`Д´)ﾉ(\\\"▔□▔)\/(∂ω∂)｡ﾟ(ﾟ´Д｀)ﾟ｡(๑>؂<๑）(º﹃º )(┯_┯)(・ω< )★( ๑ˊ•̥▵•)੭₎₎¥ㄟ(´･ᴗ･`)ノ¥(๑‾᷅^‾᷅๑)٩(๛ ˘ ³˘)۶❤Σ_(꒪ཀ꒪」∠)_\", \"ctrl\": \"\", \"orig_dy_id\": 0, \"pre_dy_id\": 0, \"timestamp\": 1623295981, \"reply\": 0 } }",
            "extend_json": "{\"from\":{\"emoji_type\":1,\"up_close_comment\":0,\"verify\":{}},\"like_icon\":{\"action\":\"\",\"action_url\":\"\",\"end\":\"\",\"end_url\":\"\",\"start\":\"\",\"start_url\":\"\"},\"topic\":{\"is_attach_topic\":1}}",
            "display": {
                "topic_info": {
                    "topic_details": [
                        {
                            "topic_id": 6757324,
                            "topic_name": "￣) Σ(￣ε(",
                            "is_activity": 1,
                            "topic_link": "https://www.bilibili.com/blackboard/dynamic/66323"
                        }
                    ]
                },
                "relation": {
                    "status": 1,
                    "is_follow": 0,
                    "is_followed": 0
                },
                "show_tip": {
                    "del_tip": "要删除动态吗？"
                }
    }
}

# 这里实例化了 DynamicPictureRendering 类
# data 为动态数据，tmp_path 为 缓存文件夹的位置（绝对路径相对路径均可）
Render = DynamicRender.DynamicPictureRendering(data, tmp_path=r"tmp")

# 运行协程函数需要在事件循环中运行
loop = asyncio.get_event_loop()
loop.run_until_complete(Render.ReneringManage())

# 您可以在实例化的类中的
Render.ReprenderIMG.show()
