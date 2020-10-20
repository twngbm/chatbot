# Server Setup
try:
    from realKey import *
except:
    pass
WEBSOCKETPORT = 8080


# Ckip Data Path
# Relative Path to chatcore.py
CKIPDATA = "../data/"

# Other File Path
# Relative Path to chatcore.py
ITTABLE = "../reference/ITPrincipal.csv"
QUESTION = "../reference/questions.json"
SOLUTION = "../reference/solution.json"
SIMILAR = "../reference/similar.json"
ENCDICT = "../reference/ckip.json"

# Fuzzy Search Confidence Threshold 0~100
CONFIDENCE_DROP_THRESHOLD = 55  # Any Suggestion Below This Threshold will be drop
# Any Suggesstion Above This Threshold will be seen as only intent.
CONFIDENCE_ACCEPT_THRESHOLD = 95
MAX_INTEND_AMOUNT = 4
CKIP_MARK = ['COLONCATEGORY', 'COMMACATEGORY', 'DASHCATEGORY', 'DOTCATEGORY', 'ETCCATEGORY',
             'EXCLAMATIONCATEGORY', 'PARENTHESISCATEGORY', 'PAUSECATEGORY', 'PERIODCATEGORY', 'QUESTIONCATEGORY',
             'SEMICOLONCATEGORY', 'SPCHANGECATEGORY', 'WHITESPACE']
CKIP_UNWANTED = ["DE", "D", "Nh", "Cbb", "Caa", "Cab",
                 "Cba", "Da", "Dfa", "Dfb", "Di", "Dk", "DM", "I", "Nd"]

# Other Supported (OpenWeather AIP Key...)
try:
    OPENWEATHER_APIKEY
except:
    OPENWEATHER_APIKEY = "https://openweathermap.org/ api key here"
try:
    GOOGLE_PLACES_API_KEY
except:
    GOOGLE_PLACES_API_KEY = "GOOGLE API KEY HERE"
