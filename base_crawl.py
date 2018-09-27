import google_search_helper
import urllib, htmllib, formatter
import urlparse
import search_util

class Page:
    
    def __init__(self, url, score):
        self.url = url
        self.score = score
    
    def __cmp__(self, other):
        # for max heap
        return cmp(-self.score, -other.score)

class Base_Crawl:
    MAX_HOST_VISIT_NUMBER = 20
    MAX_LINK_VISIT = 30
    FILE_TYPE_BLACKLIST = [
        'jpg', 'pdf'
    ]

    def __init__(self, search_terms):
        self.visited_urls = set()
        self.found_pages = []
        self.hostname_count = {}
        self.search_terms = search_terms
        format = formatter.NullFormatter()
        self.htmlparser = search_util.LinksExtractor(format)
        search_terms_str = " ".join(search_terms)
        self.start_pages = google_search_helper.get_google_top_10_search_result(search_terms_str)
        search_terms = [x.lower() for x in search_terms]

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

    # def get_hostname(self, url):
    #     parsed_url = urlparse.urlparse(url)
    #     return parsed_url.hostname

    def add_page(self, url):
        ''' abstract method '''
        raise NotImplementedError("Please Implement this method")
    
    def start_crawl(self, limit):
        ''' abstract method '''
        raise NotImplementedError("Please Implement this method")
