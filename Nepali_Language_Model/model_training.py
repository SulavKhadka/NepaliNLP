from tokenizers.implementations import ByteLevelBPETokenizer
from transformers import LineByLineTextDataset

# config = RobertaConfig(
#     vocab_size=52_000,
#     max_position_embeddings=514,
#     num_attention_heads=12,
#     num_hidden_layers=6,
#     type_vocab_size=1,
# )

tokenizer = ByteLevelBPETokenizer(
    "./models/nepali_BERT_tokenizer_L-vocab.json",
    "./models/nepali_BERT_tokenizer_L-merges.txt",
)


dataset = LineByLineTextDataset(
tokenizer = tokenizer,
file_path="../Data/nepali_corpus/sanitized_data/sentences/master_sentence_list.txt", #this path is from step 1
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