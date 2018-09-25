import google_search_helper
from bs4 import BeautifulSoup
import heapq
import urllib2
import search_util
import urlparse
import numpy as np

is_test = False
search_term = 'dog cat'
search_terms = search_term.strip().lower().split(' ')
doc_number = 0 # total number of document
word_freq = {} # total number of occurences of t in the collection

if is_test: # for testing
    start_pages = [
        u'http://www.vetstreet.com/dogs/', 
        u'https://en.wikipedia.org/wiki/Dog', 
        u'https://www.youtube.com/watch%3Fv%3DSfLV8hD7zX4', 
        u'https://www.what-dog.net/', 
        u'https://www.urbandictionary.com/define.php%3Fterm%3DDogs', 
        u'https://simple.wikipedia.org/wiki/Dog', 
        u'https://people.com/pets/khloe-kardashian-gabbana-dog-dies-heart-tumor/', 
        u'https://www.nj.com/news/index.ssf/2018/09/amid_scrutiny_over_dog_deaths_petsmart_hosts_tour_of_grooming_salons_at_stores_across_the_us.html', 
        u'https://www.dog.com/', 
        u'https://www.webmd.com/pets/dogs/default.htm'
    ]
else:
    start_pages = google_search_helper.get_google_top_10_search_result(search_term)

class Page:
    
    def __init__(self, url, score):
        self.url = url
        self.score = score
    
    def __cmp__(self, other):
        return cmp(-self.score, -other.score)

def get_word_count_and_doc_len(url):
    response = urllib2.urlopen(url)
    html = response.read().strip().lower().split(' ')
    count = {}
    doc_len = len(html)
    for word in html:
        if word in search_terms:
            if word in count:
                count[word] += 1
            else:
                count[word] = 1
    return [count, doc_len]

# def get_score(url):
#     response = urllib2.urlopen(url)
#     html = response.read().strip().split(' ')
#     count = {}
#     total_word = len(html);
#     for word in html:
#         total_word += 1
#         if word in search_terms:
#             if word in count:
#                 count[word] += 1
#             else:
#                 count[word] = 1

#     score = 0
#     for word in search_terms:
#         if word in count:
#             score += count[word]
#     return score

heap = []
visited_urls = set()
pages = []

n = 20

def add_page(url):
    global doc_number
    if search_util.page_visible(url) and url not in visited_urls:
        word_count, doc_len = get_word_count_and_doc_len(url)

        # update doc number and total word frequency
        doc_number += 1
        for word in word_count:
            if word in word_freq:
                word_freq[word] += word_count[word]
            else:
                word_freq[word] = word_count[word]

        # calculate score using cosine measure
        # w_q_t * w_d_t / sqrt(doc_len)
        # w_q_t = ln(1 + doc_number / f_t)
        # w_d_t = 1 + ln(fdt)
        score = 0.0
        # print ('doc_len {}'.format(doc_len))
        # print ('doc_number {}'.format(doc_number))
        # print (word_count)
        for word in word_count:
            w_q_t = np.log(1 + 1.0 * doc_number / word_freq[word])
            w_d_t = 1 + np.log(word_count[word])
            word_score = w_q_t * w_d_t / np.sqrt(doc_len)
            # print ('w_q_t {}, w_d_t {}, word_score {}'.format(w_q_t, w_d_t, word_score))
            score += word_score

        page = Page(url, score)
        heapq.heappush(heap, page)
        # visited_urls.append(url)
        visited_urls.add(url)
        print ("add page {} with score {}".format(url, score))

def link_contains_search_term(text):
    text = text.strip().lower().split(' ')
    for word in text:
        if word in search_terms:
            return True
    return False

def get_all_links(url):
    resp = urllib2.urlopen(url)
    soup = BeautifulSoup(resp, 'lxml')

    links = []
    for item in soup.find_all('a', href=True):
        link = item['href']
        if link_contains_search_term(item.text) == False:
            continue
        if len(link) >= 1 and link[0] == '/':
            possible_url = urlparse.urljoin(url, link)
        elif len(link) >= 4 and link[:4] == 'http':
            possible_url = link
        else:
            continue
        if search_util.page_visible(possible_url):
            links.append(possible_url)
            # print (possible_url)

    return links

for link in start_pages:
    add_page(link)

# print (urlparse.urljoin('http://www.vetstreet.com/dogs/', '/dogs/'))
while len(pages) < n and len(heap) > 0:
    print ('visited {} urls'.format(len(visited_urls)))
    page = heapq.heappop(heap)
    pages.append(page) # add to found page list
    print ('current page {} with score {}'.format(page.url, page.score))
    links = get_all_links(page.url)
    for link in links:
        add_page(link)


print ('find {} results'.format(len(pages)))
for page in pages:
    print ('{}'.format(page.url))

