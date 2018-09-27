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

def get_hostname(url):
    parsed_url = urlparse.urlparse(url)
    return parsed_url.hostname
