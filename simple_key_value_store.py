import xxhash

class SimpleKeyValueStore():

    kv_store = dict()
    kv_store_length = 0

    def __init__(self):
        pass


    def __len__(self):
        return(len(self.kv_store_length))


    def get(self, key=None):
        if key:
            return self.kv_store.get(key)
        
        return None


    def set(self, text=None, key=None):
        if key:
            self.kv_store[key] = text
        if text:
            self.kv_store[self.hash(text)] = text
        self.kv_store_length += 1


    def delete(self, key=None, text=None):
        if key:
            self.kv_store.pop(key)
        if text:
            self.kv_store.pop(self.hash(text))
        self.kv_store_length -= 1


    def exists(self, text):
        if self.kv_store.get(self.hash(text)):
            return True
        else:
            return False


    def hash(self, text):
        return xxhash.xxh32_hexdigest(text)