import scrapy
"""
How To Start:
Go to the top of the directory, type "scrapy crawl job" to start the spider
scrapy crawl job -o url.json

"""
class MySpider(scrapy.Spider):
    name = "job"

    def start_requests(self):
        # runs the requests asynchronously, doesn't wait for the request to finish 
        # must return an iterable of Requests (you can return a list of requests or write a generator function) 
        # which the Spider will begin to crawl from. 
        # Subsequent requests will be generated successively from these initial requests.
        #Query Parameters
        KeyWord = "Backend Engineer"
        YoE = 1
        page_num = 50
        for num in range(page_num):
            url = "https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword={}&jobcatExpansionType=0&area=6001001000&order=15&asc=0&page={}&jobexp={}&mode=s&jobsource=n_my104_search".format(KeyWord, str(num), str(YoE))
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #gets all valid jobs for a given url
        if response.css('p.b-tit').getall():
            #no results found
            return 
        for article in response.css('article'):
            res = article.css("a.js-job-link::attr(href)").getall()
            if not res or not res[0].startswith("//www.104.com.tw"):
                #skips empty urls and annomaly urls
                continue
            yield {
                'url': "https:" + res[0]
            }

    