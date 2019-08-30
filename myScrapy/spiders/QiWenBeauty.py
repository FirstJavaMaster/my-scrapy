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
        print('进入网站第 %s 页, 发现 %s 组图片' % (page_number, item_number))

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
                meta = {
                    'image_item': self.image_file_utils.get_init_image_item(href, group_name)
                }
                yield Request(href, meta=meta, callback=self.parse2)

        # 下一页
        next_page_href = page_div.find(class_='pageNext')['href']
        next_page_url = parse.urljoin(response.url, next_page_href)
        if next_page_url.endswith(r'.html'):
            yield Request(next_page_url)

    def parse2(self, response):
        soup = BS4Utils.get_soup(response)
        image_item = response.meta['image_item']
        group_name = image_item['image_group_name']

        # 获得图片名,图片完整保存路径
        image_src = soup.find(class_="article-body").find(class_='picimg').find("img")['src']

        # 组装图片完整url,下载
        image_url = parse.urljoin(response.url, image_src)
        image_item['image_urls'].append(image_url)
        print('解析图组第 %s 页 >>> %s' % (len(image_item['image_urls']), group_name))

        # 处理下一页
        next_page_div = soup.find('a', id='NY_XYY')
        if next_page_div is None:
            self.progress_utils.task_complete('图组解析完成, 图片下载中... >>>' + group_name)
            yield image_item
        else:
            next_page_url = parse.urljoin(response.url, next_page_div['href'])
            yield Request(next_page_url, meta=response.meta, callback=self.parse2)

    # 获取图组编码
    @staticmethod
    def get_group_code(href):
        return href.split(r'/')[-1].split(r'.')[0].split(r'_')[0]
