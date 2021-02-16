import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hoaresbank.items import Article


class HoaresSpider(scrapy.Spider):
    name = 'hoares'
    start_urls = ['https://www.hoaresbank.co.uk/news']

    def parse(self, response):
        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="field-item even"]/h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="date-display-single"]/@content').get()
        if date:
            date = datetime.strptime(date.strip(), '%Y-%m-%dT00:00:00+%H:00')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="group-header"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
