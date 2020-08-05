import warnings
import logging
import json
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    from ckiptagger import data_utils, construct_dictionary, WS, POS, NER


class chatbot(object):
    def __init__(self):
        self.transformer = Transformer()
        self.greeting = self.transformer.tree["root"]["featureName"]

    def chat(self, sentence, ClientStatus):
        currentRoot = ClientStatus["currentRoot"]
        knownInfo = ClientStatus["knownInfo"]

        if (sentence == None and currentRoot == None) or sentence == "RE:0":#Reset or Initinel Chat
            currentRoot = self.transformer.tree["root"]
            return currentRoot["featureText"], {"currentRoot": currentRoot, "knownInfo": {}}
        print(currentRoot)
        featureName = currentRoot["featureName"]
        inputTrans = currentRoot["inputTrans"]
        featureKey = currentRoot["featureKey"]
        defaultAnswer = currentRoot["defaultAnswer"]

        

        if featureName not in knownInfo:# Get feature
            
            if inputTrans != None:# Feature Preprocessor
                processedData=sentence 
                for functionName in inputTrans:# Itterate Feature Preprocessor
                    try:
                        preprocessor=getattr(self.transformer,functionName)
                    except:
                        logging.error("No Function Named{fn}".format(fn=functionName))
                        raise NotImplementedError
                        
                    processedData=preprocessor(processedData)
                feature=processedData
            else: # No Feature Preprocessor, feature=sentence
                feature = sentence


        if type(feature)==list: #TODO:Json load boolean
                                # Feature need to be str, bool or tuple 
            try:
                feature=feature[0]
            except:
                feature=""
                
        
        if feature in featureKey:
            currentRoot=featureKey[feature]
            knownInfo[featureName] = feature
            result=currentRoot["featureText"]
            if currentRoot["featureKey"]==None:# End of Tree. Reset To Root
                currentRoot=self.transformer.tree["root"]
                knownInfo={}
                result+="\nWhat Wrong With You?"# Greeting Message
            return result, {"currentRoot": currentRoot, "knownInfo": knownInfo}

        else:
            return self.defaultResponse(defaultAnswer,sentence,feature), {"currentRoot": currentRoot, "knownInfo": knownInfo}
    
    def defaultResponse(self,defaultAnswer,sentence,feature):
        if "str" in defaultAnswer:
            return defaultAnswer["str"]
        elif "function" in defaultAnswer:
            try:
                exceptFunction=getattr(self.transformer,defaultAnswer["function"])
            except:
                logging.error("No Function Named{fn}".format(fn=exceptFunction))
                raise NotImplementedError
            result=exceptFunction(sentence,feature)
            return result


class Transformer(object):
    def __init__(self):
        self.__PATH__ = os.path.dirname(os.path.abspath(__file__))
        logging.critical("Loading CKIP Data")
        logging.critical("WS Loading")
        self.ws = WS(self.__PATH__+"/data")
        logging.critical("WS Loaded")
        logging.critical("POS Loading")
        self.pos = POS(self.__PATH__+"/data")
        logging.critical("POS Loaded")
        logging.critical("NER Loading")
        self.ner = NER(self.__PATH__+"/data")
        logging.critical("NER Loaded")

        logging.critical("Loading Solution Tree")
        with open(self.__PATH__+"/tree.json", "r") as treefile:
            #TODO:Load json file with boolean
            self.tree = json.load(treefile)
            
        logging.critical("Solution Tree Loaded")

    def CKIPParser(self, sentence):
        word_to_weight = {
            "網路": 1,
            "連線": 1,
            "宿舍": 1,
            "宿網": 2,
        }
        dictionary = construct_dictionary(word_to_weight)

        word_sentence_list = self.ws(
            [sentence],
            coerce_dictionary=dictionary,
        )
        #pos_sentence_list = self.pos(word_sentence_list)
        #entity_sentence_list = self.ner(word_sentence_list, pos_sentence_list)

        for i, sentence in enumerate([sentence]):

            keyword = []
            for word in word_sentence_list[i]:
                if word in word_to_weight:
                    keyword.append(word)
        logging.info("CKIP find TOKEN : {token}".format(token=str(keyword)))
        return keyword
    def checkDormNetIDUsage(self,feature):
        n=feature[-1]
        try:
            n=int(n)
        except:
            return None
        if n%2==0:
            return "true"
        else:
            return "false"
    def Google(self,sentenct,feature):
        return "Google Say this is:"+str(sentenct)