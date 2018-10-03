import urllib, htmllib, formatter
from bs4 import BeautifulSoup
import datetime, time
import requests
import webbrowser
import re
import urlparse

def get_google_results(search_term, size):
    ''' given search_term string, get the search result from google '''
    result = []
    hostnames = set()

    results = 100 # valid options 10, 20, 30, 40, 50, and 100
    page = requests.get("https://www.google.com/search?q={}&num={}".format(search_term, results))
    soup = BeautifulSoup(page.content, "html5lib")
    links = soup.findAll("a")
    # print (links)
    for link in links :
        link_href = link.get('href')
        if "url?q=" in link_href and not "webcache" in link_href:
            link = link.get('href').split("?q=")[1].split("&sa=U")[0]
            hostname = get_hostname(link)
            print (hostname)
            if hostname not in hostnames: # each host only exist once
                hostnames.add(hostname)
                result.append(link)
        if len(result) >= size:
            break

    return result

def get_hostname(url):
    ''' given url, return hostname in url '''
    parsed_url = urlparse.urlparse(url)
    return parsed_url.hostname

def get_current_time_in_seconds():
    t = datetime.datetime.now()
    return time.mktime(t.timetuple())
