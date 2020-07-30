from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
import os
import sys
import struct
import select
import tensorflow as tf
import time


def create_msg(content):
    return struct.pack("<I", len(content)) + content

def get_message(fifo):
    """Get a message from the named pipe."""
    msg_size_bytes = os.read(fifo, 4)
    msg_size = struct.unpack("<I", msg_size_bytes)[0]
    msg_content = os.read(fifo, msg_size).decode("utf8")
    return msg_content

def init():
    __PATH__=os.path.dirname(os.path.abspath(__file__))
    try:
        os.mkfifo(__PATH__+"/input.pipe")
        os.mkfifo(__PATH__+"/output.pipe")
    except:
        pass
    Ckip=ckip()
    writer=os.open(__PATH__+"/output.pipe",os.O_WRONLY)
    msg=create_msg("ACK".encode("utf8"))
    os.write(writer,msg)
    os.close(writer)
    
    return Ckip

def run(Ckip):
    __PATH__=os.path.dirname(os.path.abspath(__file__))
    reader=os.open(__PATH__+"/input.pipe",os.O_RDONLY|os.O_NONBLOCK)
    poll=select.poll()
    poll.register(reader,select.POLLIN)
    while True:
        if (reader,select.POLLIN) in poll.poll(500):
            msg=get_message(reader)
        else:
            time.sleep(0.5)
            continue
        keyword=Ckip.GetKeyword(msg)
        msg=create_msg(str(keyword).encode("utf8"))
        writer=os.open(__PATH__+"/output.pipe",
                         os.O_WRONLY | os.O_NONBLOCK)
        os.write(writer,msg)
        os.close(writer)
class ckip:
    def __init__(self):
        self.ws = WS("./data")
        self.pos = POS("./data")
        self.ner = NER("./data")

    def GetKeyword(self,sentence):

        word_to_weight = {
            "網路": 1,
            "連線": 1,
            "宿舍": 1,
            "宿網": 2,
        }
        dictionary = construct_dictionary(word_to_weight)

        word_sentence_list = self.ws(
            [sentence],
            coerce_dictionary = dictionary, 
        )
        pos_sentence_list = self.pos(word_sentence_list)
        entity_sentence_list = self.ner(word_sentence_list, pos_sentence_list)


        for i, sentence in enumerate([sentence]):

            keyword = []
            for word in word_sentence_list[i]:
                if word in word_to_weight:
                    keyword.append(word)
            return keyword
if __name__ == "__main__":
    Ckip=init()
    run(Ckip)