import sys
import ijson
from tqdm import tqdm
from .simple_key_value_store import SimpleKeyValueStore
from .simple_item_store import SimpleItemStore
from .helpers import humansize, total_size
from time import perf_counter 


def load_news_data_generator(file, items=None):
    with open(file, "rb") as file:
        json_stream = ijson.items(file, 'item.sentences.item')
        for item in json_stream:
            yield item


def item_store_time_perf(file):
    item_store = SimpleItemStore()

    time = []
    for sentence in tqdm(load_news_data_generator(file)):
        start = perf_counter()
        item_store.add_adler(sentence)
        stop = perf_counter()
        time.append(stop - start)

    avg_xx3 = sum(time)/len(time)

    time = []
    for sentence in tqdm(load_news_data_generator(file)):
        start = perf_counter()
        item_store.add_xx3(sentence)
        stop = perf_counter()
        time.append(stop - start)

    avg_adler = sum(time)/len(time)

    return (avg_xx3, avg_adler)


def item_store_size_perf(file):
    item_store = SimpleItemStore()

    for sentence in tqdm(load_news_data_generator(file)):
        item_store.add_adler(sentence)

    adler_size = total_size(item_store.item_store)
    item_store.flush()

    for sentence in tqdm(load_news_data_generator(file)):
        item_store.add_xx3(sentence)

    xx3_size = total_size(item_store.item_store)

    return (xx3_size, adler_size)



def main():
    xx_bucket = []
    adler_bucket = []
    for i in range(5):
        xx3, adler = item_store_time_perf("data/nepali_news_crawl_news24nepal.json")
        xx_bucket.append(xx3)
        adler_bucket.append(adler)
    
    print(f"item_store.add_adler() avg time: {sum(adler_bucket)/len(adler_bucket)}")
    print(f"item_store.add_xx3() avg time: {sum(xx_bucket)/len(xx_bucket)}")

    # print(f"item_store.add_adler() avg space: {humansize(sum(adler_bucket)/len(adler_bucket))}")
    # print(f"item_store.add_xx3() avg space: {humansize(sum(xx_bucket)/len(xx_bucket))}")


main()