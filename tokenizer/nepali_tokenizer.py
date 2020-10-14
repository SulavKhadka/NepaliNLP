import re
from string import punctuation
from icu import Locale, BreakIterator
from .byakaran.regex import not_word_re, word_re
from language_data.alphabhet_and_characters import punctuation_char
from ahocorapy.keywordtree import KeywordTree

#From https://github.com/sushil79g/Nepali_nlp/blob/master/Nepali_nlp/Nepali_tokenizer.py
class NepaliTokenizer:
    def __init__(self):
        self.punctuation_signs = set(punctuation_char)
        self.kwtree = self.build_tree()


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


    def word_tokenize(self, sentence, with_delimeter=True):
        """This function tokenize with respect to word.

        # FIXME: Doesnt capture the last word of a sentence in some circumstances!!
        Utilizes the grammar built by @tnagorra for https://github.com/tnagorra/nepali-text-extraction
        
        Arguments:
            sentence {string} -- sentence you want to tokenize
            with_delimeter {bool} -- True if you want to preserve punctuation as they can be a part of the word boundary in regex.
        
        Returns:
            list -- tokenized words
        """
        if with_delimeter:
            tokenized_sentence = []
            start_index = 0
            end_index = 0
            for boundary in not_word_re.finditer(sentence):
                left_boundary = boundary.start(0)
                right_boundary = boundary.end(0)
                end_index = left_boundary

                token = sentence[start_index:end_index].strip()
                delimeter = sentence[left_boundary:right_boundary].strip()

                if token != '':
                    tokenized_sentence.append(token)
                if delimeter != '':
                    tokenized_sentence.append(delimeter)
                
                start_index = right_boundary

            return tokenized_sentence
        
        return word_re.findall(sentence)



    def word_tokenize_ahocorapy(self, sentence):
        # TODO: This is slow; inverse this list to see what you get back
        results = self.kwtree.search_all(sentence)
        tokenized_sentence = []
        sentence_length = len(sentence)
        start_token_index = 0
        end_token_index = 0
        previous_token_index = 0
        for result in results:
            current_token_index = result[1]
            token_distance = current_token_index - previous_token_index

            if token_distance > 1:
                end_token_index = previous_token_index + 1

                word = sentence[start_token_index:end_token_index]
                delimeter = sentence[(previous_token_index + 1):current_token_index]

                tokenized_sentence.append(word)
                tokenized_sentence.append(delimeter)

                start_token_index = current_token_index
                end_token_index = None
            
            previous_token_index = current_token_index
        
        if previous_token_index != sentence_length - 1:
            end_token_index = previous_token_index + 1

        # cant combine the two if statements, because the `if` above can manipulate end_token_index which the `if` below needs.    
        if end_token_index:
            tokenized_sentence.append(sentence[start_token_index:end_token_index])
            tokenized_sentence.append(sentence[(previous_token_index + 1):sentence_length])
        else:
            tokenized_sentence.append(sentence[start_token_index:])
        
        tokenized_sentence = [i for i in tokenized_sentence if i.strip() != '']

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

    @staticmethod
    def build_tree():
        kwtree = KeywordTree()
        word = "क़ख़ग़ज़ड़ढ़फ़य़ऩऱॿॾॼॻकखगघङचछजझञटठडढणतथदधनपफबभमयरऱलळवशषसह़ािीुूृॅॆेैॉॊोौऻऺॄॆॏॗॖॢॣ्\u200d\u200cॷॶॵॴॳॲअआइईउऊऋऍऎएऐऑऒओऔॠऌॡँंःॐऽॱ॰१२३४५६७८९०^"
        for i in word:
            kwtree.add(i)
        kwtree.finalize()
        return kwtree


    def __str__(self):
        return "Helps to tokenize content written in Nepali language." 


if __name__ == "__main__":
    np = NepaliTokenizer()
    print(np.word_tokenize("असोज २२ मा बसेको मन्त्रिपरिषद् बैठकले मदिरा आयातमा लगाइएको प्रतिबन्ध फुकुवा गरेको सरकारका प्रवक्ता एवं परराष्ट्रमन्त्री प्रदीप ज्ञवालीले जानकारी दिए ।"))