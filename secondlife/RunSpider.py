from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from secondlife.spiders.SecondLifeSpider import SecondLifeSpider
from scrapy.utils.project import get_project_settings

# # create new spider
# spider = SecondLifeSpider()
# 
# # get settings
# settings = get_project_settings()
# crawler = Crawler(settings)
# crawler.signals.connect(reactor.stop, signal = signals.spider_closed)
# crawler.configure()
# crawler.crawl(spider)
# crawler.start()
# log.start()
# reactor.run()