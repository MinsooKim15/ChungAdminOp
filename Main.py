from models import *
from applyHomeCrawler import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import sys, getopt
import math
import numpy as np
from PriceRate import *

import inspect,json,os
import datetime
import math
import json
from ScorePredictor.Predictor import Predictor

# 얘는 수동입력할 때 쓰는 건데 없어질 겁니다.


# Admin : 데이터의 후처리/DB 입출력 등을 다룬다.<- 아니 넌 로직 컨트롤러야
# ApplyHome : 얘는 Crawler임.
# Model : Model임.
# Query : Query만 다루는 애를 만들거야.

class Admin(object):
    def __init__(self,environment):
        self.priceRateFile = "./priceRateFile.xlsx"
        # self.credFileName = fileName
        self.dbService = DBService(environment=environment)
        self.priceRateList = []
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
    def hasSubscription(self, subscriptionId):
        doc_ref = self.dbService.getOneSubscription(subscriptionId)
        returnNull = False
        doc = doc_ref.get()
        if doc.exists:
            targetSubscription = Subscription.from_dict(doc.to_dict())
            return True
        else:
            return False
    def getSubscriptions(self):
        self.dbService.addCondition(key = u"subscriptionType", operator = u"==", value = u"민영")
        docs = self.dbService.getSubscriptionList()
        subscriptionList = []
        for doc in docs:
           subscription = Subscription.from_dict(doc.to_dict())
           subscription.id = doc.id
           subscriptionList.append(subscription)
        return subscriptionList

    def secondUpdateSubscriptions(self):
        # subscription 후처리가 점점 많아 진다. 여기서 모두 호출하자.
        # 순서 matter
        self.__updateWithOriginalInDB()
        self.__updateGeocode()
        self.__updateEstimatedScore()
        self.__updatePriceRates()
    def __updateWithOriginalInDB(self):
        for index, subscription in enumerate(self.subscriptionList):
            doc = self.dbService.getOneSubscription(subscription.getId())
            if doc.exists == True:
                originalSubscription = Subscription.from_dict(doc.to_dict())
                self.subscriptionList[index].updateWithOriginal(originalSubscription)
    def __updateGeocode(self):
        for subscription in self.subscriptionList:
            subscription.updateGeocode()
    def __updateEstimatedScore(self):
        predictor = Predictor()
        for subscription in self.subscriptionList:
            if (subscription.buildingType == "아파트") & (subscription.noRank == False):
                scoreList = predictor.predictScore(subscription)
                print("subscription - score 검즘")
                print(scoreList)
                print(len(scoreList))
                for homeType in subscription.typeList:
                    print(homeType.id)
                print(len(subscription.typeList))
                subscription.setEstimatedScore(scoreList)
    def __updatePriceRates(self):
        docs = self.dbService.getPrices()
        for doc in docs:
            priceRate = PriceRate.from_dict(doc.to_dict())
            priceRate.id = doc.id
            self.priceRateList.append(priceRate)
        for priceRate in self.priceRateList:
            for subscription in self.subscriptionList:
                if int(subscription.id) == int(priceRate.subscriptionId):
                    subscription.setPriceRate(firstPriceRate=float(priceRate.firstRate),
                                              middlePriceRate=float(priceRate.middleRate),
                                              finalPriceRate=float(priceRate.lastRate))


    def saveSubscriptionToDB(self):
        # # print(subsc)
        # for subscription in self.subscriptionList:
        #     print(subscription.title)
        #     if subscription.typeList[0].firstCompetitionRate == None:
        #         print("경쟁률이 ㄴNONE")
        #     else:
        #         print("경쟁률은")
        #         print(subscription.typeList[0].firstCompetitionRate.toDict())
        #     print(subscription.toDict())
        #     doc_ref = self.db.collection(u'subscriptions').document(subscription.getId())
        #     doc_ref.set(subscription.toDict())
        self.dbService.setSubscriptionList(self.subscriptionList)

    # def connectDb(self):
    #     path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    #     cred = credentials.Certificate(path + "/" + self.credFileName)
    #     firebase_admin.initialize_app(cred)
    #     self.db = firestore.client()
    #

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
    def saveSupscriptionsToJson(self):
        subscriptionJsonList = []
        for subscription in self.subscriptionList:
            subscriptionJsonList.append(subscription.toDict())
        with open("subscription20.json", "w") as json_file:
            json.dump(subscriptionJsonList, json_file, default= self.json_default)

    def json_default(self,value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d')
        raise TypeError('not JSON serializable')



# def getArgv(argv):
#     #기본은 STG로 한다.
#     fileName = "./credential/homeguide-stg.json"
#     databaseCategory = ""
#     saveOption = 0
#     try:
#         opts, args = getopt.getopt(argv, "he:s:", ["environment=","saveOption="])
#     except getopt.GetoptError:
#         print("main.py -e <environment> -s <save option>")
#     for opt, arg in opts:
#         if opt == "-h":
#             print("main.py -e <environment> -s <save option>")
#         elif opt in ("-e", "--environment"):
#             if arg in ("prd", "PRD", "PROD", "prod", "production", "PRODUCTION"):
#                 fileName = "./credential/homeguide-prd.json"
#             else:
#                 fileName = "./credential/homeguide-stg.json"
#         elif opt in ("-s", "--saveOption"):
#             if arg in ("price", "priceRate", "priceOnly"):
#                 saveOption = 1
#             else:
#                 saveOption = 0
#     return (fileName, saveOption)
def getArgv(argv):
    #기본은 STG
    environment = "staging"
    try:
        opts, args = getopt.getopt(argv, "he:", ["environment="])
    except getopt.GetoptError:
        print("Main.py -e <environment>")
    for opt, arg in opts:
        if opt == "-h":
            print("main.py -e <environment> -s <save option>")
        elif opt in ("-e", "--environment"):
            environment = arg
    return environment

class DBService(object):
    def __init__(self,environment):
        self.credFileName = EnvironmentController(environment).getCredfileName()
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        cred = credentials.Certificate(path + "/" + self.credFileName)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.queryList = []
    def getSubscriptionList(self):
        queryTerm = self.db.collection(u'subscriptions')
        for query in self.queryList:
            queryTerm = queryTerm.where(query.key, query.operator, query.value)
        self.queryList = []
        docs = queryTerm.stream()
        return docs
    def addCondition(self,key,operator,value):
        self.queryList.append(QueryConditionItem(key = key, operator = operator, value = value))

    def setSubscriptionList(self, subscriptionList):
        for subscription in subscriptionList:
            self.setSubscription(subscription)
    def setSubscription(self, subscription):
        doc_ref = self.db.collection(u'subscriptions').document(subscription.getId())
        doc_ref.set(subscription.toDict())
    def getOneSubscription(self,subscriptionId):
        doc_ref = self.db.collection(u"subscriptions").document(subscriptionId)
        returnNull = False
        doc = doc_ref.get()
        return doc
    def getPrices(self):
        sub_ref = self.db.collection(u"priceRates")
        docs = sub_ref.stream()
        return docs
class QueryConditionItem(object):
    def __init__(self, key, operator, value):
        self.key = key
        self.operator = operator
        self.value = value


class EnvironmentController(object):
    def __init__(self,environment):
        self.__isPRD = False
        prdTuple = ("prd", "PRD", "PROD", "prod", "production", "PRODUCTION")
        if environment in prdTuple:
            self.__isPRD = True
        else:
            self.__isPRD = False
        self.__stgCredFileName = "./credential/homeguide-stg.json"
        self.__prdCredFileName = "./credential/homeguide-prd.json"
    def getCredfileName(self):
        if self.__isPRD:
            return self.__prdCredFileName
        else:
            return self.__stgCredFileName



if __name__ == "__main__":

    # fileName, saveOption = getArgv(sys.argv[1:])
    environment = getArgv(sys.argv[1:])
    # if saveOption == 1:
    #     admin = Admin(fileName)
    #     admin.connectDb()
    #     priceSetting = PriceSetting(fileName = fileName, db = admin.db)
    #     # admin.connectDb()
    #     priceSetting.getSubscriptions()
    #     priceSetting.getPriceRates()
    #     priceSetting.setPriceRate()
    #     priceSetting.saveSubscriptionToDB()
    #
    # else:
        # # 모든 동작 희망할때,
    crawler = ApplyHomeCrawler()
    # admin = Admin(fileName)
    admin = Admin(environment= environment)
    # admin.connectDb()
    crawler.getHomeList(startDate="202008", endDate="202012")
    crawler.getHomeDetail()
    crawler.getHomeCompetitionRate()

    admin.subscriptionList = crawler.subscriptionList

    admin.secondUpdateSubscriptions()
    admin.saveSubscriptionToDB()
    # admin.saveSupscriptionsToJson()

    # applyHome.subscriptionList = []
    # applyHome.getOfficetelList(startDate="202007", endDate="202012")
    # applyHome.getOfficetelDetail()
    # admin.subscriptionList = applyHome.subscriptionList
    # admin.secondUpdateSubscriptions()
    # admin.saveSubscriptionToDB()
    #
    # applyHome.subscriptionList = []
    # applyHome.getNoRankList(startDate="202007", endDate="202012")
    # applyHome.getNoRankDetail()
    # admin.subscriptionList = applyHome.subscriptionList
    # admin.secondUpdateSubscriptions()
    # admin.saveSubscriptionToDB()
    #
    # priceSetting = PriceSetting(fileName,db = admin.db)
    # # # admin.connectDb()
    # priceSetting.getSubscriptions()
    # priceSetting.getPriceRates()
    # priceSetting.setPriceRate()
    # priceSetting.saveSubscriptionToDB()