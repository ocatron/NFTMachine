import pandas as pd
import itertools
from collections import Counter
from pprint import pprint

layers = [
    {
        "name": "Background",
        "traits": ["Blue","Green","Red","Yellow"],
        "rarities": [5,20,5,30],
    },
    {
        "name": "Glasses",
        "traits": ["Clear","BlackTinted","RedTinted"],
        "rarities": [10,30,20],
    },
    {
        "name": "Mood",
        "traits": ["Happy","Sad","Neutral","Meh","Wow"],
        "rarities": [10,5,25,10,10],
    }
]

neededTotal = 30

def getTotalCombinations():
    
    total = 1
    for layer in layers:
        total = total * len(layer['traits'])
    return total

print(getTotalCombinations())


def generateImage(layers):
    for layer in layers:
        pass