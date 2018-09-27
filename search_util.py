import urllib, htmllib, formatter
import urlparse

class LinksExtractor(htmllib.HTMLParser): # derive new HTML parser
    def __init__(self, formatter):
        htmllib.HTMLParser.__init__(self, formatter) # class constructor
        self.links = [] # create an empty list for storing hyperlinks
    
    def start_a(self, attrs): # override handler of <A...> ... </A> tags
        # process the attributes
        if len(attrs) > 0:
            for attr in attrs:
                if attr[0] == 'href': # ignore all non HREF attributes
                    self.links.append(attr[1]) # save the link info in the list
    
    def get_links(self): # return the list of extracted links
        return self.links


# def page_visible(url):
#     try:
#         response = urllib.urlopen(url)
#     except:
#         return False
#     return True

# FILE_TYPE_BLACKLIST = [
#     'jpg', 'pdf'
# ]

# def is_legal_file_type(url):
#     last_pos_of_dot = url.rfind('.')
#     if last_pos_of_dot < 0:
#         return True
#     file_type = url[last_pos_of_dot + 1:]
#     if file_type in FILE_TYPE_BLACKLIST:
#         return False
#     else:
#         return True

# def get_all_legal_links(url, search_terms):
#     format = formatter.NullFormatter()
#     # htmlparser = htmllib.HTMLParser(format)
#     htmlparser = LinksExtractor(format)

#     try:
#         data = urllib.urlopen(url)
#     except:
#         raise Exception()
#     # print (data.read())
#     htmlparser.feed(data.read())
#     htmlparser.close()

#     links = htmlparser.get_links()
#     # print (links)

#     legal_links = []
#     for link in links:
#         # ignore empty link
#         if len(link) <= 0:
#             continue
#         # ignore link starting with '#'
#         if len(link) >= 1 and link[0] == '#':
#             continue
#         if len(link) >= 1 and link[0] == '/':
#             absolute_url = urlparse.urljoin(url, link)
#         elif len(link) >= 4 and link[:4] == 'http':
#             absolute_url = link
#         else:
#             continue

#         if is_legal_file_type(absolute_url):
#             legal_links.append(absolute_url)

#     return legal_links

# def get_word_count_and_doc_len(url, search_terms):
#     try:
#         response = urllib.urlopen(url)
#     except:
#         raise Exception()
#     html = response.read().strip().lower().split(' ')
#     # count = {}
#     count = 0;
#     doc_len = len(html)
#     for word in html:
#         if word in search_terms:
#             count += 1
#             # if word in count:
#                 # count[word] += 1
#             # else:
#             #     count[word] = 1
#     return [count, doc_len]

# def get_hostname(url):
#     parsed_url = urlparse.urlparse(url)
#     return parsed_url.hostname

# def add_page(url):
#     global doc_number
#     if search_util.page_visible(url) and url not in visited_urls:
#         word_count, doc_len = get_word_count_and_doc_len(url)

#         # update doc number and total word frequency
#         doc_number += 1
#         for word in word_count:
#             if word in word_freq:
#                 word_freq[word] += word_count[word]
#             else:
#                 word_freq[word] = word_count[word]

#         # calculate score using cosine measure
#         # w_q_t * w_d_t / sqrt(doc_len)
#         # w_q_t = ln(1 + doc_number / f_t)
#         # w_d_t = 1 + ln(fdt)
#         score = 0.0
#         # print ('doc_len {}'.format(doc_len))
#         # print ('doc_number {}'.format(doc_number))
#         # print (word_count)
#         for word in word_count:
#             w_q_t = np.log(1 + 1.0 * doc_number / word_freq[word])
#             w_d_t = 1 + np.log(word_count[word])
#             word_score = w_q_t * w_d_t / np.sqrt(doc_len)
#             # print ('w_q_t {}, w_d_t {}, word_score {}'.format(w_q_t, w_d_t, word_score))
#             score += word_score

#         page = Page(url, score)
#         heapq.heappush(heap, page)
#         # visited_urls.append(url)
#         visited_urls.add(url)
#         print ("add page {} with score {}".format(url, score))

# def link_contains_search_term(text):
#     text = text.strip().lower().split(' ')
#     for word in text:
#         if word in search_terms:
#             return True
#     return False