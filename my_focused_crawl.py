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

class My_Priority_Queue:
    ''' priority queue with update time 
        if there are multiple same url with old and new promise
        ignore the url with old pormise according to the update_time dict
    '''
    
    def __init__(self):
        self.queue = [] # store Url class
        self.promise = {} # promise of url in queue
        self.promise_update_time = {} # latest update time of promise in queue
        self.time_count = 0 # time counter for update time
    
    def size(self):
        self.top()
        return len(self.queue)
    
    def add(self, url, promise, depth, from_url):
        ''' add url with promise to priority queue '''
        update_time = self.getTime()
        self.promise[url] = promise
        self.promise_update_time[url] = update_time # update the promise time

        heapq.heappush(self.queue, Url(url, promise, update_time, depth, from_url))

    def pop(self):
        ''' pop and return the top value '''
        self.top()
        return heapq.heappop(self.queue)

    def top(self):
        ''' return the top value '''
        while len(self.queue) > 0:
            current = heapq.heappop(self.queue)
            url = current.url
            update_time = current.update_time
            if update_time != self.promise_update_time[url]:
                continue
            self.add(url, current.promise, current.depth, current.from_url)
            return current

    def getTime(self):
        self.time_count += 1
        return self.time_count

    def get_promise(self, url):
        ''' get url's promise value '''
        if url not in self.promise:
            return 0.0
        return self.promise[url]

class My_Focused_Crawl:
    ''' focused crawl class, use priority queue to store promised url '''
    MAX_HOST_VISIT_NUMBER = 50 # limit the maximum number of same host pages
    RELEVANCE_SCORE_RATIO = 0.2 # how relevance score in downloaded page influnence promise of links in it
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
        self.queue = My_Priority_Queue()
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
        print ('relevance is {}'.format(relevance_score))
        if is_start_page_url:
            self.start_url_relevance_score_sum += relevance_score
            self.start_url_count += 1

        self.download_page[parse_url] = Page(parse_url, promise, download_time, http_code, relevance_score, depth, from_url)
            
        if depth >= 5:
            return
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

            word_set = set()
            for search_term in self.search_terms:
                if re.search(search_term, text, re.IGNORECASE):
                    word_set.add(search_term)
                    # count += 1

            old_promise = self.queue.get_promise(url)
            new_promise = 0
            if len(word_set) == 1:
                new_promise += 1
            elif len(word_set) > 1:
                new_promise += 10
            
            new_promise = new_promise * 0.6 + old_promise * 0.6
            # calculate the new promise value
            # new_promise = self.queue.get_promise(url)
            new_promise += relevance_score * self.RELEVANCE_SCORE_RATIO / np.sqrt(len(links))
            if new_promise > self.MAX_PROMISE:
                new_promise = self.MAX_PROMISE

            print (' get url {} at depth {} with promise {}'.format(url.encode('utf-8'), depth, new_promise))
            print (' size of queue is {}'.format(self.queue.size()))
            self.queue.add(url, new_promise, depth + 1, parse_url)

    def start_crawl(self, search_terms, limit_size, limit_time):
        start_time = util.get_current_time_in_seconds()
        self.search_terms = search_terms
        self.relevance_strategy = relevance_strategy.cosine_measure_strategy(search_terms)
        self.start_url_relevance_score_sum = 0.0
        self.start_url_count = 0
        self.not_found_page_count = 0
        self.fetch_error_page_count = 0
        start_urls = util.get_google_results(" ".join(search_terms), 10)  

        for start_url in start_urls:
            print (start_url.encode('utf-8'))
            self.queue.add(start_url, self.MAX_PROMISE, 0, start_url)
        
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
