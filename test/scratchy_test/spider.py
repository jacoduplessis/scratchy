from scrapy import Spider


class TestSpider(Spider):
    name = 'test'

    start_urls = [
        'http://localhost:9009/',
    ]

    def parse(self, response):
        for href in response.css('a::attr(href)'):
            yield response.follow(href, callback=self.parse_detail)

    def parse_detail(self, response):
        title = response.css('h1::text').get()
        content = response.css('.content::text').get()

        yield dict(title=title, content=content)
