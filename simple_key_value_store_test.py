import simple_key_value_json
import json

def load_sentence_generator():
    with open("data/nepali_news_crawl_gorkhapatra.json") as json_file:
        json.load(json_file)


def main():
    for i in load_sentence_generator():
        input(i)