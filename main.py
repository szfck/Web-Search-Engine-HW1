import my_crawl
import sys

# entrance of program
if __name__ == '__main__':
    search_type = sys.argv[1] # get search type, 'f' means focused crawl and 'b' means bfs search
    search_terms = sys.argv[2:] # get search term list

    if search_type[0] == 'f':
        # use focused search crawl
        crawl = my_crawl.My_Focused_Crawl(search_terms)
    else:
        # use bfs search crawl
        crawl = my_crawl.My_Bfs_Crawl(search_terms)

    # search 1000 pages with 15 minutes
    crawl.start_crawl(1000, 60 * 15)

