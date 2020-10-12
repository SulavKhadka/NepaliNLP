from string import punctuation
import ijson
from tqdm import tqdm
from utils.simple_item_store import SimpleItemStore
from utils.simple_data_pipeline import SimpleDataPipeline
from tokenizer.nepali_tokenizer import NepaliTokenizer
from language_data.stopwords import stopwords
from language_data.alphabhet_and_characters import number, punctuation_char
from tokenizer.byakaran.regex import number_token_re, unwanted_token_re



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
        sanitized_sentence = [word for word in tokenized_sentence if word not in word_filter_set if unwanted_token_re.fullmatch(word) is None]
        if len(sanitized_sentence) >= 5:
            yield " ".join(sanitized_sentence)
        

def unique_sentences(sentences, storage):
    with open('data/sanitized/unique_sentences.txt', 'w') as file:
        for sentence in sentences:
            if sentence not in storage:
                storage.add(sentence)
                file.write(f"{sentence}\n")
            yield sentence


processor = SimpleDataPipeline("data/unsanitized/*.json")

# this is the order we want the functions to run
processor.add_filter(new_filter=load_news_data)

processor.add_filter(new_filter=sanitize_sentence, args=[NepaliTokenizer(), set(stopwords)])

processor.add_filter(new_filter=unique_sentences, storage=SimpleItemStore())

# process() returns the generator pipeline
counter = 0
for line in tqdm(processor.process()):
    # line with be a dict whose status is
    # 200 and method is 'GET' and whose
    # size is expressed in megabytes
    counter += 1