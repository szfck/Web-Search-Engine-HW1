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

# To Store Url information
class Url:
    
    def __init__(self, url, promise, update_time, depth, from_url):
        self.url = url
        self.promise = promise # promise score of the link
        self.update_time = update_time # identify the latest promise
        self.depth = depth # search depth
        self.from_url = from_url # from which url
    
    def __cmp__(self, other):
        # for max heap
        return cmp(-self.promise, -other.promise)

    def __str__(self):
        return str('url: {}, promise: {}, update time count: {}, depth {}, from url {}' \
            .format(self.url.encode('utf-8'), self.promise, self.update_time, self.depth, self.from_url.encode('utf-8')))

# store page info
class Page:

    def __init__(self, url, promise, download_time, http_code, relevance, depth, from_url):
        self.url = url
        self.promise = promise
        self.download_time = download_time
        self.http_code = http_code
        self.relevance = relevance
        self.depth = depth
        self.from_url = from_url

    def __str__(self):
        return str('url: {}, promise: {}, download time: {}, http code: {}, relevance {}, depth {}, from url {}' \
            .format(self.url.encode('utf-8'), self.promise, self.download_time, self.http_code, self.relevance, self.depth, self.from_url.encode('utf-8')))
