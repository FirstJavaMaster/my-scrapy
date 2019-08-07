import datetime

import scrapy
from scrapy import Request

from myScrapy.items import ImageItem
from myScrapy.utils import BS4Utils
from myScrapy.utils.ImageGroupUtils import ImageGroupUtils
from myScrapy.utils.ProgressUtils import ProgressUtils


class ACG12(scrapy.Spider):
    name = "acg-12"
    allow_domains = ["acg12.com"]
    # 各个板块的url,目前包括(动漫图集,图站精选,绅士道,在线图集)
    start_urls = ['https://acg12.com/category/acg-gallery/',
                  'https://acg12.com/category/pixiv/',
                  'https://acg12.com/category/hentai-dou/',
                  'https://acg12.com/category/online-atlas/']

    image_group_utils = ImageGroupUtils(name)
    progress_utils = ProgressUtils()

    # 需要跳过的分类
    error_category_list = ['【搜狗输入法皮肤】', '【站务消息】', '【LOL萌化】', '【教程】', '【表情包】', '【动漫表情】',
                           '【动漫头像】', '【情侣头像】', '【萌化软件】', '【无损音乐】', '【喵热点】', '【破事水】',
                           '【二次表情】', '【四格漫画】', '【萌化】', '【萌化教程】']
    # 用于判断时间,超过1个月的不再爬取
    limit_time = (datetime.datetime.now() + datetime.timedelta(days=-30)).strftime('%Y-%m-%d %H:%M:%S')

    def parse(self, response):
        soup = BS4Utils.get_soup(response)
        group_div_list = soup.find('div', class_='inn-archive__container').find_all('article')
        print('进入第%s页, 发现%s组图片' % (self.get_url_last_part(response.url), len(group_div_list)))

        for group_div in group_div_list:
            # 图组名称和链接
            a_div = group_div.find('h3', class_='inn-archive__item__title').find('a')
            title = a_div.get_text()
            href = a_div['href']

            # 图组类型
            error_category_flag = False
            for error_category in self.error_category_list:
                if error_category in title:
                    error_category_flag = True
                    break
            if error_category_flag:
                print('跳过不合格图组: %s' % title)
                continue

            # 图组时间
            group_time = group_div.find('time', class_='inn-archive__item__meta__date')['title']
            if group_time < self.limit_time:
                print('该图组时间为 %s, 后面的将不再爬取 >> %s' % (group_time, title))
                return

            group_code = self.get_url_last_part(href)
            group_is_done = self.image_group_utils.group_is_done(group_code)
            if group_is_done:
                print('跳过已完成图组 >> %s' % title)
            else:
                # 代码进行到这里,说明此图组加入爬取任务
                self.progress_utils.add_task()
                group_name = self.image_group_utils.get_group_name(group_code, title)
                yield Request(href, meta=ImageGroupUtils.create_meta_data(group_code, group_name), callback=self.parse2)

        # 处理下一页
        next_page_div = soup.find('a', class_='poi-pager__item_next', title='下一页')
        if next_page_div is not None:
            next_page_href = next_page_div['href']
            print('进入下一页-> ', next_page_href)
            yield Request(next_page_href)

    def parse2(self, response):
        soup = BS4Utils.get_soup(response)
        group_code = response.meta['group_code']
        group_name = response.meta['group_name']

        image_div_list = soup.find('article', class_='inn-singular__post') \
            .find('div', class_='inn-singular__post__body').find('div', class_='inn-singular__post__body__content') \
            .find_all('img')

        if len(image_div_list) == 0:
            self.progress_utils.task_complete('图组 %s 中图片数量为0,跳过该图组' % group_name)
            return

        print('下载图组 %s >> 共 %s 张图片保存中...' % (group_name, len(image_div_list)))
        # 组装图片url数据
        image_item = ImageItem()
        image_item['image_group_utils'] = self.image_group_utils
        image_item['image_group_url'] = response.url
        image_item['image_group_name'] = group_name
        image_item['image_urls'] = []
        for image_div in image_div_list:
            src = image_div.get('src')
            image_item['image_urls'].append(src)
        yield image_item

    @staticmethod
    def get_url_last_part(url):
        items = url.split(r'/')
        while '' in items:
            items.remove('')
        return items[-1]
