### File structure

- util.py : some help function(eg. google search)
- search_util.py : some utility class and function
- page_and_url.py : define the page and url class needed
- main.py : entrance of the program, reading search type and search terms from stdin, then run crawling
- my_focused_crawl.py : define the focused crawl classes
- my_bfs_crawl.py : define the bfs crawl classes
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

