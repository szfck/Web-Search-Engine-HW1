import heapq
import Queue

class My_Queue:

    def add(self, item):
        ''' abstract method '''
        raise NotImplementedError("Please Implement this method")
    
    def top_and_pop(self):
        ''' abstract method '''
        raise NotImplementedError("Please Implement this method")

    def size(self):
        ''' abstract method '''
        raise NotImplementedError("Please Implement this method")

class My_Priority_Queue(My_Queue):
    
    def __init__(self):
        self.max_heap = []

    def add(self, item):
        heapq.heappush(self.max_heap, item)

    def top_and_pop(self):
        return heapq.heappop(self.max_heap)

    def size(self):
        return len(self.max_heap)

class My_FIFO_Queue(My_Queue):
    
    def __init__(self):
        self.queue = Queue.Queue()

    def add(self, item):
        self.queue.put(item)

    def top_and_pop(self):
        return self.queue.get()

    def size(self):
        return self.queue.qsize()

