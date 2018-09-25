import urllib2
def page_visible(url):
    try:
        response = urllib2.urlopen(url)
    except:
        return False;
    return True;