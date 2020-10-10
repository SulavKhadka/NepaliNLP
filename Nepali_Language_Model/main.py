from tokenizers import ByteLevelBPETokenizer, SentencePieceBPETokenizer
import glob


def main():

    file_paths = glob.glob("../Data/nepali_corpus/sanitized_data/sentences/*.txt")
    print(file_paths)
    build_tokenizer(file_paths, vocab_size=50_000, output_file="nepali_BERT_tokenizer")


def build_tokenizer(file_paths, vocab_size, output_file="UNKNOWN_BERT_tokenizer"):
    tokenizer = ByteLevelBPETokenizer()
    # tokenizer = SentencePieceBPETokenizer(vocab_file=None, unk_token="<unk>")
    tokenizer.train(files=file_paths, vocab_size=vocab_size, min_frequency=2, special_tokens=["<s>", "<pad>", "</s>", "<unk>", "<mask>"])
    tokenizer.save_model(".", output_file)


main()