import google_search_helper
import urllib, htmllib, formatter
import numpy as np
import urlparse
import search_util
import my_queue

class Page:
    
    def __init__(self, url, score):
        self.url = url
        self.score = score
    
    def __cmp__(self, other):
        # for max heap
        return cmp(-self.score, -other.score)

class My_Crawl:
    MAX_HOST_VISIT_NUMBER = 20
    MAX_LINK_VISIT = 30
    FILE_TYPE_BLACKLIST = [
        'jpg', 'pdf'
    ]

    def __init__(self, search_terms, queue):
        self.visited_urls = set()
        self.found_pages = []
        self.hostname_count = {}
        self.search_terms = search_terms
        format = formatter.NullFormatter()
        self.htmlparser = search_util.LinksExtractor(format)
        search_terms_str = " ".join(search_terms)
        self.start_pages = google_search_helper.get_google_top_10_search_result(search_terms_str)
        search_terms = [x.lower() for x in search_terms]
        self.queue = queue

    def is_legal_file_type(self, url):
        last_pos_of_dot = url.rfind('.')
        if last_pos_of_dot < 0:
            return True
        file_type = url[last_pos_of_dot + 1:]
        if file_type in self.FILE_TYPE_BLACKLIST:
            return False
        else:
            return True

    def get_all_legal_links(self, url):
        # format = formatter.NullFormatter()
        # htmlparser = LinksExtractor(format)

        try:
            data = urllib.urlopen(url)
        except:
            raise Exception()
        self.htmlparser.feed(data.read())
        self.htmlparser.close()

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
                absolute_url = urlparse.urljoin(url, link)
            elif len(link) >= 4 and link[:4] == 'http':
                absolute_url = link
            else:
                continue

            if self.is_legal_file_type(absolute_url):
                legal_links.append(absolute_url)

        return legal_links

    def get_word_count_and_doc_len(self, url):
        try:
            response = urllib.urlopen(url)
        except:
            raise Exception()
        html = response.read().strip().lower().split(' ')
        count = 0;
        doc_len = len(html)
        for word in html:
            if word in self.search_terms:
                count += 1
        return [count, doc_len]

    def add_page(self, url):
        if url in self.visited_urls:
            return

        hostname = search_util.get_hostname(url)
        if hostname in self.hostname_count:
            if self.hostname_count[hostname] > self.MAX_HOST_VISIT_NUMBER:
                return
            self.hostname_count[hostname] += 1
        else:
            self.hostname_count[hostname] = 1
        
        self.visited_urls.add(url)
        try:
            word_count, doc_len = self.get_word_count_and_doc_len(url)
        except:
            return
        score = word_count / np.sqrt(doc_len)
        page = Page(url, score)
        # heapq.heappush(self.max_heap, page)
        self.queue.add(page)
        print ("add page {} with score {}".format(url, score))
    
    def start_crawl(self, limit):
        for page in self.start_pages:
            self.add_page(page)

        while len(self.found_pages) < limit and self.queue.size() > 0:
            print ('already visited {} urls'.format(len(self.visited_urls)))
            current_page = self.queue.top_and_pop()
            self.found_pages.append(current_page) # add to found page list
            print ('current page {} with score {}'.format(current_page.url, current_page.score))
            try:
                links = self.get_all_legal_links(current_page.url)
            except:
                continue

            link_count = 0
            for link in links:
                link_count += 1
                if link_count > self.MAX_LINK_VISIT:
                    break
                self.add_page(link)

        print ('find {} results'.format(len(self.found_pages)))
        for page in self.found_pages:
            print ('{}'.format(page.url))

class My_Focused_Craw(My_Crawl):
    
    def __init__(self, search_terms):
        My_Crawl.__init__(self, search_terms, my_queue.My_Priority_Queue())

class My_Bfs_Craw(My_Crawl):
    
    def __init__(self, search_terms):
        My_Crawl.__init__(self, search_terms, my_queue.My_FIFO_Queue())
