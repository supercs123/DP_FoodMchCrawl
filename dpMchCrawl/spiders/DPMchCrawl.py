import scrapy
from dpMchCrawl.items import DpmchcrawlItem 

class DPMchSpider(scrapy.Spider):
    name = "dpMchCrawl"
    
    def start_requests(self):
        urls = ["http://www.dianping.com/shanghai/ch10/g219r811o3",
                "http://www.dianping.com/shanghai/ch10/g102r811o3"]
        headers={'User-Agent':'Mozilla/5.0(Windows NT 6.1;WOW64)AppleWebKit/537.36(KHTML,like Gecko Chrome/46.0.2490.86 Safari/537.36',
        'Cookie':'_hc.v="\"beb15290-2bc8-452c-ab2d-a1d1f7f96f95.1476797445\""; \
        __utma=1.1972886557.1483260919.1490016662.1490970687.8; \
        _lxsdk_cuid=15ea4ac73ccc8-0ce33493b6de0d-e313761-100200-15ea4ac73ccc8; \
        _lxsdk=15ea4ac73ccc8-0ce33493b6de0d-e313761-100200-15ea4ac73ccc8; \
        s_ViewType=10; aburl=1; _tr.u=IQOYcZcFkVNgF1sD; \
        dper=b04546a7f9ba1c1c2a703311e3f57e88e36444c34796285b652ccfa529dbc92e; \
        ll=7fd06e815b796be3df069dec7836c3df; ua=supercs123; \
        ctu=34430638c3fbc59558454073183ed838bd76200ecf6a49b8d63e4295ffe6b18c; \
        uamo=13641731392; Hm_lvt_185e211f4a5af52aaffe6d9c1a2737f4=1521340006,1521341246,1521342682,1521349647;\
        Hm_lpvt_185e211f4a5af52aaffe6d9c1a2737f4=1521350665; tg_list_scroll=313; \
        JSESSIONID=2793719CCBC84ED2F831B828C4D051F5'}

        for url in urls:
            yield scrapy.Request(url=url,callback= self.parse,headers = headers)

    def parse(self,response):
        item = DpmchcrawlItem() 
        for mchInfo in response.xpath('//div[@id="shop-all-list"]/ul/li'):
            item["mchName"] = mchInfo.xpath('div[2]/div[1]/a/h4/text()').extract_first().encode('utf-8'),
            item["mchStars"] = mchInfo.xpath('div[2]/div[2]/span/@title').extract_first(default='-1').encode('utf-8'),
            item["commts"] = mchInfo.xpath('div[2]/div[2]/a[1]/b/text()').extract_first(default='-1').encode('utf-8')
            item["avgPrice"] = mchInfo.xpath('div[2]/div[2]/a[2]/b/text()').extract_first(default = '-1').encode('utf-8')
        
