from models import *
from applyHome import *
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
        self.priceRateFile = "./priceRate.xlsx"
        self.credFileName = "credential/homeguide-493c7-firebase-adminsdk-s2e5v-5285f17df0.json"
    def getSubscriptions(self):
        self.connectDb()
        sub_ref = self.db.collection(u'subscriptions')
        priceNeedToSet_ref = sub_ref.where(u"priceDidSet",u"==", False)
        docs = priceNeedToSet_ref.stream()
        self.subscriptionList = []
        for doc in docs:
            subscription = Subscription.from_dict(doc.to_dict())
            subscription.id = doc.id
            self.subscriptionList.append(subscription)

    def setPriceRate(self):
        self.typeList = []
        df = pd.read_excel(self.priceRateFile)
        for i in df.index:
            data = df.iloc[i,]
            print("찾고 있는 ID:",int(data[u"id"]))
            print(data[u"middlePriceRate"])
            for subscription in self.subscriptionList:
                print("청약 id:", subscription.id)
                if int(subscription.id)== int(data[u"id"]):
                    subscription.setPriceRate(firstPriceRate=data[u"firstPriceRate"],
                                              middlePriceRate= data[u"middlePriceRate"],
                                              finalPriceRate= data[u"finalPriceRate"])
    def saveSubscriptionToDB(self):
        # print(subsc)
        for subscription in self.subscriptionList:
            print(subscription.toDict())
            doc_ref = self.db.collection(u'subscriptions').document(subscription.getId())
            doc_ref.set(subscription.toDict(),merge= True)
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
            doc_ref = self.db.collection(u'guides').document(guide.getId(),merge = True)
            doc_ref.set(guide.toDict())

if __name__ == "__main__":
    # applyHome = ApplyHome()
    # applyHome.getHomeList(startDate="202007", endDate="202008")
    # applyHome.getHomeDetail()
    admin = Admin()
    # admin.connectDb()
    admin.getSubscriptions()
    admin.setPriceRate()
    admin.saveSubscriptionToDB()
    # admin.subscriptionList = applyHome.subscriptionList
    # admin.saveSubscriptionToDB()