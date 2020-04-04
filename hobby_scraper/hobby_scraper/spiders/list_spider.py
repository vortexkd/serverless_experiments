import scrapy


class ListSpider(scrapy.Spider):
    name = "list-spider"
    start_urls = ["https://www.ts-hikaku.com/clist/a0/v1s22t0p.html"]

    def __init__(self, **kwargs):
        super(ListSpider, self).__init__(**kwargs)
        self.selector = '//a[@class="company-name"]'

    def parse(self, response: scrapy.http.Response):
        names = response.xpath(self.selector)
        for name in names:
            yield {'url': name.xpath('@href').get(),
                   'name': name.xpath('text()').get()}