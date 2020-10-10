import zlib

class SimpleItemStore():

    item_store = set()
    xxhash_seed = 420

    def __init__(self):
        pass

    def __len__(self):
        return(len(self.item_store))


    def __contains__(self, text):
        return self.hash(text) in self.item_store

    
    def add(self, text):
        self.item_store.add(zlib.adler32(bytes(text, 'utf-8')))


    def delete(self, text):
        self.item_store.discard(text)
    

    def flush(self):
        self.item_store = set()