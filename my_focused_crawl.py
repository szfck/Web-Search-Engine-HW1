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
        self.queue = [] # priority queue to store Url class
        self.promise_update_time = {} # latest update time of promise in queue
    
    def calculate_promise(self, url, text, relevance_score, link_number):
        ''' calculate promise value for given link '''
        word_set = set()
        for search_term in self.search_terms:
            # anchor text contains search term
            if re.search(search_term, text, re.IGNORECASE):
                word_set.add(search_term)
            # url link contains search term
            if re.search(search_term, url, re.IGNORECASE):
                word_set.add(search_term)

        # promise value in old page
        if url in self.promise:
            old_promise = self.promise[url]
        else:
            old_promise = 0

        new_promise = 0
        if len(word_set) == 1:
            # add score by 1 if only 1 search term exist
            new_promise += 1
        elif len(word_set) > 1:
            # if more than 1 distince search terms exist, the promise 
            # value should be much larger than 1 search term
            # so I add 10 here
            new_promise += 10
        
        # consider the case that same link in two different pages
        # here I combine two promise value together
        new_promise = new_promise * 0.8 + old_promise * 0.8

        # the relevance score in the downloaded page also influence the promise score
        # But if the page has a lot of links, then the relevance score should 
        # distribute to each link, here I choose to divide by the squre root of link number 
        new_promise += relevance_score / np.sqrt(link_number)

        # new promise should larger than MAX_PROMISE value
        if new_promise > self.MAX_PROMISE:
            new_promise = self.MAX_PROMISE

        return new_promise
    
    def top(self):
        ''' return the top value '''
    
        while len(self.queue) > 0:
            current = heapq.heappop(self.queue)
            url = current.url
            update_time = current.update_time
            # use lazy deletion method here to get the top node
            # if the current node's update time is
            # not equal to url's latest promise update time
            # just ignore it
            if update_time != self.promise_update_time[url]:
                continue
            self.add_to_queue(current)
            return current

    def add_to_queue(self, item):
        ''' add url with promise to priority queue '''
        self.promise[item.url] = item.promise # update promise score
        self.promise_update_time[item.url] = item.update_time # update the promise update time

        heapq.heappush(self.queue, item)

    def pop_from_queue(self):
        ''' pop and return the top value '''
        self.top()
        return heapq.heappop(self.queue)

    def queue_size(self):
        self.top()
        return len(self.queue)