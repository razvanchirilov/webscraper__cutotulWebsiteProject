from scrapy import Spider
from scrapy.http import Request
from scrapy.loader import ItemLoader
from cutotulWebsite.items import CutotulwebsiteItem 
from scrapy.crawler import CrawlerProcess
import re
import csv
import glob
from openpyxl import Workbook
import os

class CutotulSpider(Spider):
    name = 'cutotul'
    allowed_domains = ['cutotul.ro']
    start_urls = ['https://cutotul.ro/3-karcher-aspiratoare-home-garden']                  
    
    def parse(self, response):
        #process product urls
        products_urls = response.xpath('//*[@itemprop="name"]/a/@href').extract()
        for url in products_urls:
            yield Request(url, callback=self.parse_product)
            
        #process next page
        next_page_url = response.xpath('//*[@class="pagination_next"]/a/@href').extract_first()
        absolute_next_page_url = response.urljoin(next_page_url)
        yield Request(absolute_next_page_url)    
            
    def parse_product(self, response):
        #download informations
        l = ItemLoader(item=CutotulwebsiteItem(), selector=response, response=response)
        l.add_xpath('TITLE', '//h1/text()')
        l.add_xpath('MODEL', '//*[@itemprop="sku"]/text()')
        l.add_xpath('CONDITION', '//*[@id="product_condition"]/span/text()')
        l.add_xpath('DESCRIPTION', '//div[@id="short_description_content"]//p//text() | //div[@id="short_description_content"]/div/text()')               
        l.add_xpath('PRICE', '//*[@itemprop="price"]/text()')
        l.add_xpath('STATUS', '//*[@class="available-now"]/text()[2] | //*[@id="availability_statut"]/span/text() ')
        
        #process availability_status
        product_availability_status = response.xpath('//*[@class="available-now"]/text()[2]')
        # cleaned_status_list = [x.get().replace('\n', '').replace('\t', '').strip() for x in product_availability_status if x.get().strip()]
        availability_status = ''.join(str(status) for status in product_availability_status)
        l.add_xpath('AVAILABILITY_STATUS', availability_status)
        
        #process price_list
        product_list_price_xpath = response.xpath("/html/body/script/text()").re(r'getKarcherPriceNou.*;')
        price_list_extracted = []        
        for string in product_list_price_xpath:
            search_string = string
            regex = "\\d{1,}"
            result_search = re.findall(regex, search_string)
            price_list_extracted.append(result_search[0])
            
        price_list = ''.join(str(price) for price in price_list_extracted)
        l.add_xpath('PRICE_LIST', price_list)
        
        yield l.load_item()          
        
    def close(self, reason):
        csv_files = list(glob.iglob('*.csv'))
        print(csv_files)
        if not csv_files:
            print("No CSV files found")
        else:
            csv_file = max(csv_files, key=os.path.getctime)
        wb = Workbook()
        ws = wb.active
        
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            for row in csv.reader(f):
                ws.append(row)
                
        xlsx_file = csv_file.replace('.csv', '') + '.xlsx'
        wb.save(xlsx_file)
        wb.close()


 # main driver
if __name__ == "__main__":
    # run scraper
    process = CrawlerProcess()
    process.crawl(CutotulSpider)
    process.start()