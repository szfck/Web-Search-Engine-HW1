from base_crawl import Base_Crawl
import numpy as np
import heapq

class Page:
    
    def __init__(self, url, score):
        self.url = url
        self.score = score
    
    def __cmp__(self, other):
        # for max heap
        return cmp(-self.score, -other.score)

class Focused_Crawl(Base_Crawl):

    def __init__(self, search_terms):
        super(self, search_terms)
        self.max_heap = []
    
    def add_page(self, url):
        if url in self.visited_urls:
            return

        hostname = self.get_hostname(url)
        if hostname in self.hostname_count:
            if self.hostname_count[hostname] > self.MAX_HOST_VISIT_NUMBER:
                return
            self.hostname_count[hostname] += 1
        else:
            self.hostname_count[hostname] = 1
        
        self.visited_urls.add(url)
        try:
            word_count, doc_len = self.get_word_count_and_doc_len(url, self.search_terms)
        except:
            return
        score = word_count / np.sqrt(doc_len)
        page = Page(url, score)
        heapq.heappush(self.max_heap, page)
        print ("add page {} with score {}".format(url, score))