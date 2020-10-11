import glob
import ijson
from simple_item_store import SimpleItemStore
from tqdm import tqdm


class NepaliCorpusPreProcessor(object):
    """ Original Code: https://brett.is/writing/about/generator-pipelines-in-python/ 
    """

    def __init__(self, data_folder_path):
        self._data_folder_path = glob.glob(data_folder_path)
        self._storage = dict()
        self._storage_options = {type(set()), type(list()), type(str()), type(SimpleItemStore())}
        self._filters = []


    def add_filter(self, new_filter, storage=None):
        if callable(new_filter):
            self._filters.append(new_filter)
            if storage is not None:
                if type(storage) in self._storage_options:
                    self._storage[new_filter.__name__] = storage


    def process(self):
        # this is the pattern for creating a generator
        # pipeline, we start with a generator then wrap
        # each consecutive generator with the pipeline itself
        pipeline = self._data_folder_path
        for new_filter in self._filters:
            storage = self._storage.get(new_filter.__name__)
            if storage is not None:
                pipeline = new_filter(pipeline, storage)
            else:
                pipeline = new_filter(pipeline)
        return pipeline



def load_news_data(file_path_list):

    for file_path in file_path_list:
        print (f"Working with: {file_path}")

        with open(file_path, "rb") as file:
            filter = "item.sentences.item"
            json_stream = ijson.items(file, filter)
            for item in json_stream:
                yield item


def unique_sentences(sentences, storage):
    with open('data/sanitized/unique_sentences.txt', 'w') as file:
        for sentence in sentences:
            if sentence not in storage:
                storage.add(sentence)
                file.write(f"{sentence}\n")
            
            yield sentence


processor = NepaliCorpusPreProcessor("data/unsanitized/*.json")

# this is the order we want the functions to run
processor.add_filter(load_news_data)
processor.add_filter(unique_sentences, storage=SimpleItemStore())

# process() returns the generator pipeline
counter = 0
for line in tqdm(processor.process()):
    # line with be a dict whose status is
    # 200 and method is 'GET' and whose
    # size is expressed in megabytes
    counter += 1