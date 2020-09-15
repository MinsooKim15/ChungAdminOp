from models import *
from applyHomeCrawler import *
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


class PriceSetting(object):
    def __init__(self,fileName,db = None):
        self.priceRateFile = "./priceRate.xlsx"
        self.credFileName = fileName
        self.db = db
    def getSubscriptions(self):
        # self.connectDb()
        sub_ref = self.db.collection(u'subscriptions')
        priceNeedToSet_ref = sub_ref.where(u"priceDidSet",u"==", False)
        docs = priceNeedToSet_ref.stream()
        self.subscriptionList = []
        for doc in docs:
            subscription = Subscription.from_dict(doc.to_dict())
            subscription.id = doc.id
            self.subscriptionList.append(subscription)
    def getPriceRates(self):
        sub_ref = self.db.collection(u"priceRates")
        docs = sub_ref.stream()
        self.priceRateList = []
        for doc in docs:
            priceRate = PriceRate.from_dict(doc.to_dict())
            priceRate.id = doc.id
            self.priceRateList.append(priceRate)
    def setPriceRate(self):
        for priceRate in self.priceRateList:
            for subscription in self.subscriptionList:
                if int(subscription.id) == int(priceRate.subscriptionId):
                    subscription.setPriceRate(firstPriceRate = float(priceRate.firstRate),
                                              middlePriceRate = float(priceRate.middleRate),
                                              finalPriceRate = float(priceRate.lastRate))
    # 엑셀 쓰던 시절 설정
    # def setPriceRate(self):
    #     print("admin setPriceRate")
    #     self.typeList = []
    #     df = pd.read_excel(self.priceRateFile)
    #     for i in df.index:
    #         data = df.iloc[i,]
    #         for subscription in self.subscriptionList:
    #             if int(subscription.id) == int(data[u"id"]):
    #                 subscription.setPriceRate(firstPriceRate=data[u"firstPriceRate"],
    #                                           middlePriceRate= data[u"middlePriceRate"],
    #                                           finalPriceRate= data[u"finalPriceRate"])
    #
    def saveSubscriptionToDB(self):
        # print(subsc)
        for subscription in self.subscriptionList:
            doc_ref = self.db.collection(u'subscriptions').document(subscription.getId())
            doc_ref.set(subscription.toDict(),merge= True)
    # def connectDb(self):
    #     path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    #     cred = credentials.Certificate(path + "/" + self.credFileName)
    #     firebase_admin.initialize_app(cred)
    #     self.db = firestore.client()


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
            doc_ref = self.db.collection(u'guides').document(guide.getId(),merge = True)
            doc_ref.set(guide.toDict())

if __name__ == "__main__":
    # applyHome = ApplyHome()
    # applyHome.getHomeList(startDate="202007", endDate="202008")
    # applyHome.getHomeDetail()
    priceSetting = PriceSetting()
    # admin.connectDb()
    priceSetting.getSubscriptions()
    priceSetting.setPriceRate()
    priceSetting.saveSubscriptionToDB()
    # admin.subscriptionList = applyHome.subscriptionList
    # admin.saveSubscriptionToDB()