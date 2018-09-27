from focused_crawl import Focused_Crawl
from bfs_crawl import Bfs_Crawl
import sys

if __name__ == '__main__':
    search_type = sys.argv[1]
    search_terms = sys.argv[2:]

    if search_type[0] == 'f':
        crawl = Focused_Crawl(search_terms)
    else:
        crawl = Bfs_Crawl(search_terms)

    crawl.start_crawl(10)

