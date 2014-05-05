from scrapy.item import Item, Field

class Places(Item):
    # attributes
    nameOnSite = Field()        # the name of region available on site
    name = Field()              # the real name of the region
    category = Field()          # the category which the region belongs to
    descriptions = Field()      # descriptions about the region
    likesNum = Field()          # number of facebook likes