import os
import re

import requests
from fake_useragent import UserAgent

from myScrapy import settings
from myScrapy.utils.IOUtils import IOUtils


class ImageGroupUtils:
    __home_dir__ = settings.IMAGES_STORE
    __done_sign__ = settings.IMAGES_GROUP_DONE_SIGN

    def __init__(self, spider_dir_name):
        if not spider_dir_name:
            raise RuntimeError('必须指定图组名称')

        # 准备好爬虫目录
        self.spider_dir = IOUtils.merge_dir(self.__home_dir__, spider_dir_name)
        IOUtils.create_dir_force(self.spider_dir)
        # 创建目录缓存
        self.path_cache = PathCacheUtils(self.spider_dir)

    # 组装图组名称
    @staticmethod
    def get_group_name(group_code, group_title):
        if not group_code or not group_title:
            raise RuntimeError('图组编号或图组标题缺失')
        # 去除特殊字符后,截取前200位,并去除空格
        group_title = re.sub(r'[\\/:*?"<>|\r\n.]', '-', group_title)[:100].strip()
        return '(%s)%s' % (group_code, group_title)

    @staticmethod
    def get_group_code_and_title(group_name):
        reg_result = re.findall(r'\((\d+)\)(.+)', group_name)
        if len(reg_result) == 0:
            raise RuntimeError('无法解析出group_code和group_name: ' + group_name)
        return reg_result[0]

    # 创建图组目录.同时保存超链接
    def create_group_dir(self, group_name, group_url):
        group_code = self.get_group_code_and_title(group_name)[0]
        group_dir = self.path_cache.get_path(group_code)
        if group_dir is not None:
            return group_dir

        # 创建目录
        group_dir = IOUtils.merge_dir(self.spider_dir, group_name)
        IOUtils.create_dir_force(group_dir)
        self.path_cache.add_cache(group_name)
        # 保存超链接
        self.save_url_link(group_dir, group_url)
        return group_dir

    # 删除图组目录
    def remove_group_path(self, group_code):
        group_path = self.path_cache.get_path(group_code)
        IOUtils.remove_dir(group_path)

    # 保存图片
    def save(self, group_code, image_name, image_url):
        group_path = self.path_cache.get_path(group_code)
        image_path = IOUtils.merge_dir(group_path, image_name)

        headers = {'user-agent': UserAgent().random}
        response = requests.get(image_url, stream=True, headers=headers)
        status_code = response.status_code
        if 200 != status_code:
            raise RuntimeError('请求异常(%s): %s' % (status_code, image_url))
        with open(image_path, 'wb') as file:
            file.write(response.content)

    # 图组添加已完成标志
    def group_done(self, group_code):
        old_path = self.path_cache.get_path(group_code)
        if not old_path:
            raise RuntimeError('图组不存在')
        group_name = old_path.split(r'/')[-1]
        new_path = IOUtils.merge_dir(self.spider_dir, self.__done_sign__ + group_name)
        os.rename(old_path, new_path)
        print('图组保存完成 >>> %s' % group_name)

    # 根据标志判断图组是否已完成
    def group_is_done(self, group_code):
        group_path = self.path_cache.get_path(group_code)
        if group_path:
            return self.__done_sign__ in group_path
        else:
            return False

    # 将图组的访问url放入文件夹
    @staticmethod
    def save_url_link(group_dir, url):
        file_path = group_dir + '/target.url'
        if os.path.isfile(file_path):
            return

        with open(file_path, 'w') as file:
            file.write('[{000214A0-0000-0000-C000-000000000046}]\n')
            file.write('Prop3=19,11\n')
            file.write('[InternetShortcut]\n')
            file.write('IDList=\n')
            file.write('URL=' + url + '\n')

    @staticmethod
    def create_meta_data(group_code, group_name):
        return {'group_code': group_code, 'group_name': group_name}


class PathCacheUtils:
    def __init__(self, spider_path):
        self.spider_path = spider_path

        self.cache_list = {}
        for group_name in os.listdir(self.spider_path):
            self.add_cache(group_name)

    def add_cache(self, group_name):
        group_code = ImageGroupUtils.get_group_code_and_title(group_name)[0]
        self.cache_list[group_code] = IOUtils.merge_dir(self.spider_path, group_name)

    def get_path(self, group_code):
        path = self.cache_list.get(group_code, None)
        if path is None:
            path = self.__get_path_from_disk__(group_code)
        # 将发现的路径放入缓存,并返回
        self.cache_list[group_code] = path
        return path

    # 遍历文件夹获取图组绝对路径
    def __get_path_from_disk__(self, group_code):
        sign = '(%s)' % group_code
        for dir_name in os.listdir(self.spider_path):
            if sign in dir_name:
                return IOUtils.merge_dir(self.spider_path, dir_name)
        return None
