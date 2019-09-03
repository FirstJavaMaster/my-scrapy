from scrapy.crawler import CrawlerProcess
from scrapy.utils import project

from myScrapy.spiders.ACG12 import ACG12
from myScrapy.spiders.QiWenBeauty import QiWenBeauty

spiders = {
    QiWenBeauty.name: True,
    ACG12.name: True
}

if __name__ == '__main__':
    setting = project.get_project_settings()
    process = CrawlerProcess(setting)

    for spider_name in process.spiders.list():
        if spiders.get(spider_name):
            print("启动爬虫 >>> %s <<<" % spider_name)
            process.crawl(spider_name)
    process.start()
