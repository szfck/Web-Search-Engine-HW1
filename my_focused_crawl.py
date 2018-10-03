from page_and_url import Page, Url
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
from mimetypes import MimeTypes
from my_crawl import My_Crawl

class My_Focused_Crawl(My_Crawl):
    ''' focused crawl class, use priority queue to store promised url '''

    def __init__(self):
        My_Crawl.__init__(self)
        self.queue = [] # store Url class
        self.promise_update_time = {} # latest update time of promise in queue
    
    def calculate_promise(self, url, text, relevance_score, link_number):
        word_set = set()
        for search_term in self.search_terms:
            if re.search(search_term, text, re.IGNORECASE):
                word_set.add(search_term)
            if re.search(search_term, url, re.IGNORECASE):
                word_set.add(search_term)

        if url in self.promise:
            old_promise = self.promise[url]
        else:
            old_promise = 0

        new_promise = 0
        if len(word_set) == 1:
            new_promise += 1
        elif len(word_set) > 1:
            new_promise += 10
        
        new_promise = new_promise * 0.8 + old_promise * 0.8

        new_promise += relevance_score / np.sqrt(link_number)
        if new_promise > self.MAX_PROMISE:
            new_promise = self.MAX_PROMISE

        return new_promise
    
    def top(self):
        ''' return the top value '''
        while len(self.queue) > 0:
            current = heapq.heappop(self.queue)
            url = current.url
            update_time = current.update_time
            if update_time != self.promise_update_time[url]:
                continue
            self.add_to_queue(current)
            return current

    def add_to_queue(self, item):
        ''' add url with promise to priority queue '''
        self.promise[item.url] = item.promise
        self.promise_update_time[item.url] = item.update_time # update the promise time

        heapq.heappush(self.queue, item)

    def pop_from_queue(self):
        ''' pop and return the top value '''
        self.top()
        return heapq.heappop(self.queue)

    def queue_size(self):
        self.top()
        return len(self.queue)