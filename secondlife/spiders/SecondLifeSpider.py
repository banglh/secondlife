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

class SecondLifeSpider(CrawlSpider):
    # name of spider
    name = 'Second Life Spider'
    allowed_domains = ["secondlife.com"]
    start_urls = ["http://secondlife.com/destinations/"]
    
    # rules for extracting links and contents
    rules = (# rule for pattern A
             Rule(SgmlLinkExtractor(allow = ('destinations\/?'), deny = ('destinations\/.'), callback = 'parseAType')),
             # rule for pattern B
             Rule(SgmlLinkExtractor(allow = ('destinations\/.+\/?'), deny = ('destinations\/.+\/.'), callback = 'parseBType')),
             # rule for pattern C
             Rule(SgmlLinkExtractor(allow = ('destinations\/.+\/.+\/?'), deny = ('destinations\/.+\/.+\/.'), callback = 'parseCType')),
             # rule for pattern D
             Rule(SgmlLinkExtractor(allow = ('destinations\/.+\/[0-9]\/?'), callback = 'parseDEType')),
             # rule for pattern E
             Rule(SgmlLinkExtractor(allow = ('destinations\/.+\/.+\/[0-9]\/?'), callback = 'parseDEType')),
             # rule for pattern F
             Rule(SgmlLinkExtractor(allow = ('destination\/.+'), callback = 'parseEType')))
    
    # parser for pattern a
    def parseAType(self, response):
        sel = Selector(response)
        domain = 'http://secondlife.com'
        # extract b
        categoriesLinks = sel.xpath('//ul[@class="menu_sidebar2"]/li/a/@href').extract()
        
        # generate requests to follow b
        categoriesRequests = []
        for branch in categoriesLinks:
            request = Request(url = domain + branch)
            categoriesRequests.append(request)
            
        return categoriesRequests
    
    # parser for pattern b
    def parseBType(self, response):
        # CASE 1: the category doesn't have subcategories  --> extract and follow d,e
        sel = Selector(response)
        domain = 'http://secondlife.com'
        requestList = []
        
        # try to extract d, e
        destList = sel.xpath('//div[@class="dg-catterm-list-desc"]/h3/a/@href').extract()
        if (len(destList) > 0):
            for destPath in destList:
                request = Request(url = domain + destPath)
                requestList.append(request)
            
            # extract pagers if any (d)
            pages = sel.xpath('//span[@class="qp_counter"]')[0].xpath('a/@href').extract()
            for page in pages:
                request = Request(url = domain + page)
                requestList.append(request)
        # CASE 2: the category has subcategories    --> extract and follow c
        else:
            subList = sel.xpath('//div[@class="dg-cat-wsub-cat-head"]/h2/a/@href').extract()
            if (len(subList) > 0):
                for sub in subList:
                    request = Request(url = domain + sub)
                    requestList.append(request)
            
        return requestList
    
    # parser for pattern c
    def parseCType(self, response):
        sel = Selector(response)
        domain = 'http://secondlife.com'
        requestList = []
        
        # extract d,e
        destList = sel.xpath('//div[@class="dg-catterm-list-desc"]/h3/a/@href').extract()
        if (len(destList) > 0):
            for destPath in destList:
                request = Request(url = domain + destPath)
                requestList.append(request)
            
            # extract pagers if any (d)
            pages = sel.xpath('//span[@class="qp_counter"]')[0].xpath('a/@href').extract()
            for page in pages:
                request = Request(url = domain + page)
                requestList.append(request)
                
        return requestList
    
    # parser for pattern d
    def parseDEType(self, response):
        sel = Selector(response)
        domain = 'http://secondlife.com'
        requestList = []
        
        # extract f
        destList = sel.xpath('//div[@class="dg-catterm-list-desc"]/h3/a/@href').extract()
        if (len(destList) > 0):
            for destPath in destList:
                request = Request(url = domain + destPath)
                requestList.append(request)
            
        return requestList
    
    # parser for pattern f
    def parseEType(self, response):
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
        region['description'] = descriptions
        
        # likeNum
        region['likeNum'] = 0
        
        return region