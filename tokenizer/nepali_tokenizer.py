import re
from string import punctuation
from icu import Locale, BreakIterator
from .byakaran.regex import not_word_re

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


    def word_tokenize(self, sentence):
        """This function tokenize with respect to word.

        Utilizes the grammar built by @tnagorra for https://github.com/tnagorra/nepali-text-extraction
        
        Arguments:
            sentence {string} -- sentence you want to tokenize
        
        Returns:
            list -- tokenized words
        """
        boundaries = [(m.start(0), m.end(0)) for m in not_word_re.finditer(sentence)]
        tokenized_sentence = []
        start_index = 0
        end_index = 0
        for counter, match in enumerate(boundaries):
            if counter > 0:
                start_index = end_index + 1 # Previous loop's end_index. Adding 1 to get the correct index for slicing.
            
            end_index = match[0]
            tokenized_sentence.append(sentence[start_index:end_index])
            
            delimeter = sentence[match[0]:match[1]].strip()
            if delimeter != '':
                tokenized_sentence.append(delimeter)
        
        return tokenized_sentence


    def simple_word_tokenize(self, sentence, new_punctuation=[]):
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