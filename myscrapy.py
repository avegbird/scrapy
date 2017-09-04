# -*- coding: utf-8 -*-
import urllib2
from pip._vendor.requests.api import request
import socket
import json
import re
import ssl
import threading
import time


class myscrapy(object):
    _name = "myscrapy"
    start_url = ["https://www.jd.com/"]
    url_domain = [['www.jd.com', ], ]
    Maxdeep = 10
    MAXTHREAT = 10# max threads count
    lock = threading.RLock()
    thread_count = 0

    def __init__(self, user_agent=None, timeout=10, retrytimes=2, isrepeat=True, care_mode=False, delay=0):
        """
        :param user_agent: 用户代理，默认为chrome浏览器代理
        :param timeout: 访问url超时时间
        :param retrytimes: url超时重试次数
        :param isrepeat: 是否进行重复剔除
        :param care_mode: 是否进行小心模式
        :param delay: 小心模式下访问间隔
        """
        print "init is run"
        self.delay = delay
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) " \
                              "AppleWebKit/537.36 (KHTML, like Gecko) " \
                              "Chrome/60.0.3112.113 Safari/537.36"
        self.timeout = timeout
        self.retrytimes = retrytimes

        self.headers = {'User-agent': self.user_agent}

        self.request = []
        self.isrepeat = isrepeat
        if isrepeat:
            self.repeat = []

        self.Resources_mp4 = []
        self.Resources_jpg = []
        self.lock = threading.RLock()
        self.care_mode = care_mode
        self.last_call = time.time()

    def start_request(self):
        """开始爬取request"""
        print "start request"
        for url in self.start_url:
            if self.isrepeat:
                if url in self.repeat:
                    continue
                self.repeat.append(url)
            self.request.append(urllib2.Request(url=url, headers=self.headers))
        self.scrapy_request(call_back=self.data_callback)

    def scrapy_request(self, call_back):
        """消费request，后期可以做成多进程访问"""
        print "start scrapy request"
        while self.request or self.thread_count > 0:
            if not self.care_mode:
                while self.thread_count < self.MAXTHREAT:
                    myscrapy.thread_count += 1
                    try:
                        http = self.request.pop()
                    except IndexError as e:
                        time.sleep(1)
                        continue
                    t = ScrapyRequest(http, retrytimes=self.retrytimes, callback=call_back)
                    t.start()
            else:
                retry = 0
                while retry < self.retrytimes:
                    try:
                        if self.delay > 0:
                            now = time.time()
                            last = now - self.last_call
                            if self.delay > last:
                                time.sleep(int(self.delay-last))
                        http = self.request.pop()
                        data = urllib2.urlopen(http, timeout=self.timeout).read()
                        call_back(data, http)
                        break
                    except urllib2.URLError as e:
                        if isinstance(e.reason, socket.timeout):
                            print "timeout and retry {}".format(retry)
                            retry += 1
                        else:
                            print 'url is error:', e.message
                            print http._Request__original
                            break
                    except ssl.SSLError as e:
                        print 'SSLError:', e.message
                        print http._Request__original
                    except Exception, e:
                        print 'unknow Error：', e.message
                        print http._Request__original
        with open('D:\Python27\workspace\mp4.txt', 'ab') as mp4:
            for line in self.Resources_mp4:
                mp4.write(str(line) + '\r\n')
        with open('D:\Python27\workspace\jpg.txt', 'ab') as jpg:
            for line in self.Resources_jpg:
                jpg.write(str(line) + '\r\n')

    def make_request(self, urls):
        """生产request"""
        for url in urls:
            print url
            for domains in self.url_domain:
                for domain in domains:
                    if domain in url:
                        if self.isrepeat:
                            if url in self.repeat:
                                continue
                            self.repeat.append(url)

                        # calculate the pseudo deep
                        base_count = 2
                        this_count = url.count('/')
                        if this_count - base_count <= self.Maxdeep:
                            self.request.append(urllib2.Request(url=url, headers=self.headers))

    def data_callback(self, data, request):
        """处理页面,注意同步问题"""
        print "callback"
        # get all the url in this page
        # get pic url <img[^>]+src=["\'](.*?)["\']
        webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
        webpage_jpg = re.compile('<img[^>]+src=["\'](.*?)["\']', re.IGNORECASE)
        urls = webpage_regex.findall(data)
        jpgs = webpage_jpg.findall(data)
        # first to complete the url
        host = request._Request__original
        if host.endswith('.html'):
            host = host[0:-5]
        if host.endswith('/'):
            host = host[0:-1]
        new_urls = []
        self.lock.acquire()
        for url in urls:
            if "http://" not in url and "https://" not in url:
                url = self.merge_url(host, url)
            if url.endswith('.html'):
                new_urls.append(url)
            elif url.endswith('.mp4'):
                if url not in self.Resources_mp4:
                    self.Resources_mp4.append(url)
        for jpg in jpgs:
            if "http://" not in url and "https://" not in url:
                url = host + url
            if url.endswith('.jpg'):
                if url not in self.Resources_jpg:
                    self.Resources_jpg.append(url)
        self.make_request(new_urls)
        self.lock.release()
        pass

    def merge_url(self, host, url):
        if url[0:2] == '//':
            url = url[1:]
        minlen = 1000
        if minlen > len(host):
            minlen = len(host)
        if minlen > len(url):
            minlen = len(url)
        maxlike = 0
        for i in range(minlen):
            tail_host = host[-1 - i:]
            head_url = url[0:1 + i]
            if tail_host == head_url:
                if maxlike < i:
                    maxlike = i
        host = host + url[maxlike:]
        return host

class ScrapyRequest(threading.Thread):
    def __init__(self, http, retrytimes=2, timeout=10, **kwargs):
        super(ScrapyRequest, self).__init__()
        self.http = http
        self.retrytimes = retrytimes
        self.timeout = timeout
        if kwargs.get('callback'):
            self.callback = kwargs['callback']

    def run(self):
        retry = 0
        while retry < self.retrytimes:
            try:
                data = urllib2.urlopen(self.http, timeout=self.timeout).read()
                self.callback(data, self.http)
                break
            except urllib2.URLError as e:
                if isinstance(e.reason, socket.timeout):
                    print "timeout and retry {}".format(retry)
                    retry += 1
                else:
                    print 'url is error:', e.message
                    print self.http._Request__original
                    break
            except ssl.SSLError as e:
                print 'SSLError:', e.message
                print self.http._Request__original
            except Exception, e:
                print 'unknow Error：',e.message
                print self.http._Request__original
            finally:
                myscrapy.thread_count -= 1


scrapy = myscrapy()
scrapy.start_request()