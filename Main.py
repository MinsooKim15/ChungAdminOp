from models import *
from applyHome import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import sys, getopt
import math
import numpy as np
from PriceRate import *

import inspect,json,os
from datetime import datetime
import math

# 얘는 수동입력할 때 쓰는 건데 없어질 겁니다.


class Admin(object):
    def __init__(self,fileName):
        self.priceRateFile = "./priceRateFile.xlsx"
        self.credFileName = fileName
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
            doc_ref = self.db.collection(u'guides').document(guide.getId(),merge = True)
            doc_ref.set(guide.toDict())

def getArgv(argv):
    #기본은 STG로 한다.

    fileName = "./credential/homeguide-stg.json"
    databaseCategory = ""
    saveOption = 0
    try:
        opts, args = getopt.getopt(argv, "he:s:", ["environment=","saveOption="])
    except getopt.GetoptError:
        print("main.py -e <environment> -s <save option>")
    for opt, arg in opts:
        if opt == "-h":
            print("main.py -e <environment> -s <save option>")
        elif opt in ("-e", "--environment"):
            if arg in ("prd", "PRD", "PROD", "prod", "production", "PRODUCTION"):
                fileName = "./credential/homeguide-prd.json"
            else:
                fileName = "./credential/homeguide-stg.json"
        elif opt in ("-s", "--saveOption"):
            if arg in ("price", "priceRate", "priceOnly"):
                saveOption = 1
            else:
                saveOption = 0
    return (fileName, saveOption)




if __name__ == "__main__":

    fileName, saveOption = getArgv(sys.argv[1:])

    if saveOption == 1:
        admin = Admin(fileName)
        admin.connectDb()
        priceSetting = PriceSetting(fileName = fileName, db = admin.db)
        # admin.connectDb()
        priceSetting.getSubscriptions()
        priceSetting.setPriceRate()
        priceSetting.saveSubscriptionToDB()

    else:
        # # 모든 동작 희망할때,
        applyHome = ApplyHome()
        admin = Admin(fileName)
        admin.connectDb()
        # applyHome.getHomeList(startDate="202007", endDate="202008")
        # applyHome.getHomeDetail()
        # admin.subscriptionList = applyHome.subscriptionList
        # admin.saveSubscriptionToDB()
        #
        # applyHome.subscriptionList = []
        # applyHome.getOfficetelList(startDate="202007", endDate="202008")
        # applyHome.getOfficetelDetail()
        # admin.subscriptionList = applyHome.subscriptionList
        # admin.saveSubscriptionToDB()

        applyHome.subscriptionList = []
        applyHome.getNoRankList(startDate="202007", endDate="202008")
        applyHome.getNoRankDetail()
        admin.subscriptionList = applyHome.subscriptionList
        admin.saveSubscriptionToDB()

        priceSetting = PriceSetting(fileName,db = admin.db)
        # admin.connectDb()
        priceSetting.getSubscriptions()
        priceSetting.setPriceRate()
        priceSetting.saveSubscriptionToDB()
