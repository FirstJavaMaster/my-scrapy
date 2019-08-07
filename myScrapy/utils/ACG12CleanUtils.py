import hashlib
import shutil

from myScrapy.spiders.ACG12 import ACG12
from myScrapy.utils.IOUtils import IOUtils
from myScrapy.utils.imageUtils import *

path = r'E:\my-spider-data\acg-12'


def get_md5(file_path):
    with open(file_path, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()


def have_good_file(group_path):
    bad_md5_list = ['7e80fb31ec58b1ca2fb3548480e1b95e', '4cf24fe8401f7ab2eba2c6cb82dffb0e']
    for file_name in os.listdir(group_path):
        if file_name == 'target.url':
            continue

        file_path = IOUtils.merge_dir(group_path, file_name)

        # 判断md5和图片质量
        if (get_md5(file_path) not in bad_md5_list) and (is_good_image(file_path)):
            return True

    return False


def have_big_file(group_path):
    for file_name in os.listdir(group_path):
        file_path = IOUtils.merge_dir(group_path, file_name)
        size = os.path.getsize(file_path)
        if size > 50 * 1000:
            return True
    return False


def is_error_category(group_name):
    for error_category in ACG12.error_category_list:
        if error_category in group_name:
            return True
    return False


def remove(reason, group_path):
    print('删除 [%s] : %s' % (reason, group_path))
    shutil.rmtree(group_path)

    # new_group_path = group_path.replace('acg-12', 'acg-12-bak', 1)
    # shutil.move(group_path, new_group_path)
    pass


def runner():
    group_name_list = os.listdir(path)
    group_name_length = len(group_name_list)
    finish_count = 0
    for group_name in group_name_list:
        group_path = IOUtils.merge_dir(path, group_name)

        if is_error_category(group_name):
            remove('无用分类', group_path)
        elif not have_big_file(group_path):
            remove('小文件', group_path)
        elif not have_good_file(group_path):
            remove('低质量', group_path)

        finish_count = finish_count + 1
        print('\r[ %s / %s ] %s >> ' % (finish_count, group_name_length, group_name), end='', flush=True)
    print('运行结束')


runner()
