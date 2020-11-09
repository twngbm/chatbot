import asyncio
import copy
import logging
import os
import random
import time


import UserObj

import utils


class Chatbot(object):
    def __init__(self, data: utils.LoaderUtils):
        self.data = data
        self.IntentUtils = utils.IntentUtils(self.data)
        self.ChatUtils = utils.ChatUtils(self.data)

    async def chat(self, User: UserObj.User):

        # Find out User Intent or Feature
        if User.userSay.Type == "sys":
            # Handle System Control Message
            if User.userSay.Message == "return":
                User.undoNode()
                return

            elif User.userSay.Message == "restart":
                # Restart Chat(Initinal State)
                User.restart()
                return

            else:
                logging.error(f"Error Sys Command Name{User.userSay.Message}")
                raise TypeError

        # User Input via Text
        # We create candidateList via current node's all feature.
        # Than we try to find out what user's intent.

        elif User.userSay.Type == "raw":
            # Check if restart
            userIntent = self.IntentUtils.intentParser(
                User.userSay.Message, self.data.question["SysRestartConfirm"]["Question"], noDFS=True)
            if userIntent != []:
                User.restart()
                return

            # Check if goto previous step
            userIntent = self.IntentUtils.intentParser(
                User.userSay.Message, self.data.question["SysPrevious"]["Question"], noDFS=True)
            if userIntent != []:
                User.undoNode()
                return

            # Check if inside function
            if User.inFunction:
                User.updateFunction(User.userSay.Message, self.IntentUtils)
                return

            # Check if user press other bubble's button
            if User.userSay.relatively != 0:
                User.jump()
                return

            if User.userSay.Message in self.data.similarDict:
                if self.data.similarDict[User.userSay.Message] == "問候":
                    User.botUpdate(self.ChatUtils.getQuestion(
                        "greeting"), None,  User.userSay.Message)
                    return

            candidate = User.currentFeature()
            userIntent = self.IntentUtils.intentParser(
                User.userSay.Message, candidate)
            logging.info(f"Guess Intent: {userIntent}")
            if len(userIntent) == 0:
                if User.isRoot():
                    candidate = self.ChatUtils.getQuestion("rootUnbound")
                    checklist = [self.ChatUtils.getQuestion(
                        "SysRestartConfirm")]
                else:
                    candidate = candidate
                    checklist = candidate + \
                        [self.ChatUtils.getQuestion("SysRestartConfirm")]
                response = self.ChatUtils.getQuestion(
                    User.currentFeatureName(), True).format(INPUT=User.userSay.Message, CANDIDATE=candidate)
                User.updateNode(User.currentNode, User.userSay.Message)
                User.botUpdate(response, checklist, User.userSay.Message)
                return

            elif len(userIntent) == 1:
                intent = userIntent[0]
            else:
                response = self.ChatUtils.getQuestion(
                    "Unbounded").format(INPUT=User.userSay.Message)
                checklist = userIntent + \
                    [self.ChatUtils.getQuestion("SysRestartConfirm")]
                User.updateNode(User.currentNode, userIntent)
                User.botUpdate(response, checklist, User.userSay.Message)
                return

        else:
            raise TypeError

        logging.debug(f"Intent Found:{intent}")
        # Goto Next Stage
        # aka Feature State

        # Feature was founded on the above code.

        nextNode = User.nextNode(intent)

        if type(nextNode) == str:
            # If and only if we are in checklist state and client pick an item on list will this condition be true
            # cause other node on tree,type(newNode) will be dictionary
            # There are one exception where we need to "Reference" other node in solution tree ,make type(newNode)==dict,
            # where we'll handle with next condition
            # We than return the string object to Client, Client will determind how to display.
            # User.intentLog[len(User.recursive)].append(VeryUserIntent)
            User.updateNode(User.currentNode, intent)
            response = self.ChatUtils.getQuestion("Checklist").format(
                PATH=User.intentPath(), DESCRIPTION=User.checklistDescription())
            User.botUpdate(nextNode, User.currentFeature(),
                           intent, None, response)
            return

        elif "Reference" in nextNode:
            # We reserve "Reference" as a reserved word ,which mean a reference will be made inside checklist
            # We push Current Checklist leaf to User.recursive
            # We now enter new recursive, just after we push our pervious Checklist
            # Than we travel path that define in "Reference"'s value from root
            # We Skip the FeatureName and go to next node by using path
            # We will finally reach the very node we want to reference.
            # No mather we are in feature state or checklist state, we just update the User.botUpdate with
            # Current Feature Name and featureList.
            # User.intentLog[len(User.recursive)].append(VeryUserIntent)
            # User.recursive.append(User.currentNode)
            # User.intentLog.append([])
            refPath = nextNode["Reference"]
            newNode = User.reference(refPath)
            User.updateNode(newNode, intent)
            response = self.ChatUtils.getQuestion(User.currentFeatureName()).format(
                PATH=User.intentPath(), DESCRIPTION=User.checklistDescription())
            User.botUpdate(response, User.currentFeature(), intent)
            return

        elif "Checklist" in nextNode:
            # Entering Checklist State
            # When we reach leaf node. We are **Entering** checklist state.
            # We'll Show the information that need to be check aka. Checklist
            # Ckecklist state will be last as long as User.currentFeatureName()=="Checklist"
            User.updateNode(nextNode, intent)
            response = self.ChatUtils.getQuestion("Checklist").format(
                PATH=User.intentPath(), DESCRIPTION=User.checklistDescription())
            User.botUpdate(response, User.currentFeature(), intent)
            return

        elif "Function" in nextNode:
            User.updateFunction(intent, self.IntentUtils)
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
            # Just update user.currentNode with newnode and user.currentFeatureName() with new wanted feature
            User.updateNode(nextNode, intent)
            User.botUpdate(self.ChatUtils.getQuestion(
                User.currentFeatureName()), User.currentFeature(), intent)
            return
