import sys
from my_focused_crawl import My_Focused_Crawl
from my_bfs_crawl import My_Bfs_Crawl

# entrance of program
if __name__ == '__main__':
    search_type = sys.argv[1] # get search type, 'f' means focused crawl and 'b' means bfs search
    search_terms = sys.argv[2:] # get search term list

    if search_type[0] == 'f':
        # use focused search crawl
        crawl = My_Focused_Crawl()
    else:
        # use bfs search crawl
        crawl = My_Bfs_Crawl()

    # search 1000 pages within 30 minutes
    limit_size = 1000
    limit_time = 60 * 30
    crawl.start_crawl(search_terms, limit_size, limit_time)

