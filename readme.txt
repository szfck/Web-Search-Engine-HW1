### File structure

- util.py : some help function(eg. google search)
- page_and_url.py : define the page and url class needed
- main.py : entrance of the program, reading search type and search terms from stdin, then run crawling
- my_crawl.py: define the base crawl class, which has two child class below
- my_focused_crawl.py : define the focused crawl classes
- my_bfs_crawl.py : define the bfs crawl classes
- relevance_strategy.py: define cosine measure method
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

### not finished yet

- multi threading crawl
- robot.txt exclusion

### result for two queries

- wildfires california

    - bfs: during 1000 download pages, harvest_rate is 0.65

    - focused: during 1000 download pages, harvest_rate is 0.851

- brooklyn dodgers

   - bfs: during 1000 download pages, harvest_rate is 0.575

   - focused: during 1000 download pages, harvest_rate is 0.91

