from models import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import math
import numpy as np

import inspect,json,os
from datetime import datetime
import math

# 얘는 수동입력할 때 쓰는 건데 없어질 겁니다.


class Admin(object):
    def __init__(self):
        self.guideAddress = "./guide.xlsx"
        self.subAddress = "./subscription.xlsx"
        self.typeAddress = "./type.xlsx"
        self.credFileName = "homeguide-prd.json"
    def getSubscriptionList(self):
        self.__getSubscriptions()
        self.__getTypes()
        self.__appendTypes()
    def __getSubscriptions(self):
        self.subscriptionList = []
        df = pd.read_excel(self.subAddress)

        for i in df.index:
            subscription = Subscription(
                id = df.iloc[i,][u"id"],
                title = df.iloc[i,][u"title"],
                addressProvinceCode = df.iloc[i,][u"addressProvinceCode"],
                addressDetailFirstKor = df.iloc[i,][u"addressDetailFirstKor"],
                 addressDetailSecondKor = df.iloc[i,][u"addressDetailSecondKor"],
                 buildingType = df.iloc[i,][u"buildingType"],
                 subscriptionType = df.iloc[i,][u"subscriptionType"],
                 noRank = df.iloc[i,][u"noRank"],
                 noRankDate = df.iloc[i,][u"noRankDate"],
                 hasSpecialSupply = df.iloc[i,][u"noRankDate"],
                 dateSpecialSupplyNear = df.iloc[i,][u"dateSpecialSupplyNear"],
                 dateSpecialSupplyOther = df.iloc[i,][u"dateSpecialSupplyOther"],
                 dateFirstNear = df.iloc[i,][u"dateFirstNear"],
                 dateFirstOther = df.iloc[i,][u"dateFirstOther"],
                 dateSecondNear = df.iloc[i,][u"dateSecondNear"],
                 dateSecondOther = df.iloc[i,][u"dateSecondOther"],
                 dateNotice = df.iloc[i,][u"dateNotice"],
                 officialLLink = df.iloc[i,][u"officialLink"],
                 documentLink = df.iloc[i,][u"documentLink"]
            )
            self.subscriptionList.append(subscription)
    def __getTypes(self):
        self.typeList = []
        df = pd.read_excel(self.typeAddress)

        for i in df.index:
            data = df.iloc[i,]
            type = Type(
                subId = data[u"subId"],
                title = data[u"title"],
                size = data[u"size"],
                generalSupply = data[u"generalSupply"],
                specialSupply = data[u"specialSupply"],
                totalSupply = data[u"totalSupply"],
                totalPrice = data[u"totalPrice"],
               firstPriceRate = data[u"firstPriceRate"],
                middlePriceRate = data[u"middlePriceRate"],
                finalPriceRate = data[u"finalPriceRate"]
            )
            print(type)
            self.typeList.append(type)
    def __appendTypes(self):
        for subscription in self.subscriptionList:
            typeList = []
            print(subscription.id)
            for i,v in enumerate(self.typeList):
                print(v.subId)
                if v.subId == subscription.id:
                    typeList.append(v)
                    del self.typeList[i]
            print(typeList)
            subscription.addTypeList(typeList)
    def saveSubscriptionToDB(self):
        # print(subsc)
        for subscription in self.subscriptionList:
            doc_ref = self.db.collection(u'subscriptions').document(subscription.getId())
            doc_ref.set(subscription.toDict())
    def connectDb(self):
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        cred = credentials.Certificate(path + "/" + self.credFileName)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()


    def getGuideList(self):
        self.guideList = []
        df = pd.read_excel(self.guideAddress)
        print(df)
        for i in df.index:
            data = df.iloc[i,]

            guide = Guide(
                id = data[u"id"],
                title = data[u"title"],
                subtitle = data[u"subtitle"],
                webUrl = data[u"webUrl"],
                imgUrl= data[u"imgUrl"]
            )
            self.guideList.append(guide)
    def saveGuideToDB(self):
        for guide in self.guideList:
            doc_ref = self.db.collection(u'guides').document(guide.getId())
            doc_ref.set(guide.toDict())

if __name__ == "__main__":
    admin = Admin()
    admin.getSubscriptionList()
    admin.connectDb()
    admin.saveSubscriptionToDB()
    admin.getGuideList()
    admin.saveGuideToDB()