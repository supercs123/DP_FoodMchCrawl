# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DpmchcrawlItem(scrapy.Item):
    # define the fields for your item here like:
#    cityNm = scrapy.Field()
    mchName = scrapy.Field()
    mchStars = scrapy.Field()
    commts = scrapy.Field()
    avgPrice = scrapy.Field()
    taste = scrapy.Field()
    environ = scrapy.Field()
    service = scrapy.Field()
    foodTyp = scrapy.Field()
    region = scrapy.Field()
    addrs = scrapy.Field()
