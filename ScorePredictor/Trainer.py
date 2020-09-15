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

from models import *
import pickle
from Main import *
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
from ScorePredictCore import *

from applyHomeCrawler import *
class Trainer(ScorePredictCore):
    def __init__(self):
        self.subscriptions = []
        self.modelAddress = "./ScorePredictor/Model/"
        now = datetime.date.today()
        nowString = now.strftime("%Y%m%d")
        self.modelName = "model" + "_" + nowString
    def getSubscriptions(self):
        fileName = "credential/homeguide-stg.json"
        admin = Admin(fileName)
        admin.connectDb()
        self.subscriptions = admin.getSubscriptions()
    def trainModel(self):
        X = self.getX()
        Y = self.df.filter(["averageScore"])
        X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.15, random_state=4)
        # Train a model using XGBRegressor
        self.xgb_reg = xgb.XGBRegressor(booster='gbtree', colsample_bylevel=1,
                                        colsample_bynode=1, colsample_bytree=0.6, gamma=0,
                                        importance_type='gain', learning_rate=0.01, max_delta_step=0,
                                        max_depth=4, min_child_weight=1.5, n_estimators=2400,
                                        n_jobs=1, nthread=None, objective='reg:linear',
                                        reg_alpha=0.6, reg_lambda=0.6, scale_pos_weight=1,
                                        silent=None, subsample=0.8, verbosity=1)
        self.xgb_reg.fit(X_train, Y_train, verbose=1, early_stopping_rounds=50, eval_metric='rmse',
                         eval_set=[(X_val, Y_val)])
    def cleanNullScores(self):
        self.df = self.df[self.df["averageScore"].notnull()]
    def saveModel(self):
        # save
        pickle.dump(self.xgb_reg, open(self.modelAddress+ self.modelName, "wb"))


if __name__ == "__main__":
    trainer = Trainer()
    trainer.getSubscriptions()
    trainer.setDataFrame()
    trainer.cleanDataFrame()
    trainer.cleanNullScores()
    trainer.trainModel()
    trainer.saveModel()