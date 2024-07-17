import scrapy
import datetime
import json

class MySpider(scrapy.Spider):
    name = 'my_spider_scraper'

    with open('urls.json', 'r') as file:
        datas = json.load(file)

    urls_to_scrap = []
    
    for data in datas:
        for key, value in data.items():
            urls_to_scrap.append(value)

    def parse(self, response):
        # Extracting the main title of the page
        title_page = response.css('.Gb4id::text').get()

        # Dictionary to store scraped data
        page_dict = {title_page: {}}

        # Extracting sections
        sections = response.css('.MAcbb-')

        for section in sections:
            title_section = section.css('.sC0Aof::text').get()
            sub_section_dict = {}

            # Extracting sub-sections (assuming there are nested sections)
            sub_sections = section.css('.T8G8vu')

            for sub_section in sub_sections:
                title_sub_section = sub_section.css('.SQoGqa::text').get()

                # Handling table extraction
                feature_list = sub_section.css('.JxT10f::text').getall()
                tables = sub_section.css('.cjpIYY tr')

                feature_dict = {feature: [] for feature in feature_list}

                # Adding the date of scraping
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")

                for row in tables:
                    for i, feature in enumerate(feature_list):
                        value = row.xpath(f'./td[{i+1}]/text()').get()
                        feature_dict[feature].append(value)
                        feature_dict['Date'].append(current_date)

                sub_section_dict[title_sub_section] = feature_dict

            page_dict[title_section] = sub_section_dict

        yield page_dict
