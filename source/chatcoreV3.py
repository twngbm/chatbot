import asyncio
import copy
import csv
import json
import logging
import os
import random
import time
import warnings

from fuzzywuzzy import fuzz, process

import UserObj
from ChatbotConfig import *

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    from ckiptagger import POS, WS, construct_dictionary, data_utils

__PATH__ = os.path.dirname(os.path.abspath(__file__))+"/"

logging.critical("Loading Solution Tree")
with open(__PATH__+SOLUTION, "r", encoding="utf-8") as f:
    solutionList = json.load(f)

logging.critical("Loading Similar Dictionary")
with open(__PATH__+SIMILAR, "r", encoding="utf-8") as f:
    similarList = json.load(f)
similarDict = {}
for main, sim in similarList.items():
    similarDict[main] = main
    for s in sim:
        similarDict[s] = main
logging.critical("Loading Encouraged Dictionary")
with open(__PATH__+ENCDICT, "r", encoding="utf-8") as f:
    encouragedList = json.load(f)

logging.critical("Loading IT Table")
with open(__PATH__+ITTABLE, "r", encoding="utf-8-sig") as csvfile:
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

encouragedDict = {x: 2 for x in encouragedList+ITinfotableKey}


for ITsys, ITsysItem in ITinfotable.items():
    ans = {"系統概述": ITsysItem["功能簡述"],
           "業務單位": "業務單位/承辦人:{}<br>業務單位分機:{}".format(ITsysItem["業務單位"], ITsysItem["業務負責人分機"]),
           "系統負責單位": "系統負責單位/承辦人:{}<br>系統負責單位分機:{}".format(ITsysItem["系統負責人"], ITsysItem["系統負責人分機"])}
    solutionList["Keyword"][ITsys] = {"Checklist": ans}


logging.critical("Loading Question Table")
with open(__PATH__+QUESTION, "r", encoding="utf-8-sig") as q:
    temp = json.load(q)
    question = {list(i.keys())[0]: i[list(i.keys())[0]] for i in temp}


logging.critical("Loading CKIP-Word Segmentation(WS)")
ws = WS(__PATH__+CKIPDATA)
logging.critical("Loading CKIP-Part-of-Speech(POS)")
pos = POS(__PATH__+CKIPDATA)


class Chatbot(object):

    async def chat(self, User: UserObj.User):

        # Restart Chat or Initinal Chat
        if User.chatHistory == []:
            User.restart(solutionList, self.__GetMessage__("Keyword"))
            return

        # Find out User Intent or Feature
        if User.userSay.Type == "sys":
            # Handle System Control Message
            if User.userSay.Message == "return":
                # Return to Upper Recursive
                userPath = copy.deepcopy(User.intentLog)
                if len(userPath) == 1:
                    # Don't have any recursive
                    userPath = userPath[0]
                    if len(userPath) <= 1:
                        User.restart(
                            solutionList, self.__GetMessage__("Keyword"))
                        return

                    userPath.pop()
                    User.restart(solutionList, self.__GetMessage__("Keyword"))
                    newPath = []
                    for path in userPath:
                        featureName = [*User.currentNode][0]
                        if featureName == "Checklist":
                            break
                        newPath.append(path)
                        User.currentNode = User.currentNode[featureName][path]
                    User.intentLog = [newPath]
                    selectionList = [*User.currentNode[[*User.currentNode][0]]]
                    User.botUpdate([*User.currentNode][0],
                                   self.__GetMessage__([*User.currentNode][0]).format("-".join([x for k in User.intentLog for x in k])), selectionList)
                else:
                    if len(userPath[-1]) == 0:
                        # Head of recursive
                        outer = User.recursive.pop()
                        User.currentNode = outer
                        User.intentLog.pop()
                        User.intentLog[-1].pop()
                        User.botUpdate("Checklist", self.__GetMessage__(
                            "Checklist").format("-".join([x for k in User.intentLog for x in k])), [*outer["Checklist"]])
                    elif (len(userPath[-1])) == 1:
                        outer = User.recursive[-1]
                        lastPick = userPath[-2][-1]
                        refPath = outer["Checklist"][lastPick]["Reference"]
                        tempSolution = copy.deepcopy(solutionList)
                        for pathName in refPath:
                            tempSolution = tempSolution[[
                                *tempSolution][0]][pathName]
                        User.currentNode = tempSolution
                        userPath.pop()
                        userPath.append([])
                        User.intentLog = userPath
                        selectionList = [
                            *User.currentNode[[*User.currentNode][0]]]
                        User.botUpdate([*User.currentNode][0],
                                       self.__GetMessage__([*User.currentNode][0]).format("-".join([x for k in User.intentLog for x in k])), selectionList)

                    else:
                        # Middle of recursive
                        outer = User.recursive[-1]
                        lastPick = userPath[-2][-1]
                        refPath = outer["Checklist"][lastPick]["Reference"]
                        tempSolution = copy.deepcopy(solutionList)
                        for pathName in refPath:
                            tempSolution = tempSolution[[
                                *tempSolution][0]][pathName]
                        User.currentNode = tempSolution
                        tempPath = userPath[-1]
                        tempPath.pop()
                        newPath = []
                        for path in tempPath:
                            featureName = [*User.currentNode][0]
                            if featureName == "Checklist":
                                break
                            newPath.append(path)
                            User.currentNode = User.currentNode[featureName][path]
                        userPath.pop()
                        userPath.append(newPath)
                        User.intentLog = userPath
                        selectionList = [
                            *User.currentNode[[*User.currentNode][0]]]
                        User.botUpdate([*User.currentNode][0],
                                       self.__GetMessage__([*User.currentNode][0]).format("-".join([x for k in User.intentLog for x in k])), selectionList)
                return

            elif User.userSay.Message == "restart":
                # Restart Chat(Initinal State)
                User.restart(solutionList, self.__GetMessage__("Keyword"))
                return

            else:
                logging.error(f"Error Sys Command Name{User.userSay.Message}")
                raise TypeError

        elif User.userSay.Type == "raw":
            # User Input via Text
            # We create candidateList via current node's all feature.
            # Than we try to find out what user's intent.

            if User.userSay.Message in question["SysRestartConfirm"]["Question"]:
                # If user input match SysRestartConfirm, restart.
                User.restart(solutionList, self.__GetMessage__("Keyword"))
                return

            candidateList = [*User.currentNode[User.botSay.WantedFeature]]
            UserIntent = self.__intentParser__(
                User.userSay.Message, candidateList)
            if User.botSay.WantedFeature == "Checklist" and len(UserIntent) >= 1:
                # If it in Checklist state, pick the hightest score one of current candidate list
                # Just for convience.
                VeryUserIntent = UserIntent[0]
            elif len(UserIntent) > 1:
                logging.info(f"Guess Intent: {UserIntent}")
                User.botUpdate(User.botSay.WantedFeature,
                               self.__GetMessage__("Unbounded"), UserIntent)
                return

            elif len(UserIntent) == 1:
                VeryUserIntent = UserIntent[0]

            elif UserIntent == []:
                User.botUpdate(User.botSay.WantedFeature,
                               self.__GetMessage__(User.botSay.WantedFeature, True), [self.__GetMessage__("SysRestartConfirm")])
                return

        elif User.userSay.Type == "clicked":
            # User Input via Picked One in List
            candidateList = [*User.currentNode[User.botSay.WantedFeature]]
            if User.intentLog == [[]]:
                UserIntent = self.__intentParser__(
                    User.userSay.Message, candidateList)
                if len(UserIntent) > 1:
                    logging.info(f"Guess Intent: {UserIntent}")
                    User.botUpdate(User.botSay.WantedFeature,
                                   self.__GetMessage__("Unbounded"), UserIntent)
                    return

                elif len(UserIntent) == 1:
                    VeryUserIntent = UserIntent[0]

                elif UserIntent == []:
                    User.botUpdate(User.botSay.WantedFeature,
                                   self.__GetMessage__(User.botSay.WantedFeature, True), [self.__GetMessage__("SysRestartConfirm")])
                    return

            elif User.userSay.Message not in candidateList:
                if User.userSay.Message in question["SysRestartConfirm"]["Question"]:
                    # If user input match SysRestartConfirm, restart.
                    User.restart(solutionList, self.__GetMessage__("Keyword"))
                    return

                User.botUpdate(User.botSay.WantedFeature,
                               self.__GetMessage__(User.botSay.WantedFeature, True), [self.__GetMessage__("SysRestartConfirm")])
                return

            else:
                VeryUserIntent = User.userSay.Message
        else:
            raise TypeError

        logging.debug(f"Intent Found:{VeryUserIntent}")
        logging.debug(f"Intent Log:{User.intentLog}")
        # Goto Next Stage
        # aka Feature State

        # newNode=oldnode[WantedFeatureName][Feature]
        # Feature was founded on the above code.
        try:
            newNode = User.currentNode[User.botSay.WantedFeature][VeryUserIntent]
        except:
            User.botUpdate(User.botSay.WantedFeature,
                           self.__GetMessage__(User.botSay.WantedFeature, True), [self.__GetMessage__("SysRestartConfirm")])
            raise KeyError

        if type(newNode) == str:
            # If and only if we are in checklist state and client pick an item on list will this condition be true
            # cause other node on tree,type(newNode) will be dictionary
            # There are one exception where we need to "Reference" other node in solution tree ,make type(newNode)==dict,
            # where we'll handle with next condition
            # We than return the string object to Client, Client will determind how to display.
            # User.intentLog[len(User.recursive)].append(VeryUserIntent)
            User.botUpdate("Checklist", newNode, [
                           *User.currentNode["Checklist"]])
            return

        elif (type(newNode) == dict and "Reference" in newNode and User.botSay.WantedFeature == "Checklist"):
            # We reserve "Reference" as a reserved word ,which mean a reference will be made inside checklist
            # We push Current Checklist leaf to User.recursive
            # We now enter new recursive, just after we push our pervious Checklist
            # Than we travel path that define in "Reference"'s value from root
            # We Skip the FeatureName and go to next node by using path
            # We will finally reach the very node we want to reference.
            # No mather we are in feature state or checklist state, we just update the User.botUpdate with
            # current wantedFeature and featureList.
            User.intentLog[len(User.recursive)].append(VeryUserIntent)
            User.recursive.append(User.currentNode)
            User.intentLog.append([])
            refPath = newNode["Reference"]
            tempSolution = copy.deepcopy(solutionList)
            for pathName in refPath:
                tempSolution = tempSolution[[*tempSolution][0]][pathName]
            User.currentNode = tempSolution
            wantedFeature = [*tempSolution][0]
            if wantedFeature == "Checklist":
                sys_name = "-".join([x for k in User.intentLog for x in k])
                User.botUpdate(wantedFeature, self.__GetMessage__(
                    wantedFeature).format(sys_name), [*tempSolution[wantedFeature]])
            else:
                User.botUpdate(wantedFeature, self.__GetMessage__(
                    wantedFeature), [*tempSolution[wantedFeature]])
            return

        elif "Checklist" in newNode:
            # Entering Checklist State
            # When we reach leaf node. We are **Entering** checklist state.
            # We'll Show the information that need to be check aka. Checklist
            # Ckecklist state will be last as long as User.botSay.WantedFeature=="Checklist"
            User.intentLog[len(User.recursive)].append(VeryUserIntent)
            sys_name = "-".join([x for k in User.intentLog for x in k])
            response = self.__GetMessage__("Checklist").format(sys_name)
            User.botUpdate("Checklist", response, [*newNode["Checklist"]])
            User.currentNode = newNode
            return

        else:
            # There will be **Two** condition that user enter this block
            # A. Selecting in Intent State
            # B. Running in Feature State

            # A. Intent State
            # When User say it first sentent and we found the very intent that user want.
            # We selecting one cluster or one sub-tree, hance entering Feature State

            # B. Feature State
            # We want to find deeper feature so that we can go to leaf node
            # Just update user.currentNode with newnode and user.botsay.WantedFeature with new wanted feature
            User.intentLog[len(User.recursive)].append(VeryUserIntent)
            newwantedFeature = [*newNode][0]
            response = self.__GetMessage__(newwantedFeature)
            selectList = [*newNode[newwantedFeature]]
            User.botUpdate(newwantedFeature, response, selectList)
            User.currentNode = newNode
            return

    def __GetMessage__(self, featureName, exception=False):
        try:
            if exception:
                return random.choice(question[featureName]["Exception"])
            return random.choice(question[featureName]["Question"])

        except:
            raise NotImplementedError

    def __intentParser__(self, message, candidate) -> list:
        if message in candidate:
            # Phase1: If message 100% match candidate
            return [message]

        # Phase2: POS and fuzzy match throught candidate
        tokenList, token_posList = self.__CKIP__(message)

        fuzzyMatched = self.__fuzzymatcher__(
            tokenList, token_posList, candidate)

        if fuzzyMatched != []:
            return fuzzyMatched

        # Phase3: Try Sub-root search
        # For example: user input : "密碼", System will try to find out ["成功入口","電子信箱"]
        # since both have a "**密碼**" solution
        subMatch = self.__submatch__(tokenList, token_posList)
        if subMatch != []:
            return subMatch

        # Phase #: Unable to find any user intent
        return []

    def __CKIP__(self, message):
        dictionary = construct_dictionary(encouragedDict)
        word_sentence_list = ws(
            [message],
            sentence_segmentation=True,
            coerce_dictionary=dictionary)
        pos_sentence_list = pos(word_sentence_list)
        return word_sentence_list[0], pos_sentence_list[0]

    def __fuzzymatcher__(self, tokenList, token_posList, candidate) -> list:

        recommend = {}
        droped_list = CKIP_MARK+CKIP_UNWANTED

        for token, token_pos in zip(tokenList, token_posList):
            if token_pos in droped_list:
                continue

            similarPair = process.extractBests(
                token, [*similarDict], scorer=fuzz.UWRatio)
            similarText = similarPair[0][0]
            similarScore = similarPair[0][1]
            fuzzymatch = process.extract(
                token, candidate, limit=2, scorer=fuzz.UWRatio)

            similarFuzzymatch = []
            if similarScore >= CONFIDENCE_ACCEPT_THRESHOLD:
                similarFuzzymatch = process.extract(
                    similarDict[similarText], candidate, limit=2, scorer=fuzz.UWRatio)

            for match_str, confidence in fuzzymatch+similarFuzzymatch:
                if confidence < CONFIDENCE_DROP_THRESHOLD:
                    continue
                try:
                    recommend[confidence]
                    recommend[confidence].append(match_str)
                except:
                    recommend[confidence] = [match_str]
        if recommend == {}:
            return []
        logging.debug("Intent Score:"+str(recommend))
        maxFuzzy = max(recommend)
        fuzzyMatch = []
        if maxFuzzy >= CONFIDENCE_ACCEPT_THRESHOLD:
            return list(set(recommend[maxFuzzy]))
        for confidence, item in recommend.items():
            candidateGroup = list(set(item))
            if len(fuzzyMatch+candidateGroup) > MAX_INTEND_AMOUNT and fuzzyMatch != []:
                return list(set(fuzzyMatch))
            elif len(fuzzyMatch+candidateGroup) > MAX_INTEND_AMOUNT and fuzzyMatch == []:
                return list(set(candidateGroup))
            else:
                fuzzyMatch += candidateGroup
        return list(set(fuzzyMatch))

    def __submatch__(self, tokenList, token_posList) -> list:
        def dfs(node, head=None):
            nonlocal submatch
            nonlocal wantedToken
            featureName = [*node][0]
            if featureName == "Checklist":
                return
            for feature in node[featureName]:
                if head == None:
                    dfs(node[featureName][feature], feature)
                    continue
                for token in wantedToken:
                    if token in feature:  # Match Method
                        submatch.append(head)
                dfs(node[featureName][feature], head)
        droped_list = CKIP_MARK+CKIP_UNWANTED
        wantedToken = []
        for token, token_pos in zip(tokenList, token_posList):
            if token_pos in droped_list:
                continue
            wantedToken.append(token)
        submatch = []
        dfs(solutionList)

        return list(set(submatch))
