import urllib
from bs4 import BeautifulSoup
import requests
import webbrowser
from urlparse import urlparse
import search_util
import re

def get_top_10_result(links):
    used_hostname = []
    top_10_result = []

    for link in links:
        parsed_link = urlparse(link)
        hostname = parsed_link.hostname
        if hostname in used_hostname:
            continue
        if search_util.page_visible(link) == False:
            continue
        top_10_result.append(link)
        used_hostname.append(hostname)

        if len(top_10_result) >= 10:
            break
    return top_10_result

def get_google_results(search_term):
    result = []

    results = 50 # valid options 10, 20, 30, 40, 50, and 100
    page = requests.get("https://www.google.com/search?q={}&num={}".format(search_term, results))
    soup = BeautifulSoup(page.content, "html5lib")
    links = soup.findAll("a")
    for link in links :
        link_href = link.get('href')
        if "url?q=" in link_href and not "webcache" in link_href:
            result.append(link.get('href').split("?q=")[1].split("&sa=U")[0])

    return result

def get_google_top_10_search_result(search_term):
    return get_top_10_result(get_google_results(search_term))
