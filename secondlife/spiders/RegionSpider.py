# patterns of extracted links
#     a. secondlife.com/destinations/                                    --> extract b --> follow b
#     b. secondlife.com/destinations/category_name/                      --> extract c or d,f --> follow c or d,f
#     c. secondlife.com/destinations/category_name/sub_category/         --> extract e,f --> follow e,f
#     d. secondlife.com/destinations/category_name/#number               --> extract f --> follow f
#     e. secondlife.com/destinations/category_name/sub_category/#number  --> extract f --> follow f
#     f. secondlife.com/destination/region_name                          --> get data

from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from secondlife.Places import Places

class RegionSpider(CrawlSpider):
    # spider name
    name = 'RegionSpider'
    allowed_domains = ["secondlife.com"]
    start_urls = ["http://secondlife.com/destinations"]
    
    # rules
    rules = (
#              Rule(SgmlLinkExtractor(allow = ('destinations\/?'), deny = ('destinations\/.'))),
             Rule(SgmlLinkExtractor(allow = ('destination\/.+\/?'), restrict_xpaths = ('//div[@class="dg-catterm-list-desc"]/h3/a'))
                  , callback = 'parseItems'),
             )
    
    def parse_start_url(self, response):
        sel = Selector(response)
        domain = 'http://secondlife.com'
        # extract b
        categoriesLinks = sel.xpath('//ul[@class="menu_sidebar2"]/li/a/@href').extract()
        
        # generate requests to follow b
        categoriesRequests = []
        for branch in categoriesLinks:
            request = Request(url = domain + branch, callback = self.parseBType)
            categoriesRequests.append(request)
            
        return categoriesRequests
    
    def parseBType(self, response):
        sel = Selector(response)
        domain = 'http://secondlife.com'
        requestList = []
        
        # CASE 1: the category doesn't have subcategories  --> extract and follow d,f
        # extract f
        destList = sel.xpath('//div[@class="dg-catterm-list-desc"]/h3/a/@href').extract()
        for destPath in destList:
            request = Request(url = domain + destPath, callback = self.parseItems)
            requestList.append(request)
                
        # extract d if any
        pages = sel.xpath('//span[@class="qp_counter"]')
        if (len(pages) > 0):
            pages = pages[0].xpath('a/@href').extract()
            
            for page in pages:
                request = Request(url = domain + page, callback = self.parseDEType)
                requestList.append(request)
            
        # CASE 2: the category has subcategories    --> extract and follow c
        subList = sel.xpath('//div[@class="dg-cat-wsub-cat-head"]/h2/a/@href').extract()
        if (len(subList) > 0):
            for sub in subList:
                request = Request(url = domain + sub, callback = self.parseCType)
                requestList.append(request)
            
        return requestList
    
    # parser for pattern c
    def parseCType(self, response):
#         from scrapy.shell import inspect_response
#         inspect_response(response)
        sel = Selector(response)
        domain = 'http://secondlife.com'
        requestList = []
        
        # extract f
        destList = sel.xpath('//div[@class="dg-catterm-list-desc"]/h3/a/@href').extract()
        if (len(destList) > 0):
            for destPath in destList:
                request = Request(url = domain + destPath, callback = self.parseItems)
                requestList.append(request)
            
        # extract pagers if any (d)
        pages = sel.xpath('//span[@class="qp_counter"]')
        if (len(pages) > 0):
            pages = pages[0].xpath('a/@href').extract()
            for page in pages:
                request = Request(url = domain + page, callback = self.parseDEType)
                requestList.append(request)
                
        return requestList
    
    # parser for pattern d,e
    def parseDEType(self, response):
        sel = Selector(response)
        domain = 'http://secondlife.com'
        requestList = []
        
        # extract f
        destList = sel.xpath('//div[@class="dg-catterm-list-desc"]/h3/a/@href').extract()
        for destPath in destList:
            request = Request(url = domain + destPath, callback = self.parseItems)
            requestList.append(request)
            
        return requestList
    
    def parseItems(self, response):
        
        # extract data
        sel = Selector(response)
        region = Places()
        
        # name on site
        region['nameOnSite'] = sel.xpath('//h1[@id="dg-title"]/text()').extract()[0]
        
        # name of region
        href = sel.xpath('//a[@class="HIGHLANDER_button_hot btn_md secondary btn-space"]/@href').extract()[0]
        rawName = href.split('/')[4]
        ## process rawName (optional)
        region['name'] = rawName
        
        # category
        rawCategory = sel.xpath('//div[@id="dg-breadcrumbs"]/a/@href').extract()[-1]
        ## process rawCategory (optional)
        region['category'] = rawCategory
        
        # descriptions
        descriptions = sel.xpath('//div[@id="dg-entry"]/p/text()')[1].extract()
        region['descriptions'] = descriptions
        
        # likeNum
        region['likesNum'] = 0
        
        return region