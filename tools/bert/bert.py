from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader
import torch
from transformers import BertTokenizer
import os
import pandas as pd
from torch.utils.data import Dataset
from transformers import BertForSequenceClassification
import time
print("PyTorch 版本：", torch.__version__)
PRETRAINED_MODEL_NAME = "bert-base-chinese"  # 指定繁簡中文 BERT-BASE 預訓練模型


BATCH_SIZE = 64
MAX_LENGTH = 30  # Max sentence Length
NUM_LABELS = 3
EPOCHS = 6  # Epochs Time

"""
實作一個可以用來讀取訓練 / 測試集的 Dataset，這是你需要徹底了解的部分。
此 Dataset 每次將 tsv 裡的一筆成對句子轉換成 BERT 相容的格式，並回傳 3 個 tensors：
- tokens_tensor：兩個句子合併後的索引序列，包含 [CLS] 與 [SEP]
- segments_tensor：可以用來識別兩個句子界限的 binary tensor
- label_tensor：將分類標籤轉換成類別索引的 tensor, 如果是測試集則回傳 None
"""


class CCDataset(Dataset):
    # 讀取前處理後的 tsv 檔並初始化一些參數
    def __init__(self, mode, tokenizer):
        import json
        assert mode in ["train", "test"]  # 一般訓練你會需要 dev set
        self.mode = mode
        # 大數據你會需要用 iterator=True
        self.df = pd.read_csv(mode + ".tsv", sep="\t").fillna("")

        self.len = len(self.df)
        with open("class.json", "r") as f:
            self.label_map = json.load(f)
        self.tokenizer = tokenizer  # 我們將使用 BERT tokenizer

    # 定義回傳一筆訓練 / 測試數據的函式
    def __getitem__(self, idx):
        if self.mode == "test":
            text_a = self.df.iloc[idx, 1]
            label_tensor = None
        else:
            text_a = self.df.iloc[idx, 0]
            label = self.df.iloc[idx, 1]

            # 將 label 文字也轉換成索引方便轉換成 tensor
            label_id = self.label_map[label]
            label_tensor = torch.tensor(label_id)

        # 把兩個句子串成一個句子輸入

        # 建立第一個句子的 BERT tokens 並加入分隔符號 [SEP]
        word_pieces = ["[CLS]"]
        tokens = self.tokenizer.tokenize(text_a)
        tokens = [x if x not in ["，", ","] else "[SEP]" for x in tokens]

        word_pieces += tokens
        len_a = len(word_pieces)

        # 將整個 token 序列轉換成索引序列
        ids = self.tokenizer.convert_tokens_to_ids(word_pieces)
        tokens_tensor = torch.tensor(ids)

        # 將第一句包含 [SEP] 的 token 位置設為 0，其他為 1 表示第二句
        x = 0
        st = []
        for i in word_pieces:
            st.append(x)
            if i == "[SEP]":
                x += 1

        segments_tensor = torch.tensor(st,
                                       dtype=torch.long)

        return (tokens_tensor, segments_tensor, label_tensor)

    def __len__(self):
        return self.len


"""
實作可以一次回傳一個 mini-batch 的 DataLoader
這個 DataLoader 吃我們上面定義的 `FakeNewsDataset`，
回傳訓練 BERT 時會需要的 4 個 tensors：
- tokens_tensors  : (batch_size, max_seq_len_in_batch)
- segments_tensors: (batch_size, max_seq_len_in_batch)
- masks_tensors   : (batch_size, max_seq_len_in_batch)
- label_ids       : (batch_size)
"""


# 這個函式的輸入 `samples` 是一個 list，裡頭的每個 element 都是
# 剛剛定義的 `FakeNewsDataset` 回傳的一個樣本，每個樣本都包含 3 tensors：
# - tokens_tensor
# - segments_tensor
# - label_tensor
# 它會對前兩個 tensors 作 zero padding，並產生前面說明過的 masks_tensors

def create_mini_batch(samples):
    tokens_tensors = [s[0] for s in samples]
    segments_tensors = [s[1] for s in samples]

    # 測試集有 labels
    if samples[0][2] is not None:
        label_ids = torch.stack([s[2] for s in samples])
    else:
        label_ids = None

    # zero pad 到同一序列長度
    tokens_tensors = pad_sequence(tokens_tensors,
                                  batch_first=True)
    segments_tensors = pad_sequence(segments_tensors,
                                    batch_first=True)

    # attention masks，將 tokens_tensors 裡頭不為 zero padding
    # 的位置設為 1 讓 BERT 只關注這些位置的 tokens
    masks_tensors = torch.zeros(tokens_tensors.shape,
                                dtype=torch.long)
    masks_tensors = masks_tensors.masked_fill(
        tokens_tensors != 0, 1)

    return tokens_tensors, segments_tensors, masks_tensors, label_ids


def get_predictions(model, dataloader, compute_acc=False):
    predictions = None
    correct = 0
    total = 0

    with torch.no_grad():
        # 遍巡整個資料集
        for data in dataloader:
            # 將所有 tensors 移到 GPU 上
            if next(model.parameters()).is_cuda:
                data = [t.to("cuda:0") for t in data if t is not None]

            # 別忘記前 3 個 tensors 分別為 tokens, segments 以及 masks
            # 且強烈建議在將這些 tensors 丟入 `model` 時指定對應的參數名稱
            tokens_tensors, segments_tensors, masks_tensors = data[:3]
            outputs = model(input_ids=tokens_tensors,
                            token_type_ids=segments_tensors,
                            attention_mask=masks_tensors)

            logits = outputs[0]
            _, pred = torch.max(logits.data, 1)

            # 用來計算訓練集的分類準確率
            if compute_acc:
                labels = data[3]
                total += labels.size(0)
                correct += (pred == labels).sum().item()

            # 將當前 batch 記錄下來
            if predictions is None:
                predictions = pred
            else:
                predictions = torch.cat((predictions, pred))
    print(predictions)
    if compute_acc:
        acc = correct / total
        return predictions, acc

    return predictions


if __name__ == "__main__":
    # dataCleanup()
    # testCleanup()
    # 初始化一個專門讀取訓練樣本的 Dataset，使用中文 BERT 斷詞
    tokenizer = BertTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)
    trainset = CCDataset("train", tokenizer=tokenizer)
    #trainset = FakeNewsDataset("train", tokenizer=tokenizer)

    # 初始化一個每次回傳 64 個訓練樣本的 DataLoader
    # 利用 `collate_fn` 將 list of samples 合併成一個 mini-batch 是關鍵
    trainloader = DataLoader(trainset, batch_size=BATCH_SIZE,
                             collate_fn=create_mini_batch)
    model = BertForSequenceClassification.from_pretrained(
        PRETRAINED_MODEL_NAME, num_labels=NUM_LABELS)

    # 讓模型跑在 GPU 上並取得訓練集的分類準確率
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("device:", device)
    model = model.to(device)

    # Train
    startTime = time.time()
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
    for epoch in range(EPOCHS):

        running_loss = 0.0
        for data in trainloader:

            tokens_tensors, segments_tensors, \
                masks_tensors, labels = [t.to(device) for t in data]

            # 將參數梯度歸零
            optimizer.zero_grad()

            # forward pass
            outputs = model(input_ids=tokens_tensors,
                            token_type_ids=segments_tensors,
                            attention_mask=masks_tensors,
                            labels=labels)

            loss = outputs[0]
            # backward
            loss.backward()
            optimizer.step()

            # 紀錄當前 batch loss
            running_loss += loss.item()

        # 計算分類準確率
        _, acc = get_predictions(model, trainloader, compute_acc=True)

        print('[epoch %d] loss: %.3f, acc: %.3f' %
              (epoch + 1, running_loss, acc))
    print("Take Time: ", time.time()-startTime)
    model.save_pretrained("./modelSave")
    # Test
