# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2
from scrapy.exceptions import DropItem

class RegionPipeline(object):
    
    def __init__(self):
        self.regions_seen = set()
    
    def process_item(self, item, spider):
        # check for duplication
        if item['nameOnSite'] in self.regions_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.regions_seen.add(item['nameOnSite'])
        
        # process region name
        item['name'] = urllib2.unquote(item['name'])
        
        # process category name (pattern: '/destinations/category[/subcategory]')
        item['category'] = item['category'][14:]
        
        # process raw description (pattern: '\n\t\n..\t [description content]\n\t\n...\t')
        item['descriptions'] = item['descriptions'].replace('\n', '').replace('\t', '')
        
        return item
