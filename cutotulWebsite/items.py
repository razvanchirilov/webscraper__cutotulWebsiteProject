# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from price_parser import Price 
from itemloaders.processors import TakeFirst, MapCompose

def remove_lei(value):
    return value.replace("lei", '').strip()

# def get_price(price_raw):
#     price_object = Price.fromstring(price_raw)
#     return price_object.amount_float

# def get_currency(price_raw):
#     price_object = Price.fromstring(price_raw)
#     return price_object.currency

class CutotulwebsiteItem(scrapy.Item):
    # define the fields for your item here like:
    TITLE = scrapy.Field(output_processor=TakeFirst())
    MODEL = scrapy.Field(output_processor=TakeFirst())
    CONDITION = scrapy.Field(default=0,output_processor=TakeFirst())
    DESCRIPTION = scrapy.Field()
    STATUS = scrapy.Field(default=0,output_processor=TakeFirst())
    PRICE = scrapy.Field(default=0,output_processor=TakeFirst(), input_processor=MapCompose(remove_lei))
    PRICE_LIST = scrapy.Field(default=0, output_processor=TakeFirst())

    
