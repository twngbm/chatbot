########################
#structure={"Key":{
#    "featureText":"Text To Explain Feature",
#    "featureName":"Feature Name",
#    "inputTrans":["Input Transform Function Name",],
#    "featureKey":{"Key":*structure,"Key2":*structure},
#    "defaultAnswer":{"str":"Answer Text.","function":"Function Name"}}
#}
#example:
#{"Network":{
#    "featureName":"Location",
#    "inputTrans":None,
#    "featureKey":{"Dorm":dormPath,"Lab":labPath},
#    "defaultAnswer":"Call 61010"},
#"software":{...}
#}
#dormPath:{
#    "featureName":"Student ID",
#    "inputTrans":"checkUsage(studentID:str)->bool",
#    "featureKey":{True:dormNetOveruse,False:dormNetDebug},
#    "defaultAnswer":None
#}
#overusage:{
#    "featureName":None,
#    "inputTrans":None,
#    "featureKey":{None:None},
#    "defaultAnswer":"You use too much."
#}
########################
import json
import os
import logging
import time
dormNetOveruse={
    "featureText":"You use too much.",
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

