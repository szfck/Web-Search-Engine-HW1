import google_search_helper
import urllib, htmllib, formatter
import numpy as np
import urlparse
import search_util
import my_queue
import datetime, time

# To Store Page information
class Page:
    
    def __init__(self, url, score, time, http_code, size, is_related):
        self.url = url
        self.score = score
        self.time = time
        self.http_code = http_code
        self.size = size
        self.is_related = is_related
    
    def __cmp__(self, other):
        # for max heap
        return cmp(-self.score, -other.score)

    def __str__(self):
        return str("[{}](time: {}, url: {}, score: {}, code: {}, size: {})" \
            .format(self.score, self.time, self.url, self.score, self.http_code, self.size))

# Base Crawl Class, which could be derived
class My_Crawl:
    MAX_HOST_VISIT_NUMBER = 100 # limit the maximum number of same host pages
    MAX_LINK_VISIT = 100 # limit the maximum number of links crawled in the same page

    FILE_TYPE_BLACKLIST = [ 'jpg', 'pdf' ] # black list for specified file type

    def __init__(self, search_terms, queue):
        self.visited_urls = set() # set to record urls added to the queue
        self.found_pages = [] # found page list (pop from the queue)
        self.hostname_count = {} # map to record number of pages added to the queue under same hostname
        self.search_terms = search_terms
        format = formatter.NullFormatter()
        self.htmlparser = search_util.LinksExtractor(format)
        search_terms_str = " ".join(search_terms)

        # get google search result as start pages
        self.start_pages = google_search_helper.get_google_top_10_search_result(search_terms_str)

        search_terms = [x.lower() for x in search_terms]
        self.queue = queue
        self.total_size = 0 # total size of pages added to the queue
        self.count_404 = 0 # total number of 404 pages added to the queue

    def is_legal_file_type(self, url):
        ''' check if the url is ended with legal file type '''
        last_pos_of_dot = url.rfind('.')
        if last_pos_of_dot < 0:
            return True
        file_type = url[last_pos_of_dot + 1:]
        if file_type in self.FILE_TYPE_BLACKLIST:
            return False
        else:
            return True

    def get_all_legal_links(self, url):
        ''' get all the legal links in the web page with url '''
        try:
            data = urllib.urlopen(url)
            self.htmlparser.feed(data.read())
            self.htmlparser.close()
        except:
            return []

        links = self.htmlparser.get_links()

        legal_links = []
        for link in links:
            # ignore empty link
            if len(link) <= 0:
                continue
            # ignore link starting with '#'
            if len(link) >= 1 and link[0] == '#':
                continue
            if len(link) >= 1 and link[0] == '/':
                try:
                    absolute_url = urlparse.urljoin(url, link)
                except:
                    continue
            elif len(link) >= 4 and link[:4] == 'http':
                absolute_url = link
            else:
                continue

            if self.is_legal_file_type(absolute_url):
                legal_links.append(absolute_url)

        return legal_links

    def get_word_count_and_doc_len(self, html):
        ''' given html text, return a list [related search word count, document length, is related or not] '''
        html = html.strip().lower().split(' ')
        count = 0;
        doc_len = len(html)
        related_term = set()
        for word in html:
            if word in self.search_terms:
                count += 1
                related_term.add(word)
        
        if len(related_term) == len(self.search_terms):
            is_related = True
        else:
            is_related = False
        return [count, doc_len, is_related]

    def add_page(self, url):
        ''' add url to the queue '''
        if url in self.visited_urls:
            return
        try:
            response = urllib.urlopen(url)
        except:
            return

        http_code = response.getcode()
        if http_code == 404: # return if http code is 404
            self.count_404 += 1
            return

        html = response.read()

        html_size = len(html)
        time = datetime.datetime.now()

        hostname = search_util.get_hostname(url)
        if hostname in self.hostname_count:
            if self.hostname_count[hostname] > self.MAX_HOST_VISIT_NUMBER:
                return
            self.hostname_count[hostname] += 1
        else:
            self.hostname_count[hostname] = 1
        
        self.visited_urls.add(url)
        word_count, doc_len, is_related = self.get_word_count_and_doc_len(html)
        score = word_count / np.sqrt(doc_len)
        self.total_size += html_size

        page = Page(url, score, time, http_code, html_size, is_related)
        self.queue.add(page)
        print ("add page to queue {}".format(page))
    
    def time2second(self, t):
        ''' change date time to seconds '''
        return time.mktime(t.timetuple())
    
    def start_crawl(self, limit_size, limit_time = 60 * 20):
        ''' start crawling based on the start page got from google
            return no more than limit_size page list within limit_time
        '''
        startTime = datetime.datetime.now()

        for page in self.start_pages:
            self.add_page(page)

        while len(self.found_pages) < limit_size and self.queue.size() > 0:
            # break if run longer than limit_time
            if self.time2second(datetime.datetime.now()) - self.time2second(startTime) > limit_time:
                break

            current_page = self.queue.top_and_pop()
            self.found_pages.append(current_page) # add to found page list
            print ('* search links in page {}'.format(current_page))

            if self.queue.size() > limit_size * 2: # to limit the size of queue
                continue
            links = self.get_all_legal_links(current_page.url)

            link_count = 0
            for link in links:
                link_count += 1
                if link_count > self.MAX_LINK_VISIT: # to limit links visit in the same page
                    break
                self.add_page(link)

        while len(self.found_pages) < limit_size and self.queue.size() > 0:
            page = self.queue.top_and_pop()
            if page.score > 0:
                self.found_pages.append(page)
        
        endTime = datetime.datetime.now()
        time_elapse = self.time2second(endTime) - self.time2second(startTime)

        print ('find {} results'.format(len(self.found_pages)))
        total_related_page_found = 0
        for page in self.found_pages:
            print ('{}'.format(page))
            if page.is_related:
                total_related_page_found += 1

        total_page_found = len(self.found_pages)
        total_page_visit = len(self.visited_urls)
        total_404_page_visit = self.count_404
        related_rate = 1.0 * total_related_page_found / total_page_found
        print ('use {} seconds'.format(time_elapse))
        print ('visit {} pages, total size is {}, in which have {} 404 pages' \
            .format(total_page_visit, self.total_size, total_404_page_visit))
        print ('find {} pages, in which {} are related, related rate is {}' \
            .format(total_page_found, total_related_page_found, related_rate))

# Focused Crawl Class, derived from My_Crawl Class
class My_Focused_Crawl(My_Crawl):
    
    def __init__(self, search_terms):
        # use priority queue
        My_Crawl.__init__(self, search_terms, my_queue.My_Priority_Queue())

# Bfs Crawl Class, derived from My_Crawl Class
class My_Bfs_Crawl(My_Crawl):
    
    def __init__(self, search_terms):
        # use first in first out queue
        My_Crawl.__init__(self, search_terms, my_queue.My_FIFO_Queue())
