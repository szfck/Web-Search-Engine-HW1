from page_and_url import Page, Url
import heapq
import util
import urllib, htmllib, formatter
import numpy as np
import urlparse
from bs4 import BeautifulSoup
import datetime, time
import heapq
import relevance_strategy
import re
from mimetypes import MimeTypes

class My_Crawl:
    ''' base crawl class '''
    MAX_HOST_VISIT_NUMBER = 50 # limit the maximum number of same host pages
    RELEVANCE_SCORE_RATIO = 0.2 # how relevance score in downloaded page influnence promise of links in it
    MAX_PROMISE = 1000 # maximum value of promise
    MAX_DEPTH = 5 # maximum depth in search

    # common file extensions that are not followed if they occur in links
    IGNORED_EXTENSIONS = [
        # images
        'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
        'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',

        # audio
        'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

        # video
        '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
        'm4a',

        # other
        'css', 'pdf', 'doc', 'exe', 'bin', 'rss', 'zip', 'rar',
    ]

    def __init__(self):
        self.download_page = {} # info of downloaded page
        self.host_count = {} # count the number of same host
        self.promise = {} # promise of url
        self.time_count = 0 # for update time in queue
    
    def get_increment_time(self):
        ''' increment time by 1, for promise update time '''
        self.time_count += 1
        return self.time_count

    def calculate_promise(self, url, text, relevance_score, link_number):
        ''' abstract method, calculate relevance score '''
        raise NotImplementedError("Please Implement this method")
    
    def add_to_queue(self, item):
        ''' abstract method, add item to queue '''
        raise NotImplementedError("Please Implement this method")

    def pop_from_queue(self):
        ''' abstract method, pop and return top value from queue '''
        raise NotImplementedError("Please Implement this method")

    def queue_size(self):
        ''' abstract method, return size of queue '''
        raise NotImplementedError("Please Implement this method")
    
    def need_stop(self):
        ''' if need to stop crawling links in a downloaded page, default is false '''
        return False

    def download_and_parse(self, url_item, is_start_page_url = False):
        ''' download and parse links for given url '''
        parse_url = url_item.url
        promise = url_item.promise
        from_url = url_item.from_url
        depth = url_item.depth

        mime = MimeTypes().guess_type(parse_url)[0]
        if mime in self.IGNORED_EXTENSIONS: # ignore illegal file type
            return

        try:
            resp = urllib.urlopen(parse_url)
        except:
            print ('{} fetch error'.format(parse_url.encode('utf-8')))
            self.fetch_error_page_count += 1 # fetch error
            return
        
        http_code = resp.getcode()
        if http_code != 200:
            print ('http code error: {} http code is {}'.format(parse_url.encode('utf-8') ,http_code))
            if http_code == 404: # not found
                self.not_found_page_count += 1
            return

        download_time = util.get_current_time_in_seconds()

        soup = BeautifulSoup(resp, 'lxml')

        texts = soup.findAll(text=True)

        # calculate relevance score
        relevance_score = self.relevance_strategy.get_relevance(texts)
        print ('relevance is {}'.format(relevance_score))

        if is_start_page_url:
            self.start_url_relevance_score_sum += relevance_score
            self.start_url_count += 1

        # add download page to result list
        self.download_page[parse_url] = Page(parse_url, promise, download_time, http_code, relevance_score, depth, from_url)
            
        # if search depth is too large, return
        if depth >= self.MAX_DEPTH:
            return

        if self.need_stop():
            return

        # crawl links in the page
        links = soup.find_all('a', href=True)
        for item in links:
            link = item['href']
            text = item.text
            
            if len(link) >= 4 and link[:4] == 'http':
                url = link
            else:
                url = urlparse.urljoin(parse_url, link)

            if url in self.download_page:
                continue
            if len(url) < 4 or url[:4] != 'http':
                continue

            # calculate the new promise score
            new_promise = self.calculate_promise(url, text, relevance_score, len(links))

            print (' queue size {}, get url {} at depth {} with promise {} from url {}'.format(self.queue_size(), url.encode('utf-8'), depth, new_promise, parse_url))
            # add url with new promise to the queue
            self.add_to_queue(Url(url, new_promise, self.get_increment_time(), depth + 1, parse_url))

    def start_crawl(self, search_terms, limit_size, limit_time):
        start_time = util.get_current_time_in_seconds() # start time
        self.search_terms = search_terms # search term list
        # use cosine measure to calculate relevance value
        self.relevance_strategy = relevance_strategy.cosine_measure_strategy(search_terms) 
        self.start_url_relevance_score_sum = 0.0 # sum of start page relevance value
        self.start_url_count = 0 # number of start pages
        self.not_found_page_count = 0 # 404 not found count
        self.fetch_error_page_count = 0 # fetch error count
        self.start_urls = util.get_google_results(" ".join(search_terms), 10) # start pages

        max_promise = self.MAX_PROMISE
        # add start page to queue
        for start_url in self.start_urls:
            print (start_url.encode('utf-8'))
            self.add_to_queue(Url(start_url, max_promise, self.get_increment_time(), 0, start_url))
            max_promise -= 10 # decrease promise by 10 every time for google search result
        
        # start crawling
        while len(self.download_page) < limit_size and self.queue_size() > 0:
            current_time = util.get_current_time_in_seconds()
            # break loop if exceed limit time
            if current_time - start_time > limit_time:
                break
            current = self.pop_from_queue() # get top node from queue
            url = current.url
            print ('** get one node out of queue: {}'.format(current))
            if url in self.download_page: # already downloaded
                continue
            hostname = util.get_hostname(url)
            # ignore if exceed maximum host count
            if hostname in self.host_count and self.host_count[hostname] >= self.MAX_HOST_VISIT_NUMBER: # exceed maxinum host count
                continue
            if hostname in self.host_count:
                self.host_count[hostname] += 1
            else:
                self.host_count[hostname] = 1

            print ('[{}]download and parse {}, promise is {}'.format(len(self.download_page), url.encode('utf-8'), current.promise))
            
            # start download and parse page
            self.download_and_parse(current, current.promise >= self.MAX_PROMISE - 100)
        
        end_time = util.get_current_time_in_seconds()
        print ('use {} seconds'.format(end_time - start_time)) # total time spent
        self.output()
    
    def output(self):
        ''' output crawl result '''
        # calculate start page average relevance score
        start_url_relevance_score_sum = self.start_url_relevance_score_sum / self.start_url_count
        # calculate relevance threshhold: 0.5 * start pages average relevance
        relevance_threshhold = start_url_relevance_score_sum * 0.5
        
        # total visit page = download page + not found page + fetch error page
        total_visit_page_count = len(self.download_page) + self.not_found_page_count + self.fetch_error_page_count
        print ('visit total {} pages, where {} is 404 not found, {} is fetch error' \
            .format(total_visit_page_count, self.not_found_page_count, self.fetch_error_page_count))
        
        download_count = len(self.download_page)

        # output download page list
        print ('--- start {} pages ---'.format(len(self.start_urls)))
        for start_url in self.start_urls:
            if start_url in self.download_page:
                print (self.download_page[start_url])
        print ('--- download {} pages ---'.format(download_count))

        # calculate related page count
        related_count = 0
        for url, page in self.download_page.iteritems():
            print (page)
            if page.relevance >= relevance_threshhold:
                related_count += 1
        
        print ('average of start page relevance is {}'.format(start_url_relevance_score_sum))
        print ('threshhold of relevance is {}'.format(relevance_threshhold))
        
        print ('during {} download pages, {}\'s relevance are above {}, harvest_rate is {}'\
            .format(download_count, related_count, relevance_threshhold, 1.0 * related_count / download_count))

