import xxhash
import zlib

class SimpleItemStore():

    item_store = set()
    xxhash_seed = 420

    def __init__(self, xxhash_seed=None):
        if xxhash_seed:
            self.xxhash_seed = xxhash_seed


    def __iter__(self):
        return self.item_store.__iter__


    def __len__(self):
        return self.item_store.__len__


    def __contains__(self, text):
        return xxhash.xxh3_64_intdigest(text, seed=self.xxhash_seed) in self.item_store


    def add(self, text):
        self.item_store.add(xxhash.xxh3_64_intdigest(text, seed=self.xxhash_seed))


    def delete(self, text):
        self.item_store.discard(text)
    

    def flush(self):
        self.item_store = set()
    

    def add_adler(self, text):
        self.item_store.add(zlib.adler32(bytes(text, 'utf-8')))


    def add_xx3(self, text):
        self.item_store.add(xxhash.xxh3_64_intdigest(text, seed=self.xxhash_seed))