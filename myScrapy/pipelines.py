# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re

import scrapy
from scrapy.pipelines.images import ImagesPipeline

from myScrapy import settings
from myScrapy.utils.IOUtils import IOUtils


class MyscrapyPipeline(object):
    def process_item(self, item, spider):
        return item


class MyImagesPipeline(ImagesPipeline):
    # 从项目设置文件中导入图片下载路径
    img_store = settings.IMAGES_STORE

    # 组装图片下载请求
    # 提供URL的格式化处理
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            # 判断url正确性
            if not self.is_right_image_url(image_url):
                continue
            # 处理url
            image_url = self.fix_url(image_url)
            # 返回请求
            yield scrapy.Request(image_url, meta={'item': item})

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        image_group_url = item['image_group_url']
        image_group_utils = item['image_group_utils']
        group_name = item['image_group_name']

        # 创建图组目录(如果已经存在不会重复创建)
        group_dir = image_group_utils.create_group_dir(group_name, image_group_url)
        # 获取到爬虫根目录后的相对路径
        reg_result = re.findall(r'^' + self.img_store + r'[\\/](.+)$', group_dir)
        if len(reg_result) == 0:
            raise RuntimeError('相对路径获取失败')
        relative_dir = reg_result[0]
        # 图片名
        image_name = self.get_image_name(request.url)
        # 图片地址
        return IOUtils.merge_dir(relative_dir, image_name)

    # 重写item_completed方法
    # 将图组标记为已完成
    def item_completed(self, results, item, info):
        image_group_utils = item['image_group_utils']
        image_group_name = item['image_group_name']
        group_code = image_group_utils.get_group_code_and_title(image_group_name)[0]
        image_group_utils.group_done(group_code)
        return item

    @staticmethod
    def is_right_image_url(url):
        if not url:
            return False
        wrong_value_list = ['file://', 'data:']
        for wrong_value in wrong_value_list:
            if url.startswith(wrong_value):
                return False
        return True

    @staticmethod
    def fix_url(url):
        # 补充协议
        if url.startswith(r'//'):
            url = 'https:' + url

        # 去除长宽限定参数
        return re.sub(r'-\d+x\d+\.', r'.', url)

    @staticmethod
    def get_image_name(image_url):
        last_part = image_url.split(r'/')[-1]
        if r'.' not in last_part:
            last_part = last_part + '.jpg'
        return last_part
