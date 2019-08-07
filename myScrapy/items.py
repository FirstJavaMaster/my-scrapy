# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MyscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ImageItem(scrapy.Item):
    # 工具类,用于创建文件夹等操作
    image_group_utils = scrapy.Field()
    # 图组页面url,用于创建超链接
    image_group_url = scrapy.Field()

    # 图组名称
    image_group_name = scrapy.Field()
    # 图片url列表
    image_urls = scrapy.Field()
