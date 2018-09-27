from base_crawl import Base_Crawl, Page
import search_util
import numpy as np
import heapq
import Queue

class Bfs_Crawl(Base_Crawl):

    def __init__(self, search_terms):
        Base_Crawl.__init__(self, search_terms)
        self.queue = Queue.Queue()
    
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
        self.queue.put(page)
        print ("add page {} with score {}".format(url, score))
    
    def start_crawl(self, limit):
        for page in self.start_pages:
            self.add_page(page)

        while len(self.found_pages) < limit and self.queue.qsize() > 0:
            print ('already visited {} urls'.format(len(self.visited_urls)))
            # current_page = heapq.heappop(self.max_heap)
            current_page = self.queue.get()
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