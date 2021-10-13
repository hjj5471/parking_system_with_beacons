from enum import Enum

class Hedge(Enum):
    brick1 = 5
    brick2 = 6

def ss(user):
    if user == "brick1":
        hedgeNum = Hedge.brick1
    elif user == "brick2":
        hedgeNum = Hedge.brick2
    else:
        hedgeNum = None

    return hedgeNum
