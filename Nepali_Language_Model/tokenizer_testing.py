from tokenizers.implementations import ByteLevelBPETokenizer
from tokenizers.processors import BertProcessing
from transformers import LineByLineTextDataset


tokenizer = ByteLevelBPETokenizer(
    "./models/nepali_BERT_tokenizer_L-vocab.json",
    "./models/nepali_BERT_tokenizer_L-merges.txt",
)
# tokenizer._tokenizer.post_processor = BertProcessing(
#     ("</s>", tokenizer.token_to_id("</s>")),
#     ("<s>", tokenizer.token_to_id("<s>")),
# )
# tokenizer.enable_truncation(max_length=512)

# original = "क्षमता विकासको"
# encoded = tokenizer.encode(original)
# decoded = tokenizer.decode(encoded.ids)

# print(f"original: {original}")
# print(f"encoded: {encoded.tokens}")
# print(f"decoded: {decoded}")



dataset = LineByLineTextDataset(
tokenizer = tokenizer,
file_path="../Data/nepali_corpus/sanitized_data/sentences/master_lists/master_paragraph_list.txt", #this path is from step 1
block_size=128,)


#Need this util for data back propagation 
from transformers import DataCollatorForLanguageModeling

data_collator = DataCollatorForLanguageModeling(
tokenizer=tokenizer, mlm=True, mlm_probability=0.15)


#Set up training arguments
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./models/language_models", #this dir name is from step 1
    overwrite_output_dir=True,
    num_train_epochs=10,#change epoch values as you need.more the number longer it takes to train.
    per_gpu_train_batch_size=8, #decrease this number for out of memory issues
    save_steps=10_000,
    save_total_limit=2,
)


#Define trainer object with above training args
trainer = Trainer(
    model=None,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset,
    prediction_loss_only=True,
)

#trigger the training 
trainer.train()#save the model in local directory
trainer.save_model("./models/language_models")