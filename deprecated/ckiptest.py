import asyncio
import csv
import warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
    #from ckipnlp.container import ParseClause, ParseTree
ITPrincipal = "ITPrincipal.csv"

with open(ITPrincipal, "r", encoding="utf-8-sig") as csvfile:
    rows = csv.reader(csvfile)
    header = next(rows)
    header[0] = "代號"
    header[6] = "業務負責人分機"
    header[8] = "系統負責人分機"
    header[9] = "備註"
    header = header[:10]

    ITinfotable = {}
    for row in rows:
        ITinfotable[row[1]] = dict(zip(header, row))
    ITinfotableKey = list(ITinfotable.keys())

ws = WS("./data")
pos = POS("./data")
#ner = NER("./data")
print("load done")
word_to_weight = {"VPN": 1, "成功入口": 1, "成功大學": 1, "校園授權軟體": 1}
for systemName in ITinfotableKey:
    word_to_weight[systemName] = 1
forced_word = {"成功入口": 1, "成功大學": 1}
encouraged_dictionary = construct_dictionary(word_to_weight)
forced_dictionary = construct_dictionary(forced_word)


async def ckip(sentence):
    sentence_list = [sentence]
    word_sentence_list = ws(
        sentence_list,
        sentence_segmentation=True,  # To consider delimiters
        # segment_delimiter_set = {",", "。", ":", "?", "!", ";"}), # This is the defualt set of delimiters
        # words in this dictionary are encouraged
        recommend_dictionary=encouraged_dictionary,
        coerce_dictionary=forced_dictionary,  # words in this dictionary are forced
    )

    pos_sentence_list = pos(word_sentence_list)
    mark = ['COLONCATEGORY', 'COMMACATEGORY', 'DASHCATEGORY', 'DOTCATEGORY', 'ETCCATEGORY',
            'EXCLAMATIONCATEGORY', 'PARENTHESISCATEGORY', 'PAUSECATEGORY', 'PERIODCATEGORY', 'QUESTIONCATEGORY',
            'SEMICOLONCATEGORY', 'SPCHANGECATEGORY', 'WHITESPACE']
    #entity_sentence_list = ner(word_sentence_list, pos_sentence_list)
    wanted_word = ["FW", "Na", "Nb", "Nc", "Ncd", "Nv"]
    droped_list = ["DE", "D", "Nh", "Cbb", "Caa", "Cab",
                   "Cba", "Da", "Dfa", "Dfb", "Di", "Dk", "DM", "I", "V_2"]+mark

    def print_word_pos_sentence(word_sentence, pos_sentence):
        assert len(word_sentence) == len(pos_sentence)
        temp = ""
        for word, pos in zip(word_sentence, pos_sentence):
            if pos in wanted_word:
                print(f"*{word}({pos})")
                temp += word
            elif pos in droped_list:
                pass
            else:
                print(f"{word}({pos})")
                temp += word
        print(temp)
        return

    for i, sentence in enumerate(sentence_list):
        print()
        print(f"'{sentence}'")
        print_word_pos_sentence(word_sentence_list[i],  pos_sentence_list[i])
        # for entity in sorted(entity_sentence_list[i]):
        #    print(entity)


inputSentence = [
    "想請問我使用vpn，但是在啟動network connect，他說要等幾分鐘，但之後都沒動作。我的前一步驟是按開始，後來就沒動作，我是要下載校園授權軟體，但是卡在下載ssl vpn連線軟體，請問這如何排解困難？",
    "你好：我已經下載office2013的光碟映像檔，再重新安裝，但是打開office軟體，都會出現產品啟動失敗，請問要如何操作才能安裝成功？謝謝。",
    "認證就一定得在學校網路內唷，因為是校園授權，所以在外面還是需要VPN"]

tasks=[ckip(i) for i in inputSentence]
asyncio.run(asyncio.wait(tasks))

