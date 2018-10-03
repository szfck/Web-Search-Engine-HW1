import numpy as np
from bs4 import BeautifulSoup
from bs4.element import Comment
import re

class cosine_measure_strategy:
    def __init__(self, search_terms):
        self.search_terms = search_terms
        self.doc_number = 0 # total number of document
        self.word_freq = {} # total number of occurences of t in the collection

    def add(self, word_count):
        self.doc_number += 1
        for word in word_count:
            if word in self.word_freq:
                self.word_freq[word] += word_count[word]
            else:
                self.word_freq[word] = word_count[word]
    
    def cosine_measure(self, word_count, doc_len):
        # calculate score using cosine measure
        # w_q_t * w_d_t / sqrt(doc_len)
        # w_q_t = ln(1 + doc_number / f_t)
        # w_d_t = 1 + ln(fdt)
        score = 0.0
        for word in word_count:
            w_q_t = np.log(1 + 1.0 * self.doc_number / self.word_freq[word])
            w_d_t = 1 + np.log(word_count[word])
            word_score = w_q_t * w_d_t / np.sqrt(doc_len)
            # print ('w_q_t {}, w_d_t {}, word_score {}'.format(w_q_t, w_d_t, word_score))
            score += word_score
        return score
        # if len(word_count) == len(self.search_terms):
        #     return 1
        # else:
        #     return 0
    
    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def get_relevance(self, texts):
        visible_texts = filter(self.tag_visible, texts)  
        word_count = {}
        for t in texts:
            for search_term in self.search_terms:
                if re.search(search_term, t, re.IGNORECASE):
                    if search_term in word_count:
                        word_count[search_term] += 1
                    else:
                        word_count[search_term] = 1

        doc_len = len(visible_texts)
        self.add(word_count)

        if doc_len <= 0:
            return 0
        else:
            return self.cosine_measure(word_count, doc_len)
    