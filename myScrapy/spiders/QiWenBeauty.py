from urllib import parse

import scrapy
from scrapy import Request

from myScrapy.utils import BS4Utils
from myScrapy.utils.ImageGroupUtils import ImageGroupUtils
from myScrapy.utils.ProgressUtils import ProgressUtils


class QiWenBeauty(scrapy.Spider):
    name = "qi-wen-beauty"
    allow_domains = ["qiwen007.com"]
    start_urls = ['http://www.qiwen007.com/mb-db/qingchun/']

    image_file_utils = ImageGroupUtils(name)
    progress_utils = ProgressUtils()

    def parse(self, response):
        soup = BS4Utils.get_soup(response)

        # 尝试获取分页元素
        page_div = soup.find(class_='PGDIV')
        if page_div is None:
            print('已到最后一页, 爬虫结束!')
            return

        page_number = page_div.find(class_='PGThis').get_text()

        # 获取当前页的图组列表
        item_list = soup.find(id="pubu_id").find_all(class_="w")
        item_number = len(item_list)
        self.progress_utils.add_task(item_number)
        print('进入第%s页, 发现%s组图片' % (page_number, item_number))

        # 循环判断每组图片
        for item in item_list:
            a_div = item.find(class_="bt").find('a')
            title = a_div.get_text()
            href = parse.urljoin(response.url, a_div['href'])
            group_code = self.get_group_code(href)
            # 判断图组是否已完成
            group_is_done = self.image_file_utils.group_is_done(group_code)
            if group_is_done:
                self.progress_utils.task_complete('跳过已完成图组:' + title)
            else:
                group_name = self.image_file_utils.get_group_name(group_code, title)
                self.image_file_utils.create_group_dir(group_name, href)
                yield Request(href, meta=ImageGroupUtils.create_meta_data(group_code, group_name), callback=self.parse2)

        # 下一页
        next_page_href = page_div.find(class_='pageNext')['href']
        next_page_url = parse.urljoin(response.url, next_page_href)
        if next_page_url.endswith(r'.html'):
            yield Request(next_page_url)

    def parse2(self, response):
        soup = BS4Utils.get_soup(response)
        group_code = response.meta['group_code']
        group_name = response.meta['group_name']

        # 获得图片名,图片完整保存路径
        image_src = soup.find(class_="article-body").find(class_='picimg').find("img")['src']
        image_name = image_src.split(r'/')[-1]

        # 组装图片完整url,下载
        image_url = parse.urljoin(response.url, image_src)
        # 保存图片(会自动创建图组目录)
        self.image_file_utils.save(group_code, image_name, image_url)
        print('保存图片-> %s >> %s >> %s' % (group_name, image_name, image_url))

        # 处理下一页
        next_page_div = soup.find('a', id='NY_XYY')
        if next_page_div is None:
            self.image_file_utils.group_done(group_code)
            self.progress_utils.task_complete('图组下载完成:' + group_name)
        else:
            next_page_url = parse.urljoin(response.url, next_page_div['href'])
            yield Request(next_page_url, meta=ImageGroupUtils.create_meta_data(group_code, group_name),
                          callback=self.parse2)

    # 获取图组编码
    @staticmethod
    def get_group_code(href):
        return href.split(r'/')[-1].split(r'.')[0].split(r'_')[0]
