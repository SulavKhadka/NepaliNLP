from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor

class NepaliNewsCrawler(CrawlSpider):
    name = "Nepali_News_Crawler"
    start_urls = ["https://ekantipur.com/"]
    allowed_domains = ["ekantipur.com", "onlinekhabar.com", "nagariknews.nagariknetwork.com", "ratopati.com", "setopati.com", "newsofnepal.com", "gorkhapatraonline.com", "nayapatrikadaily.com", "aarthiknews.com"]
    download_delay = 0.7
    rules = [Rule(LinkExtractor(canonicalize=True, unique=True),
                      callback='parse', 
                      follow=True)]


    def extract_p_tag_text(self, response):
        # Parsing the html to extract all text from <p> tags
        text = ""
        for p_tag in response.xpath('.//p'):
            p_tag_text_list = [] 
            for line in p_tag.xpath('.//text()').extract():
                if line:
                    line = line.strip()
                    if line:
                        p_tag_text_list.append(line)

            p_tag_text = " ".join(p_tag_text_list)
            if p_tag_text:
                if p_tag_text.strip():
                    text = f"{text}\n{p_tag_text}"
        
        return text
    

    def extract_all_links(self, response, filter_allowed_domains = False):
        page_links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        domain_links = []
        for link in page_links:
            if filter_allowed_domains:
                # filtering out any link that isnt in allowed_domains
                for allowed_domain in self.allowed_domains:
                    if allowed_domain in link.url:
                        domain_links.append(link)
            else:
                domain_links.append(link)
        
        return domain_links


    def parse(self, response):        
        tokenizer = NepaliTokenizer()
        parser = NepaliParser()

        text = self.extract_p_tag_text(response)
        
        sanitized_text = []
        sentences = tokenizer.sentence_tokenize(text)
        # print(f"Unsanitized Sentences:\n{sentences}")
        for sentence in sentences:
            sanitized_sentence = parser.sanitize_sentence(sentence)

            if sanitized_sentence:
                if len(sanitized_sentence.strip()) != 0:
                    sanitized_text.append(sanitized_sentence)
                    

        # print(f"Sanitized Sentences:\n{sanitized_text}")
        yield {"url" : response.request.url, "num_of_sentences": len(sanitized_text), "sentences": sanitized_text}
        
        # TODO: Do language recognition and replacement in a way it doesnt affect the sentence structure (whitespacing and stuff)
        # TODO: Check to see if there is a way to preserve quotes from text. Could be useful for language models as quotes from various sources are common in language
        # TODO: Nepali: False || WHO: ['W', 'H', 'O'] = might need a NER for english to identify and save information that has english letters to represent english companites/entities


from string import punctuation

class NepaliParser():

    punctuation_set = {'।', ',', ';', '?', '!', '—', '-', '.'}
    special_character_set = {u'–', u'र्\u200d', u'द्\u200d', 'ञ्\u200d'} # This is here for special characters that matters for nepali words but werent captured by the punctuation or the unicode range
    unified_punctuation_set = {}

    def __init__(self, external_character_set = None):
        if external_character_set:
            self.special_character_set = self.special_character_set.union(external_character_set)

        self.unified_punctuation_set = self.punctuation_set.union(self.special_character_set)


    def is_Devanagari(self, word):
        for character in word:
            if ((u'\u0900' > character) or (character > u'\u097F')) and ((character not in self.punctuation_set) or (character not in self.special_character_set)):
                return False
        return True


    def remove_non_devanagari_characters(self, text):
        tidy_text = ""
        for character in text:
            if (u'\u0900' <= character <= u'\u097F') or (character in self.punctuation_set) or (character in self.special_character_set):
                tidy_text += character

        if len(tidy_text) == 0:
            return None
        
        return tidy_text
    

    def sanitize_sentence(self, sentence, word_tokenized = False):
        tokenizer = NepaliTokenizer()
        word_tokenized_sentence = []
        words = tokenizer.word_tokenize(sentence)
        for word in words:
            is_devanagari = self.is_Devanagari(word)
            # print(f"Nepali: {is_devanagari} || {word}: {word_split[counter]}")
            if is_devanagari:
                word_tokenized_sentence.append(word)
            else:
                sanitized_word = self.remove_non_devanagari_characters(tokenizer.character_tokenize(word))
                if sanitized_word is not None:
                    if len(sanitized_word.strip()) != 0:
                        word_tokenized_sentence.append(sanitized_word)
                

        if len(word_tokenized_sentence) != 0:
            if word_tokenized:
                return word_tokenized_sentence
            
            sanitized_sentence = self.word_tokenized_sentence_to_text(word_tokenized_sentence)
            return sanitized_sentence


    def word_tokenized_sentence_to_text(self, word_tokenized_sentence):
        sentence = ""
        if word_tokenized_sentence is None:
            return None

        for word in word_tokenized_sentence:
            if word is not None:
                if word in self.punctuation_set:
                    sentence = f"{sentence}{word}"
                else:
                    sentence = f"{sentence} {word}"
        
        return sentence



import re
from string import punctuation
from icu import BreakIterator, Locale

#From https://github.com/sushil79g/Nepali_nlp/blob/master/Nepali_nlp/Nepali_tokenizer.py
class NepaliTokenizer:
    def __init__(self):
        pass


    def sentence_tokenize(self, text, new_punctuation=[]):
        """This function tokenize the sentences
        
        Arguments:
            text {string} -- Sentences you want to tokenize
        
        Returns:
            sentence {list} -- tokenized sentence in list
        """
        ## TODO: Sulav's custom sentence tokenizer. This comment is so I can remember to fork and edit the original repo(linked above) instead of doing this.
        split_sentences = re.split(r'(\।|\?|\!)+', text)
        tokenized_sentences = []
        for sentence in split_sentences:
            if (len(sentence) == 0) or (sentence is None):
                pass #skipping over empty strings
            elif sentence in {u"।", u"?", u"!"}: # re.split() separates the delimeter as a new element in the list. This checks for those elements and adds them to the sentence before it
                # TODO: This if-else block below seems more complex than it needs to be. 
                if len(tokenized_sentences) == 0:
                    tokenized_sentences.append(sentence)
                elif tokenized_sentences[-1] == None:
                    tokenized_sentences[-1] = sentence
                else:
                    try:
                        tokenized_sentences[-1] += sentence
                    except:
                        #TODO: Log this stuff
                        print(f"couldnt join {sentence} to previous sentence.")
                        print(f"tokenized_sentences list length: {len(tokenized_sentences)}")
            else:
                tokenized_sentences.append(sentence)
        return tokenized_sentences


    def word_tokenize(self, sentence, new_punctuation=[]):
        """This function tokenize with respect to word
        
        Arguments:
            sentence {string} -- sentence you want to tokenize
            new_punctuation {list} -- more punctutaion for tokenizing  default ['।',',',';','?','!','—','-']
        
        Returns:
            list -- tokenized words
        """
        punctuations = ['।', ',', ';', '?', '!', '—', '-', '.']
        if new_punctuation:
            punctuations = set(punctuations + new_punctuation)
        for punct in punctuations:
            sentence_split = sentence.split(punct)
            if sentence != sentence_split[0]: # checking if the split didnt find anything. If it didnt the result is [sentence, '']
                sentence = f" {punct} ".join(sentence_split)

        return sentence.split()


    def character_tokenize(self, word):
        """ Returns the tokenization in character level.
        
        Arguments:
            word {string} -- word to be tokenized in character level.
        
        Returns:
            [list] -- list of characters.
        """

        temp_ = BreakIterator.createCharacterInstance(Locale())
        temp_.setText(word)
        char = []
        i = 0
        for j in temp_:
            s = word[i:j]
            char.append(s)
            i = j

        return char


    def __str__(self):
        return "Helps to tokenize content written in Nepali language."        