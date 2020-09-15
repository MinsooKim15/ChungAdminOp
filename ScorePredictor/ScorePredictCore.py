import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pandas as pd
import numpy as np
class ScorePredictCore(object):
    def __init__(self):
        self.subscriptionList = []
        self.df = None
        # 타겟 스코어는 여기서 한 번에 바꾼다.
        self.targetScore = "averageScore"
        self.originalDf = None
    def setDataFrame(self):
        self.df = pd.DataFrame()
        for subscription in self.subscriptions:
            for homeType in subscription.typeList:
                if subscription.buildingType == "아파트":
                    new_row = {
                        'dateAnnounce': subscription.dateAnnounce,
                        'dateContract': subscription.dateContract,
                        'dateFirstNear': subscription.dateFirstNear,
                        'dateNotice': subscription.dateNotice,
                        'dateSecondNear': subscription.dateSecondNear,
                        'dateSpecialSupplyNear': subscription.dateSpecialSupplyNear,
                        'hasSpecialSupply': subscription.hasSpecialSupply,
                        'sizeInMeter': homeType.sizeInMeter,
                        'generalSupply': homeType.generalSupply,
                        'specialSupply': homeType.specialSupply,
                        'totalPriceNumeric': homeType.totalPrice.numeric,
                        'totalSupply': homeType.totalSupply,
                        'subscriptionId' : subscription.id,
                        'homeTypeCode' : homeType.id
                    }
                    if subscription.geocode != None:
                        new_row["latitude"] =  subscription.geocode.latitude
                        new_row["longitude"] =  subscription.geocode.longitude
                    else:
                        new_row["latitude"] = np.nan
                        new_row["longitude"] = np.nan
                    if homeType.winningScore != None:
                        new_row["minScore"] = homeType.winningScore.minScore
                        new_row["maxScore"] = homeType.winningScore.maxScore
                        new_row["averageScore"] = homeType.winningScore.averageScore
                    else:
                        new_row["minScore"] = np.nan
                        new_row["maxScore"] = np.nan
                        new_row["averageScore"] = np.nan
                    self.df = self.df.append(new_row, ignore_index=True)
        self.originalDf = self.df
    def cleanDataFrame(self):
        # Datetime to total Seconds
        dateTimeList = ["dateAnnounce", "dateContract", "dateFirstNear", "dateNotice", "dateSecondNear",
                        'dateSpecialSupplyNear']
        for dateTime in dateTimeList:
            self.df[dateTime] = pd.to_datetime(self.df[dateTime], format="%Y-%m-%d").astype(int)
        # String to Numeric
        stringList = ["latitude", "longitude"]
        for stringItem in stringList:
            self.df[stringItem] = pd.to_numeric(self.df[stringItem])

    def getX(self):
        filteringColumns = ['dateAnnounce',
                            'dateContract',
                            'dateFirstNear',
                            'dateNotice',
                            'dateSecondNear',
                        'dateSpecialSupplyNear',
                            'generalSupply',
                        'hasSpecialSupply',
                            'latitude',
                            'longitude',
                        'sizeInMeter',
                        'specialSupply',
                        'totalPriceNumeric',
                        'totalSupply']
        return self.df.filter(filteringColumns)
