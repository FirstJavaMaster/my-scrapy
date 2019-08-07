import os
import shutil


class IOUtils:
    # 强制创建文件夹,如果存在同名文件,则会将其重命名
    @staticmethod
    def create_dir_force(path):
        is_dir = os.path.isdir(path)
        # 如果文件夹已经存在,则直接返回
        if is_dir:
            return

        # 如果是文件,则重命名文件
        is_file = os.path.isfile(path)
        if is_file:
            os.rename(path, path + '_old')

        # 创建目录
        os.makedirs(path)
        pass

    # 组装path
    @staticmethod
    def merge_dir(parent_path, *children):
        result = parent_path.rstrip(r'/')
        for child in children:
            result = result + '/' + child
        return result

    @classmethod
    def remove_dir(cls, group_path):
        shutil.rmtree(group_path)
