# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re,time,random,urllib2,os,socket
from multiprocessing.dummy  import Pool

pool = Pool()

headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
    'Cookie':'navCtgScroll=0; showNav=#nav-tab|0|0; navCtgScroll=0; showNav=#nav-tab|0|0; _hc.v="\"28c48835-807a-422e-ba61-ad744498f777.1450593856\"";__utma=1.196682546.1450594182.1450594182.1452605452.2; __utmz=1.1452605452.2.2.utmcsr=gufensoso.com|utmccn=(referral)|utmcmd=referral|utmcct=/search/; PHOENIX_ID=0a018986-152531ce5a3-13cb4e7; s_ViewType=10; JSESSIONID=6FAF186D727AFC4CD60107EBA6D2D2D4; aburl=1; cy=1; cye=shanghai'}

#headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
#           'Cookie':'s_ViewType=10;Domain=.dianping.com;Expires=Mon, 17-Jul-2017 06:18:46 GMT;Path=/;JSESSIONID=DF651374389129A9149326BA93EABCA0;_hc.v="\"34fcfbbf-b319-4355-bdae-9112b3012952.1468736483\"";PHOENIX_ID=0a0303bc-155f781c895-1283432;='}
#proxies = ['http://121.69.33.158:8080',
#           'http://61.135.217.3:80',
#           'http://61.135.217.9:80',
#           'http://61.135.217.15:80',
#           'http://61.135.217.13:80',
#           'http://61.135.217.12:80',
#           'http://203.195.204.168:8080',
#           'http://61.135.217.10:80',
#           'http://61.135.217.16:80']
#

cityNm = '' #城市名全局变量
adminRegion_glb = ''   #行政区全局变量

def change_proxy():
    '''代理IP智能切换'''
    proxy =  random.choice(proxies)
    if proxy is None:
        proxy_support = urllib2.ProxyHandler({})
    else:
        proxy_support = urllib2.ProxyHandler({'http':proxy})
    opener = urllib2.build_opener(proxy_support,urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    print u'切换代理:%s'%(u'本机'if proxy is None else proxy)

def multiple_replace(text,adict):
    rx = re.compile('|'.join(map(re.escape,adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat,text)


def connect(url):
    '''网络请求连接并返回数据部分'''
    timeoutNo = 50
    maxTryNms = 3  #连接失败则反复尝试的最大次数 
    for tryTms in range(maxTryNms):
        try:
            print u'正在爬取%s'%url
            req = urllib2.Request(url,headers = headers)
            response = urllib2.urlopen(req,timeout = timeoutNo).read()
            return response
        except urllib2.URLError, e :  #处理URL连接错误  
            if tryTms <= maxTryNms-1:
                continue
            else:
                if hasattr(e,"reason"):
                    print u"错误原因：",e.reason
                    if re.match(r'.*11004.*',str(e.reason)):
                        print u'网络连接出错，请检查！！\n'
                        text = raw_input(u"是否继续[y/n]?")
                        if text.lower() == 'y':
                            continue  
                        else:
                            return None
                    else:
                        print u'%s爬取失败'%url
                        return None
        except:                     #处理其它类型的错误
            if tryTms <= maxTryNms-1:
                continue
            else:
                print u'%s爬取失败'%url
                return None
            
                              

def getRegionFoodType(url):
    '''根据选定行政区和菜系要求后的页面，得到该页面的页数，三者组合后得到所有URL地址，逐个传递给getMchinfo函数进行爬取'''
    global adminRegion_glb
    response = connect(url)
    if response is not None:
        datasoup = BeautifulSoup(response,"lxml")
        regionTags = datasoup.find('div',id="region-nav").find_all('a') #行政区代码
        foodTypeTags = datasoup.find('div',id = "classfy").find_all('a')  #菜系类型代码
        adminRegions = [re.search('[rc]\d+',region["href"]).group() for region in regionTags]  #得到行政区代码e.g. r5
        foodTyps = [re.search('g\d+',foodType["href"]).group() for foodType in foodTypeTags]  #得到菜系e.g. g105
        for foodtp in foodTyps:
			#foodTyp = re.search('g\d+',foodtp["href"]).group()
            for region in adminRegions:
                url_new = url+foodtp+region+'o3'   #菜系和行政区代码组合并按人气排序后的url
                response = connect(url_new)                                     #新url页面获得该类型下的页面数
                if response is not None:
                    '''首先将第一页的数据爬取下来，再根据得到的页码数，继续往下爬取'''
                    datasoup = BeautifulSoup(response,"lxml")
                    adminRegion_glb = datasoup.find('div',id = "region-nav").find('a',class_="cur").text.encode('utf-8')
                    #爬取第一页的商户信息
                    storeList = datasoup.find_all('div',class_="txt")
                    for store in storeList:
                        getStoreDetailInfo(store)
                    #得到接下来的页码数据
                    pageTags = datasoup.find('div',class_='page')
                    if pageTags is not None:
                        pageTagList = pageTags.find_all('a',class_='PageLink')
                        pageNum = [int(pgTag.text) for pgTag in pageTagList]   #得到所有页码
                        urlNew = [url_new+'p'+str(pgNo) for pgNo in range(2,max(pageNum)+1)]
                        fun = lambda urlnew: getMchInfo(urlnew)
                        pool.map(fun,urlNew)
                        #for pgNo in range(2,max(pageNum)+1):                #从2至最大页码生成页码表
                        #    urlNew = url+'p'+str(pgNo)                     #将页码组合进url,生成最后的爬取URL
                        #    getMchInfo(urlNew)                              #开始爬取页面商户信息                      
                else:
                    with open(os.getcwd()+'/'+'OriFailedPageUrl.txt','a') as fw:
                        fw.write(url+'\n')
                        
def getMchInfo(url):
    '''获取商户页信息'''
    global adminRegion_glb
    time.sleep(random.uniform(0.1,1))
    response = connect(url)
    if response is not None:
        datasoup = BeautifulSoup(response,"lxml")
        #获取当前行政区，并存入全局变量
        adminRegion_glb = datasoup.find('div',id = "region-nav").find('a',class_="cur").text.encode('utf-8')
        #爬取商户信息
        storeList = datasoup.find_all('div',class_="txt")
        for store in storeList:
            getStoreDetailInfo(store)
    else:
        with open(os.getcwd()+'/'+'SingleFailedPageUrl.txt','a') as fw:
            fw.write(url+'\n')

def getStoreDetailInfo(mcht):
    '''获取每个商户详细信息'''
    global cityNm,adminRegion_glb
    adict = {",":"^^",
             "，":"^^",
             "\\":"",
             "￥":""}

       #输出的保存文件名
    outFileName = 'store_merchants_info3.csv'
    name = mcht.find('div',class_='tit').find('a')['title'].encode('UTF-8') #商户名
    name = multiple_replace(name,adict)
    mch_id = mcht.find('div',class_= 'tit').find('a')['href']
    mch_id = re.search('\d+',mch_id).group().encode('UTF-8')
    levelFlag = mcht.find('span',class_="sml-rank-stars")    
    if levelFlag is not None:
        level = levelFlag['title'].encode('UTF-8')   #星级
        level = multiple_replace(level,adict)
    else:
        level = '-1'.encode('utf8')
    #评论数
    reviewFlag = mcht.find('a',class_='review-num')
    if reviewFlag is not None:
        reviewNum = reviewFlag.b.text.encode('UTF-8') #评论数
    else:
        reviewNum ='-1'.encode('utf8')
    #人均价格
    meanpriceFlag = mcht.find('a',class_='mean-price').find('b')
    if meanpriceFlag is not None:
        meanPrice = meanpriceFlag.text.encode('UTF-8')
        meanPrice = multiple_replace(meanPrice,adict)
    else:
        meanPrice = '-1'.encode('utf8')
    #评论相关的口味，环境，服务信息
    commentInfo = mcht.find('span',class_='comment-list')
    if commentInfo is not None:
        info = commentInfo.find_all('span')
        taste = info[0].b.text.encode('UTF-8') #口味
        environment = info[1].b.text.encode('UTF-8') #环境
        service = info[2].b.text.encode('UTF-8') #服务
    else:
        taste  =''
        environment = ''
        service = ''
    addrInfo = mcht.find('div','tag-addr').find_all('a')
    mchType = addrInfo[0].span.text.encode('utf8') #美食商户类型
    businRegion = addrInfo[1].span.text.encode('utf8')  #商户所在商圈
    #地址
    address = mcht.find('span',class_='addr').text.encode('UTF-8')
    address = multiple_replace(address,adict)
    #存储数据
    data = ','.join([cityNm,adminRegion_glb.decode('utf8'),businRegion.decode('utf8'),name.decode('utf8'),\
           level.decode('utf8'),reviewNum.decode('utf8'),meanPrice.decode('utf8'),taste.decode('utf8'), \
           environment.decode('utf8'),service.decode('utf8'),mchType.decode('utf8'),address.decode('utf8'),mch_id.decode('utf8')])+'\n'
    with open(outFileName,'a') as fw:
        fw.write(data.encode('gbk','ignore'))


def loadCityList(filename):
    city = {} #dict:{'cityname':'cityid'}
    with open(filename,'r') as fr:
        for line in fr.readlines()[1:]:
            li = line.strip().split('\t')
            if city.has_key(li[1]):
                continue
            else:
                city[li[1]] = li[0].decode('GBK')
    return city

def oriFailedPageReCrawl():
    '''针对爬取过程中获取页码数据的原始页面失败导致的错误页面，重新进行爬取'''
    maxTryTms = 2
    filename = os.getcwd()+'/'+'OriFailedPageUrl.txt'
    for tm in range(maxTryTms):  
    #尝试爬取文件内容多次
        resList = []
        if os.path.exists(filename):
            with open(filename,'r') as fr:
                for line in fr.readlines():
                    response = connect(line.strip())
                    if response is not None:
                        datasoup = BeautifulSoup(response,"lxml")
                        pageTags = datasoup.find('div',class_='page').find_all('a',class_='PageLink')
                        pageNum = [pgTag.text for pgTag in pageTags]
                        for pgNo in range(1,max(pageNum)+1):
                            urlNew = line +'p'+str(pgNo)
                            getMchInfo(urlNew)
                    else:
                        #再次不成功则保存链接 
		        if len(line) != 0:
                            resList.append(line)
            if len(resList) != 0:    #仍有未爬取链接的情况
                with open(filename,'w') as fw:  #覆盖源文件内容
                    for item in resList:
                        fw.write(str(item)+'\n')
            else:                    #全部都爬取结束则删除文件
                os.remove(filename)

def singlFailedURLReCrawl():
    '''针对爬取过程中单个page页面爬取错误的重新爬取'''
    maxTryTms = 2
    filename = os.getcwd()+'/'+'SingleFailedPageUrl.txt'
    for tm in range(maxTryTms):
        resList = []
        if os.path.exists(filename):
            with open(filename,'r') as fr:
                for line in fr.readlines():
                    time.sleep(random.uniform(0.1,1))
                    response = connect(url)
                    if response is not None:
                        datasoup = BeautifulSoup(response,"lxml")
                        adminRegion_glb = datasoup.find('div',id = "region-nav").find('a',class_="cur").text.encode('utf-8')
                        storeList = datasoup.find_all('div',class_="txt")
                        for store in storeList:
                            getStoreDetailInfo(store)
                    else:
		        if len(url) != 0 :
                            resList.append(line)
            if len(resList) != 0:
                with open(filename,'w') as fw:
                    for item in resList:
                        fw.write('%s\n'%item)
            else:
                os.remove(filename)
        
                    

if __name__=="__main__":
    start = time.clock()  #程序开始时间
    filename ="cityList3.txt"
    cityDict = loadCityList(filename)
    for cityno in cityDict.keys():
        cityNm = cityDict[cityno]
        url = 'http://www.dianping.com/search/category/'+cityno+'/10/'
        getRegionFoodType(url)
    oriFailedPageReCrawl()
    #singlFailedURLReCrawl()
    elapsed = str(time.clock()-start)
    print u"\n爬取结束,所花时间%s,请按任意键退出..."%elapsed
    raw_input()
