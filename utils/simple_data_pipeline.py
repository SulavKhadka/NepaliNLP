import glob
from .simple_item_store import SimpleItemStore
from .simple_key_value_store import SimpleKeyValueStore


class SimpleDataPipeline(object):
    """ Original Code: https://brett.is/writing/about/generator-pipelines-in-python/ 
    """

    def __init__(self, data_folder_path):
        self._data_folder_path = glob.glob(data_folder_path)
        self._storage = dict()
        self._storage_options = {type(set()), type(list()), type(str()), type(SimpleItemStore()), type(SimpleKeyValueStore())}
        self._filters = []


    def add_filter(self, *, args=None, new_filter=None, storage=None):
        if callable(new_filter):
            if args:
                self._filters.append((new_filter, args))
            else:
                self._filters.append((new_filter, None))
            
            if storage is not None:
                if type(storage) in self._storage_options:
                    self._storage[new_filter.__name__] = storage
                else:
                    #TODO: Pass back message that informs the user to use one of the options from self._storage
                    pass


    def process(self):
        # this is the pattern for creating a generator
        # pipeline, we start with a generator then wrap
        # each consecutive generator with the pipeline itself
        pipeline = self._data_folder_path
        for new_filter, args in self._filters:
            storage = self._storage.get(new_filter.__name__)
            if args:
                if storage is not None:
                    pipeline = new_filter(pipeline, storage, *args)
                else:
                    pipeline = new_filter(pipeline, *args)
            else:
                if storage is not None:
                    pipeline = new_filter(pipeline, storage)
                else:
                    pipeline = new_filter(pipeline)
        return pipeline