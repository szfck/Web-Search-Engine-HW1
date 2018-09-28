import heapq
import Queue

# Abstract Class of self defined Queue
class My_Queue:

    def add(self, item):
        ''' abstract method, add item to the queue '''
        raise NotImplementedError("Please Implement this method")
    
    def top_and_pop(self):
        ''' abstract method, get the top item of the queue and pop it '''
        raise NotImplementedError("Please Implement this method")

    def size(self):
        ''' abstract method, return the size of the queue '''
        raise NotImplementedError("Please Implement this method")

# Priority Queue Implementation
class My_Priority_Queue(My_Queue):
    
    def __init__(self):
        self.max_heap = []

    def add(self, item):
        heapq.heappush(self.max_heap, item)

    def top_and_pop(self):
        return heapq.heappop(self.max_heap)

    def size(self):
        return len(self.max_heap)

# First in First out Queue implementation
class My_FIFO_Queue(My_Queue):
    
    def __init__(self):
        self.queue = Queue.Queue()

    def add(self, item):
        self.queue.put(item)

    def top_and_pop(self):
        return self.queue.get()

    def size(self):
        return self.queue.qsize()

