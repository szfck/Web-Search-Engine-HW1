from page_and_url import Page, Url
import urllib, htmllib, formatter
import numpy as np
import urlparse
from bs4 import BeautifulSoup
import datetime, time
import heapq
import relevance_strategy
import re
from mimetypes import MimeTypes
import Queue
import util

class My_FIFO_Queue:
    
    def __init__(self):
        self.queue = Queue.Queue()

    def add(self, item):
        self.queue.put(item)

    def pop(self):
        return self.queue.get()

    def size(self):
        return self.queue.qsize()

class My_Bfs_Crawl:
    ''' bfs craw class, use first in first out queue to store url '''
    MAX_HOST_VISIT_NUMBER = 50 # limit the maximum number of same host pages
    MAX_PROMISE = 1000 # maximum value of promise

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
        self.queue = My_FIFO_Queue()
        self.download_page = {} # info of downloaded page
        self.host_count = {} # count the number of same host
    
    def download_and_parse(self, url_item, is_start_page_url = False):
        parse_url = url_item.url
        promise = url_item.promise
        from_url = url_item.from_url
        depth = url_item.depth

        mime = MimeTypes().guess_type(parse_url)[0]
        if mime in self.IGNORED_EXTENSIONS: # ignore 
            return

        try:
            resp = urllib.urlopen(parse_url)
        except:
            print ('{} fetch error'.format(parse_url.encode('utf-8')))
            self.fetch_error_page_count += 1
            return
        
        http_code = resp.getcode()
        if http_code != 200:
            print ('http code error: {} http code is {}'.format(parse_url.encode('utf-8') ,http_code))
            if http_code == 404:
                self.not_found_page_count += 1
            return

        download_time = util.get_current_time_in_seconds()

        soup = BeautifulSoup(resp, 'lxml')

        texts = soup.findAll(text=True)
        relevance_score = self.relevance_strategy.get_relevance(texts)
        if is_start_page_url:
            self.start_url_relevance_score_sum += relevance_score
            self.start_url_count += 1

        self.download_page[parse_url] = Page(parse_url, promise, download_time, http_code, relevance_score, depth, from_url)
        print ('relevance score is {}'.format(relevance_score))
            
        if depth > 5:
            return
        for item in soup.find_all('a', href=True):
            link = item['href']
            
            if len(link) >= 4 and link[:4] == 'http':
                url = link
            else:
                url = urlparse.urljoin(parse_url, link)

            if url in self.download_page:
                # print ('{} already exist'.format(url))
                continue
            if len(url) < 4 or url[:4] != 'http':
                continue

            print (' get url {} at depth {} from {}'.format(url.encode('utf-8'), depth, parse_url))
            self.queue.add(Url(url, -1, -1, depth + 1, parse_url))

    def start_crawl(self, search_terms, limit_size, limit_time):
        start_time = util.get_current_time_in_seconds()
        self.search_terms = search_terms
        self.relevance_strategy = relevance_strategy.cosine_measure_strategy(search_terms)
        self.start_url_relevance_score_sum = 0.0
        self.start_url_count = 0
        self.not_found_page_count = 0
        self.fetch_error_page_count = 0
        start_urls = util.get_google_results(" ".join(search_terms), 10)  
        # start_urls = [u'http://www.fire.ca.gov/general/firemaps', u'http://calfire.ca.gov/about/downloads/Glance2006.pdf', u'http://www.calfire.ca.gov/communications/communications_factsheets', u'https://projects.sfchronicle.com/2018/fire-tracker/', u'https://abc7.com/firefighters-knock-down-oil-well-fire-in-santa-paula/4377402/', u'https://www.sfgate.com/california-wildfires/article/California-wildfires-remain-major-threat-despite-13273043.php', u'https://patch.com/california/livermore/fire-near-livermore-homeless-encampment-extinguished-saturday', u'https://abc7news.com/maps-wildfires-burning-across-california/3829366/', u'http://www.latimes.com/local/california/la-me-california-fires-blog-htmlstory.html', u'https://www.sacbee.com/news/state/california/fires/article218181325.html']
        # start_urls = ['https://www.abc10.com/video']

        for start_url in start_urls:
            print (start_url.encode('utf-8'))
            self.queue.add(Url(start_url, self.MAX_PROMISE, -1, 0, start_url))
        
        while len(self.download_page) < limit_size and self.queue.size() > 0:
            current_time = util.get_current_time_in_seconds()
            if current_time - start_time > limit_time:
                break
            current = self.queue.pop()
            url = current.url
            print ('** get one node out of queue: {}'.format(current))
            if url in self.download_page: # already downloaded
                continue
            hostname = util.get_hostname(url)
            if hostname in self.host_count and self.host_count[hostname] >= self.MAX_HOST_VISIT_NUMBER: # exceed maxinum host count
                continue
            if hostname in self.host_count:
                self.host_count[hostname] += 1
            else:
                self.host_count[hostname] = 1

            print ('[{}]download and parse {}, promise is {}'.format(len(self.download_page), url.encode('utf-8'), current.promise))
            
            self.download_and_parse(current, current.promise == self.MAX_PROMISE)
        
        end_time = util.get_current_time_in_seconds()
        print ('use {} seconds'.format(end_time - start_time))

        start_url_relevance_score_sum = self.start_url_relevance_score_sum / self.start_url_count
        relevance_threshhold = start_url_relevance_score_sum * 0.3
        
        total_visit_page_count = len(self.download_page) + self.not_found_page_count + self.fetch_error_page_count
        print ('visit total {} pages, where {} is 404 not found, {} is fetch error' \
            .format(total_visit_page_count, self.not_found_page_count, self.fetch_error_page_count))
        
        download_count = len(self.download_page)
        print ('--- download {} pages ---'.format(download_count))

        related_count = 0
        for url, page in self.download_page.iteritems():
            print (page)
            if page.relevance >= relevance_threshhold:
                related_count += 1
        
        print ('--- start {} pages ---'.format(len(start_urls)))
        for start_url in start_urls:
            if start_url in self.download_page:
                print (self.download_page[start_url])
        print ('average of start page relevance is {}'.format(start_url_relevance_score_sum))
        print ('threshhold of relevance is {}'.format(relevance_threshhold))
        
        print ('during {} download pages, {}\'s relevance are above {}, harvest_rate is {}'\
            .format(download_count, related_count, relevance_threshhold, 1.0 * related_count / download_count))
