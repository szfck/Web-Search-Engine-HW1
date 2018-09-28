### File structure

- google_search_helper.py : used to get top 10 result from google search
- search_util.py : some utility class and function
- my_queue.py : define the queues used in crawl
- my_crawl.py : define the crawl classes
- main.py : entrance of the program, reading search type and search terms from stdin, then run crawling
- run.sh : bash script to run 2 queries
- output/*.log : store logs running 2 queries

### How to run (python 2.7)

- run scirpt for both query and search type
```
./run.sh
```

- or run main.py
```
python main.py f wildfires california
python main.py b wildfires california
```

