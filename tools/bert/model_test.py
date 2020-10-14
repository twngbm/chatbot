from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader
import torch
import transformers
from transformers import BertTokenizer
import os
import pandas as pd
from torch.utils.data import Dataset
from transformers import BertForSequenceClassification
import time
from bert import DataLoader, create_mini_batch, get_predictions, CCDataset

model = BertForSequenceClassification.from_pretrained("./modelSave")

PRETRAINED_MODEL_NAME = "bert-base-chinese"
tokenizer = BertTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)
testset = CCDataset("test", tokenizer=tokenizer)
testloader = DataLoader(testset, batch_size=256,
                        collate_fn=create_mini_batch)
predictions = get_predictions(model, testloader)
index_map = {v: k for k, v in testset.label_map.items()}

# 生成 Kaggle 繳交檔案
df = pd.DataFrame({"Category": predictions.tolist()})
df['Category'] = df.Category.apply(lambda x: index_map[x])
df_pred = pd.concat([testset.df.loc[:, ["Id"]],
                     df.loc[:, 'Category']], axis=1)
df_pred.to_csv('bert_1_prec_training_samples.csv', index=False)
df_pred.head()
