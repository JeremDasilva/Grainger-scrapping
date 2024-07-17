import scrapy

class MyspiderSpider(scrapy.Spider):
    name = "myspider"
    allowed_domains = ["www.grainger.com"]
    start_urls = ["https://www.grainger.com/category"] #Starting point in order to make the testing faster

    def parse(self, response):
        links = response.css('a.BQOwdV')
        
        if len(links) > 0: #We look on the page and if we find href. If yes we keep going deeper in the website, if not we yield the url in a json file called urls (see settings)
            for link in links:
                absolute_next_page_url = 'https://www.grainger.com' + link.attrib.get('href')
                yield scrapy.Request(absolute_next_page_url, callback=self.parse)
        else:
            yield {
                'url': response.url 
            }

