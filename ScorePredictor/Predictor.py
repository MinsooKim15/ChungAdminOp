import pandas as pd
import json
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import urllib
from urllib.request import urlopen
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from os import listdir
from os.path import isfile, join
from models import *
import pickle
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import RidgeCV
import xgboost as xgb
from datetime import datetime
from .ScorePredictCore import ScorePredictCore
import pathlib

class Predictor(ScorePredictCore):
    def __init__(self):
        self.loadModel()

    def loadModel(self):
        print("WOW")
        currentPath = pathlib.Path(__file__).parent.absolute()
        print(currentPath)
        modelDir = str(currentPath) + "/Model/"
        onlyfiles = [f for f in listdir(modelDir) if isfile(join(modelDir, f))]
        print(onlyfiles)
        fileName = sorted(onlyfiles, reverse = True)[0]
        self.xgb_model = pickle.load(open(modelDir + fileName, "rb"))
    def predictScore(self, subscription):
        self.subscriptions = [subscription]
        self.setDataFrame()
        self.cleanDataFrame()
        X = self.getX()
        result = self.xgb_model.predict(X)
        for index, item in enumerate(result):
            result[index] = round(item)
        return result.tolist()

if __name__ == "__main__":
    predictor = Predictor()
