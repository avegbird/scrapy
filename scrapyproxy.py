# -*- coding: utf-8 -*-

import urllib2
import handlDB
import random
import BeautifulSoup

class CrawlProxy(object):
    def __init__(self, **kwargs):

        if kwargs.get('urlfunc'):
            self.urlfunc = kwargs['urlfunc']
        else:
            self.urlfunc = None
        if kwargs.get('callback'):
            self.callback = kwargs['callback']
        else:
            self.callback = None
        if self.urlfunc:
            self.urls = self.urlfunc()
        else:
            seed = "http://www.xicidaili.com/nn/{}"
            self.urls = [seed.format(i) for i in range(1, 2361)]

        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) " \
                          "AppleWebKit/537.36 (KHTML, like Gecko) " \
                          "Chrome/60.0.3112.113 Safari/537.36"
        self.headers = {'User-agent': self.user_agent}
        self.db = handlDB.HandlDB()
        self.proxy = []
        for i in self.db.selectdb():
            self.proxy.append(i)

    def start_crawl(self):
        for url in self.urls:
            try:
                if self.proxy and False:
                    i = random.randint(0, len(self.proxy)-1)
                    ip = self.proxy[i][0]
                    port = self.proxy[i][1]
                    self._make_proxy(ip, port)
                    pass

                request = urllib2.Request(url=url, headers=self.headers)
                data = urllib2.urlopen(request, timeout=10).read()
                if self.callback:
                    self.callback(data)
                else:
                    self._callback(data)
            except Exception, e:
                print e.message #AttributeError
    def _callback(self, data):
        soup = BeautifulSoup.BeautifulSoup(data)

        ips = soup.findAll('tr')
        for x in range(1, len(ips)):
            ip = ips[x]
            tds = ip.findAll("td")
            ip_temp = tds[1].contents[0]
            port_temp = tds[2].contents[0]
            self.db.insertdb([ip_temp, port_temp])
            self.proxy.append([ip_temp, port_temp])

    def set_proxy(self, ip=None, port=None):
        if ip == None:
            if self.proxy:
                i = random.randint(0, len(self.proxy) - 1)
                ip = self.proxy[i][0]
                port = self.proxy[i][1]
                self._make_proxy(ip, port)
            else:
                raise "no find proxy, you can set them or run start_crawl to get the default proxy"

    def _make_proxy(self, ip, port):
        # The proxy address and port:
        proxy_info = {'host': ip, 'port': int(port)}

        # We create a handler for the proxy
        proxy_support = urllib2.ProxyHandler({"http": "http://%(host)s:%(port)d" % proxy_info})

        # We create an opener which uses this handler:
        opener = urllib2.build_opener(proxy_support)

        # Then we install this opener as the default opener for urllib2:
        urllib2.install_opener(opener)

        # Now we can send our HTTP request:
        # htmlpage = urllib2.urlopen("http://sebsauvage.net/").read(200000)

        # 如果代理需要验证
        # proxy_info = {'host': 'proxy.myisp.com',
        #               'port': 3128,
        #               'user': 'John Doe',
        #               'pass': 'mysecret007'
        #               }
        # proxy_support = urllib2.ProxyHandler({"http": "http://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy_info})
        # opener = urllib2.build_opener(proxy_support)
        # urllib2.install_opener(opener)


cp = CrawlProxy()
cp.start_crawl()

