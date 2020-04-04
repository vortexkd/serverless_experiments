import scrapy



class HomePageFinder(scrapy.Spider):

    google_url = "https://www.google.co.jp/search?hl=ja&{}"
    bing_url = "https://www.bing.com/search?{}&setlang=ja-jp"

    def __init__(self, **kwargs):
        super(HomePageFinder, self).__init__(**kwargs)

    def start_requests(self):
        pass

    def parse(self, response):
        pass