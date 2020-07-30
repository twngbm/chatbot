from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
import os
import sys
# Downloads to ./data.zip (2GB) and extracts to ./data/
# data_utils.download_data_url("./") # iis-ckip
# data_utils.download_data_gdown("./") # gdrive-ckip
# To use GPU:
#    1. Install tensorflow-gpu (see Installation)
#    2. Set CUDA_VISIBLE_DEVICES environment variable, e.g. os.environ["CUDA_VISIBLE_DEVICES"] = "0"
#    3. Set disable_cuda=False, e.g. ws = WS("./data", disable_cuda=False)

# # Load model with GPU
# ws = WS("./data", disable_cuda=False)
# pos = POS("./data", disable_cuda=False)
# ner = NER("./data", disable_cuda=False)

class ckip:
    # To use CPU:
    def __init__(self, sentence_list):
        self.sentence_list = sentence_list
        self.ws = WS("./data")
        self.pos = POS("./data")
        self.ner = NER("./data")
    # def print_word_pos_sentence(self,word_sentence, pos_sentence):
    #     assert len(word_sentence) == len(pos_sentence)
    #     for word, pos in zip(word_sentence, pos_sentence):
    #         print(f"{word}({pos})", end="\u3000")
    #     print()
    #     return
    def GetKeyword(self):

        word_to_weight = {
            "網路": 1,
            "連線": 1,
            "宿舍": 1,
            "宿網": 2,
        }
        dictionary = construct_dictionary(word_to_weight)
        # print(dictionary)

        # sentence_list = [
        #     "我的網路有問題",
        #     "我的宿網路掛了",
        # ]
        word_sentence_list = self.ws(
            self.sentence_list,
            # sentence_segmentation=True, # To consider delimiters
            # segment_delimiter_set = {",", "。", ":", "?", "!", ";"}), # This is the defualt set of delimiters
            # recommend_dictionary = dictionary1, # words in this dictionary are encouraged
            coerce_dictionary = dictionary, # words in this dictionary are forced
        )
        pos_sentence_list = self.pos(word_sentence_list)
        entity_sentence_list = self.ner(word_sentence_list, pos_sentence_list)
        # Release memory
        #del self.ws
        #del self.pos
        #del self.ner

        for i, sentence in enumerate(self.sentence_list):
            # print()
            # print(f"'{sentence}'")
            # self.print_word_pos_sentence(word_sentence_list[i],  pos_sentence_list[i])
            # print("Keyword:",end=" ")
            # print(word_sentence_list[0])
            keyword = []
            for word in word_sentence_list[i]:
                if word in word_to_weight:
                    # print(word,end="******\n")
                    keyword.append(word)
            return keyword
            print()
            # for entity in sorted(entity_sentence_list[i]):
            #     print(entity)
