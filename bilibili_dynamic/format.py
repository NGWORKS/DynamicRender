# -*- encoding: utf-8 -*-
"""
对JSON数据进行整理，验证
~~~~~~~~~~~~~~~~~~~~~~

这个模块可用来对动态数据进行整理，验证。

copyright: (c) 2021 by NGWORKS.

license: MIT.
"""
from typing import Optional, Union, List
from pydantic import BaseModel, Json

class info(BaseModel):
    """用户信息"""
    uid: Optional[int] = None
    uname: Optional[str] = None
    face: Optional[str] = None
    head_url: Optional[str] = None
    name: Optional[str] = None


class level_info(BaseModel):
    """等级"""
    current_level: int


class pendant(BaseModel):
    """挂件"""
    pid: int
    name: str
    image: str


class official_verify(BaseModel):
    """认证用户情况"""
    type: int
    desc: str


class inofcard(BaseModel):
    official_verify: official_verify


class vip(BaseModel):
    """大会员情况"""
    vipType: int
    nickname_color: str


class user_profile(BaseModel):
    info: info
    level_info: Optional[level_info]
    pendant: Optional[pendant]
    card: Optional[inofcard]
    vip: Optional[vip]


class desc(BaseModel):
    type: int
    timestamp: int
    view: int
    orig_dy_id: Optional[int] = None
    orig_type: int
    user_profile: user_profile
    dynamic_id: int


class topic_details(BaseModel):
    topic_name: str
    is_activity: bool

# emoji 信息


class emoji_details(BaseModel):
    emoji_name: str
    id: int
    text: str
    url: str


class Topic_info(BaseModel):
    topic_details: List[topic_details]


class Emoji_details(BaseModel):
    emoji_details: List[emoji_details]


class at_control(BaseModel):
    data: int
    length: int
    location: int
    type: int


class pictures(BaseModel):
    img_src: str
    img_height: int
    img_width: int


class DynamicItem(BaseModel):
    at_control: Optional[Union[Json, str]] = None
    description: Optional[str] = None
    upload_time: Optional[int] = None
    content: Optional[str] = None
    ctrl: Optional[Union[Json, str]] = None
    pictures: Optional[Union[str, List[pictures]]]


class vest(BaseModel):
    content: str


class apiSeasonInfo(BaseModel):
    title: Optional[str]
    type_name: str


class Dynamic(BaseModel):
    item: Optional[DynamicItem] = None
    dynamic: Optional[str] = None
    pic: Optional[str] = None
    title: Optional[str] = None
    origin: Optional[Json] = None
    image_urls: Optional[List] = None
    summary: Optional[str] = None
    vest: Optional[vest]
    origin_user: Optional[user_profile] = None

    duration: Optional[int] = None

    user: Optional[info]
    owner: Optional[info]
    author: Optional[info]

    cover: Optional[str] = None
    area_v2_name: Optional[str] = None

    apiSeasonInfo: Optional[apiSeasonInfo]

    new_desc: Optional[str] = None


class desc_first(BaseModel):
    text: str


class reserve_attach_card(BaseModel):
    title: str
    desc_first: Optional[Union[str, desc_first]]
    desc_second: Optional[str]
    cover_url: Optional[str]
    head_text: Optional[str]


class add_on_card_info(BaseModel):
    add_on_card_show_type: int
    reserve_attach_card: Optional[reserve_attach_card]
    vote_card: Optional[Json]
    attach_card: Optional[reserve_attach_card]


class Display(BaseModel):
    topic_info: Optional[Topic_info] = None
    emoji_info: Optional[Emoji_details] = None
    add_on_card_info: Optional[List[add_on_card_info]]
    origin: Optional[dict]


class DynamicCard(BaseModel):
    """
    详细信息的card
        :desc 动态基本信息
        :card 动态的内容
    """
    desc: Optional[desc]
    card: Json[Dynamic]
    display: Display


class DynamicData(BaseModel):
    """动态详细信息data"""
    card: DynamicCard


class DynamicDetail(BaseModel):
    """动态详细信息接口返回"""
    code: int
    data: DynamicData

class division(BaseModel):
    data: Union[Json, None]
    start: int
    end: int
    len: int
    type: int


