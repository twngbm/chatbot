########################
#Node={"Key":{
#    "featureText":["Text To Explain Feature",],
#    "featureName":"Feature Name", #變數名稱
#    "inputParser":["Input Transform Function Name",], #function name
#    "featureKey":{"Key":*Node1,"Key2":*Node2},
#    "defaultAnswer":{"str":"Answer Text.","function":"Function Name"},
#    "ParentNode":*parentNode}
#}
########################
import json
import os
import logging
import time
global dormPath
dormNetOveruse={
    "featureText":["You use too much."],
    "featureName":None,
    "inputTrans":None,
    "featureKey":None,
    "defaultAnswer":None
}
labPath={"featureText":"Ask yourself.",
    "featureName":None,
    "inputTrans":None,
    "featureKey":None,
    "defaultAnswer":None}
userNetHWSuccess={"featureText":"Wait and Retry.",
    "featureName":None,
    "inputTrans":None,
    "featureKey":None,
    "defaultAnswer":None}
userNetHWFailed={"featureText":"Plug the cable in.",
    "featureName":None,
    "inputTrans":None,
    "featureKey":None,
    "defaultAnswer":None}
dormNetDebug={"featureText":"Please Check Your Socket and Connection",
    "featureName":"UserHWConnectionStatus",
    "inputTrans":None,
    "featureKey":{"正常":userNetHWSuccess,"異常":userNetHWFailed},
    "defaultAnswer":{"str":"StudentID Not Found"}}
dormPath={
    "featureText":"Please Enter Your Student ID.",
    "featureName":"StudentID",
    "inputTrans":["checkDormNetIDUsage"],
    "featureKey":{True:dormNetOveruse,False:dormNetDebug},
    "defaultAnswer":{"str":"StudentID Not Found"}
}
test1={"featureText":"You Should Have No Issue.",
    "featureName":None,
    "inputTrans":None,
    "featureKey":None,
    "defaultAnswer":None}
test2={"featureText":"Use VPM.",
    "featureName":None,
    "inputTrans":None,
    "featureKey":None,
    "defaultAnswer":None}
a={"featureText":"What Wrong With You?",
   "featureName":"Keyword",
   "inputTrans":["CKIPParser"],
   "featureKey":{
    "網路":{
    "featureText":"Where is your location?",
    "featureName":"Location",
    "inputTrans":None,
    "featureKey":{"宿舍":dormPath,"實驗室":labPath},
    "defaultAnswer":{"str":"Call 61010"}},
"授權軟體":{"featureText":"Where is your location?",
    "featureName":"Location",
    "inputTrans":None,
    "featureKey":{"校內":test1,"校外":test2},
    "defaultAnswer":{"str":"請輸入校內或校外"}}},
    "defaultAnswer":{"function":"Google"}
}

__PATH__=os.path.dirname(os.path.abspath(__file__))
with open(__PATH__+"/tree.json","w") as f:
    json.dump({"root":a},f)

