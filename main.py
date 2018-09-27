import google_search_helper
# from bs4 import BeautifulSoup
import urllib2
# import search_util
# import urlparse
import sys
# import numpy as np

# max_heap = []
# visited_urls = set()
# found_pages = []

n = 20

# MAX_HOST_NUMBER = 20

# def add_page(url, max_heap):
#     if url in visited_urls:
#         return

#     hostname = search_util.get_hostname(url)
#     if hostname in host_count:
#         if host_count[hostname] > MAX_HOST_NUMBER:
#             return
#         host_count[hostname] += 1
#     else:
#         host_count[hostname] = 1
    
#     visited_urls.add(url)
#     try:
#         word_count, doc_len = search_util.get_word_count_and_doc_len(url, search_terms)
#     except:
#         return
#     score = word_count / np.sqrt(doc_len)
#     page = Page(url, score)
#     heapq.heappush(max_heap, page)
#     print ("add page {} with score {}".format(url, score))

for link in start_pages:
    add_page(link, max_heap)

while len(found_pages) < n and len(max_heap) > 0:
    print ('already visited {} urls'.format(len(visited_urls)))
    current_page = heapq.heappop(max_heap)
    found_pages.append(current_page) # add to found page list
    print ('current page {} with score {}'.format(current_page.url, current_page.score))
    try:
        links = search_util.get_all_legal_links(current_page.url, search_terms)
    except:
        continue

    for link in links:
        add_page(link, max_heap)

print ('find {} results'.format(len(found_pages)))
for page in found_pages:
    print ('{}'.format(page.url))

def focused_crawl(search_terms, limit=1000):
    return
    
def bfs_crawl(search_terms, limit=1000):
    return

if __name__ == '__main__':
    search_type = sys.argv[1]
    search_terms = sys.argv[2:]
    # search_term = 'wildfires california'
    # search_terms = search_term.strip().lower().split(' ')
    host_count = {}

start_pages = google_search_helper.get_google_top_10_search_result(search_term)
