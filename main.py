import my_crawl
import sys

if __name__ == '__main__':
    search_type = sys.argv[1]
    search_terms = sys.argv[2:]

    if search_type[0] == 'f':
        crawl = my_crawl.My_Focused_Craw(search_terms)
    else:
        crawl = my_crawl.My_Bfs_Craw(search_terms)

    crawl.start_crawl(10)

