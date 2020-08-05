import solution
import os
import json
__PATH__=os.path.dirname(os.path.abspath(__file__))
with open(__PATH__+"/tree.json","r") as f:
    solutionTree=json.load(f)
Parser=solution.QAParser()
