from string import punctuation
import ijson
from tqdm import tqdm
from simple_item_store import SimpleItemStore
from simple_data_pipeline import SimpleDataPipeline
from nepali_tokenizer import NepaliTokenizer
from data.language_data.stopwords import stopwords
from data.language_data.alphabhet_and_characters import alphabhet


def load_news_data(file_path_list):
    for file_path in file_path_list:
        print (f"\nWorking with: {file_path}")

        with open(file_path, "rb") as file:
            filter = "item.sentences.item"
            json_stream = ijson.items(file, filter)
            for item in json_stream:
                yield item


def sanitize_sentence(sentences, tokenizer, word_filter_set):
    for sentence in sentences:
        tokenized_sentence = tokenizer.word_tokenize(sentence)
        yield " ".join([word for word in tokenized_sentence if word not in word_filter_set])
        

def unique_sentences(sentences, storage):
    with open('data/sanitized/unique_sentences_trial.txt', 'w') as file:
        for sentence in sentences:
            if sentence not in storage:
                storage.add(sentence)
                file.write(f"{sentence}\n")
            yield sentence


processor = SimpleDataPipeline("data/unsanitized/*.json")

# this is the order we want the functions to run
processor.add_filter(new_filter=load_news_data)

filter_words = [*stopwords, *alphabhet['number'], *alphabhet['punctuation']]
processor.add_filter(new_filter=sanitize_sentence, args=[NepaliTokenizer(), set(filter_words)])

processor.add_filter(new_filter=unique_sentences, storage=SimpleItemStore())

# process() returns the generator pipeline
counter = 0
for line in tqdm(processor.process()):
    # line with be a dict whose status is
    # 200 and method is 'GET' and whose
    # size is expressed in megabytes
    counter += 1