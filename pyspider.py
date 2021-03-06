from pyspider.libs.base_handler import *
import pymongo


class Handler(BaseHandler):
    crawl_config = {
        'headers':{
        'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
        }
    }
    client=pymongo.MongoClient('localhost')
    db=client['qunar']

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://travel.qunar.com/travelbook/list.htm?order=hot_heat', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('li > .tit > a').items():
            #frtch_type='js'就是启动phantomjs的意思
            self.crawl(each.attr.href, callback=self.detail_page,fetch_type='js')
        next=response.doc('.next').attr.href
        self.crawl(next,callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('#booktitle').text(),
            'date':response.doc('.when .data').text(),
            'day':response.doc('.howlong ,data').text(),
            'who':response.doc('.who .data').text(),
            'text':response.doc("#b_panel_schedule").text(),
            'image':response.doc('.cover_img').attr.src

        }
    def on_result(self,result):
        if result:
            self.save_to_mongo(result)
    def save_to_mongo(self,result):
        if self.db['nihao'].insert(result):
            print(result)