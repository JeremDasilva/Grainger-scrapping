import scrapy

class MyspiderSpider(scrapy.Spider):
    name = "myspider"
    allowed_domains = ["www.grainger.com"]
    start_urls = ["https://www.grainger.com/category/lighting/light-bulbs-lamps?categoryIndex=1"]

    def parse(self, response):
        links = response.css('a.BQOwdV')
        
        if len(links) > 0:
            for link in links:
                absolute_next_page_url = 'https://www.grainger.com' + link.attrib.get('href')
                yield scrapy.Request(absolute_next_page_url, callback=self.parse)
        else:
            yield {
                'url': response.url 
            }

