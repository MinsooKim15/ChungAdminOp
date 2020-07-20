import datetime
import math

class Subscription(object):
    def __init__(self,
                title,
                addressProvinceCode,
                 addressDetailFirstKor,
                 addressDetailSecondKor,
                 buildingType,
                 subscriptionType,
                 supplyType,
                 noRank,
                 noRankDate,
                 hasSpecialSupply,
                 dateSpecialSupplyNear,
                 dateSpecialSupplyOther,
                 dateFirstNear,
                 dateFirstOther,
                 dateSecondNear,
                 dateSecondOther,
                 dateNotice,
                 officialLink,
                 documentLink,
                 dateAnnounce,
                 dateContract,
                 noRankNotSpecified=False,
                 houseManageNo = None):
        self.id = houseManageNo
        self.title = title
        self.addressProvinceCode = addressProvinceCode
        self.addressProvinceKor = addressProvinceCode
        self.addressDetailFirstKor = addressDetailFirstKor
        self.addressDetailSecondKor = addressDetailSecondKor
        self.buildingType = buildingType
        self.subscriptionType = subscriptionType
        self.supplyType = supplyType
        #TODO : 데이터가 불리안으로 되어 있는지 확인이 필요함.
        self.noRank = bool(noRank)
        self.noRankDate = None
        if noRankDate != 0:
            self.noRankDate = noRankDate
        #TODO : 데이터가 불리안으로 되어 있는지 확인이 필요함.
        self.hasSpecialSupply = bool(hasSpecialSupply)
        self.dateSpecialSupplyNear = dateSpecialSupplyNear
        self.dateSpecialSupplyOther = dateSpecialSupplyOther
        self.dateFirstNear = dateFirstNear
        self.dateFirstOther = dateFirstOther
        self.dateSecondNear = dateSecondNear
        self.dateSecondOther = dateSecondOther
        self.dateNotice = dateNotice
        self.zoneType = self.getZoneType()
        self.officialLink = officialLink
        self.documentLink = documentLink
        self.typeList = None
        self.priceDidSet = False
        self.dateAnnounce = dateAnnounce
        self.dateContract = dateContract
        self.noRankNotSpecified = noRankNotSpecified
    def getId(self):
        return self.id

    def getAddressProvinceKor(self):
        addressProvinceDict = {
            "seoul" : "서울시",
        }
        return addressProvinceDict[self.addressProvinceCode]
    def getDateFromString(self,data):
        print(data)
        if data == 0:
            return None
        else:
            return datetime.datetime.strptime(data,"%Y-%m-%d %H:%M:%S")
    def getZoneType(self):
        # 해당 광역시 전체가 투기 지구인 케이스(없음)
        zoneType1ListInProvince = ["세종시"]
        # 해당 지역이 투기 지구인 케이스
        zoneType1ListInDetail = [
            u"강남구", u"서초구", u"송파구", u"강동구", u"용산구", u"성동구", u"노원구", u"마포구", u"양천구", u"영등포구", u"강서구",
        ]
        # 해당 광역시 전체가 투기 지구인 케이스(없음)
        zoneType2ListInProvince = ["서울시"]
        # 해당 지역이 투기 지구인 케이스
        zoneType2ListInDetail1 = [
            u"과천시", u"광명시", u"하남시",u"수성구"
        ]
        zoneType2ListInDetail2 = [
            u"분당구"
        ]
        # 해당 광역시 전체가 투기 지구인 케이스(없음)
        zoneType3ListInProvince = []
        # 해당 지역이 투기 지구인 케이스
        zoneType3ListInDetail1 = [
            u"성남시", u"고양시", u"남양주시", u"구리시", u"기흥시"
        ]
        zoneType3ListInDetail2 = [
            u"산척동", u"동안구", u"수지구", u"기흥구"
        ]

        if self.addressProvinceKor in zoneType1ListInProvince:
            return 1
        elif self.addressDetailFirstKor in zoneType1ListInDetail:
            return 1
        elif self.addressProvinceKor in zoneType2ListInProvince:
            return 2
        elif self.addressDetailFirstKor in zoneType2ListInDetail1:
            return 2
        elif self.addressDetailSecondKor in zoneType2ListInDetail2:
            return 2
        elif self.addressProvinceKor in zoneType1ListInProvince:
            return 3
        elif self.addressDetailFirstKor in zoneType3ListInDetail1:
            return 3
        elif self.addressDetailSecondKor in zoneType3ListInDetail2:
            return 3
        else:
            return 4
    def addTypeList(self,types):
        self.typeList = []
        for type in types:
            type.setZoneType(self.zoneType)
            self.typeList.append(type)
    def toDict(self):
        dict = {
            u"title" : self.title,
            u"addressProvinceCode" : self.addressProvinceCode,
            u"addressProvinceKor" : self.addressProvinceKor,
            u"addressDetailFirstKor" : self.addressDetailFirstKor,
            u"addressDetailSecondKor" : self.addressDetailSecondKor,
            u"buildingType" : self.buildingType,
            u"subscriptionType" : self.subscriptionType,
            u"supplyType" : self.supplyType,
            u"noRank" : self.noRank,
            u"noRankDate" : self.noRankDate,
            u"hasSpecialSupply" : self.hasSpecialSupply,
            u"dateSpecialSupplyNear" : self.dateSpecialSupplyNear,
            u"dateSpecialSupplyOther" : self.dateSpecialSupplyOther,
            u"dateFirstNear" : self.dateFirstNear,
            u"dateFirstOther" : self.dateFirstOther,
            u"dateSecondNear" : self.dateSecondNear,
            u"dateSecondOther" : self.dateSecondOther,
            u"dateNotice" : self.dateNotice,
            u"zoneType" : self.zoneType,
            u"officialLink" : self.officialLink,
            u"documentLink" : self.documentLink,
            u"typeList" : [],
            u"priceDidSet" : self.priceDidSet,
            u"dateAnnounce" : self.dateAnnounce,
            u"dateContract" : self.dateContract,
            u"noRankNotSpecified" : self.noRankNotSpecified
        }
        for type in self.typeList:
            dict[u"typeList"].append(type.toDict())
        return dict
    def setPriceRate(self, firstPriceRate, middlePriceRate, finalPriceRate):
        print("setPriceRate")
        for homeType in self.typeList:
            homeType.setZoneType(self.zoneType)
            print(homeType.title)
            print("homeType")
            homeType.setPriceRate(firstPriceRate, middlePriceRate, finalPriceRate)
        self.priceDidSet = True

    @staticmethod
    def from_dict(source):
        subscription = Subscription(
            title = source[u"title"],
            addressProvinceCode = source[u"addressProvinceCode"],
            addressDetailFirstKor = source[u"addressDetailFirstKor"],
            addressDetailSecondKor = source[u"addressDetailSecondKor"],
            buildingType = source[u"buildingType"],
            subscriptionType = source[u"subscriptionType"],
            supplyType = source[u"supplyType"],
            noRank = source[u"noRank"],
            noRankDate = source[u"noRankDate"],
            hasSpecialSupply = source[u"hasSpecialSupply"],
            dateSpecialSupplyNear = source[u"dateSpecialSupplyNear"],
            dateSpecialSupplyOther = source[u"dateSpecialSupplyOther"],
            dateFirstNear = source[u"dateFirstNear"],
            dateFirstOther = source[u"dateFirstOther"],
            dateSecondNear= source[u"dateSecondNear"],
            dateSecondOther= source[u"dateSecondOther"],
            dateNotice= source[u"dateNotice"],
            dateAnnounce = source[u"dateAnnounce"],
            dateContract= source[u"dateContract"],
            officialLink = source[u"officialLink"],
            documentLink= source[u"documentLink"],
            noRankNotSpecified = source[u"noRankNotSpecified"]
        )
        typeList = []
        for homeType in source[u"typeList"]:
            typeList.append(Type.from_dict(homeType))
        subscription.typeList = typeList
        if u"priceDidSet" in source:
            subscription.priceDidSet = source[u"priceDidSet"]
        return subscription


class Type(object):
    def __init__(self,homeTypeCode, title, size, generalSupply, specialSupply, totalSupply, totalPrice = None, firstPriceRate = None, middlePriceRate  = None, finalPriceRate  = None):
        self.id = homeTypeCode
        self.title = str(title)
        if math.isnan(generalSupply):
            self.generalSupply = None
        else:
            self.generalSupply = int(generalSupply)
        if math.isnan(specialSupply):
            self.specialSupply = None
        else:
          self.specialSupply = int(specialSupply)
        if math.isnan(totalSupply):
            math.totalSupply = None
        else:
            self.totalSupply = int(totalSupply)

        self.sizeInMeter = float(size)
        self.sizeInPy = self.sizeInMeter * 0.3025
        self.sizeInMeter = round(self.sizeInMeter, 2)
        self.sizeInPy = round(self.sizeInPy, 2)
        self.firstPrice = None
        self.middlePrice = None
        self.finalPrice = None
        self.middlePriceLoanAble = None
        self.needMoneyFirst = None
        self.needMoneyFinal = None
        self.loanLimit = None

    def setTotalPrice(self,totalPrice):
        self.totalPrice = Price(totalPrice)
    def setPriceRate(self, firstPriceRate, middlePriceRate, finalPriceRate):
        print("계약금 생성")
        self.firstPrice = Price(self.totalPrice.getNumeric() * firstPriceRate)
        print("중도금 생성")
        self.middlePrice = Price(self.totalPrice.getNumeric() * middlePriceRate)
        self.finalPrice = Price(self.totalPrice.getNumeric() * finalPriceRate)
        # 모든 가격이 정해졌은니 여기서 간단 계산 후 setLoanLimit()에서 최종처리
        self.needMoneyFirst = Price(self.firstPrice.getNumeric() + self.middlePrice.getNumeric())
        self.setLoanLimit()

    def makeId(self, subId, title):
        return str(subId) + "_" + str(title)

    def setZoneType(self,zoneType):
        self.zoneType = zoneType
    def setLoanLimit(self):
        zone12Limit = 900000000
        zone12LoanAbleSmall = 0.4
        zone12LoanAbleBig = 0.2
        zone12NoLoanLimit = 1500000000
        zone3Limit = 900000000
        zone3LoanAbleSmall = 0.6
        zone3LoanAbleBig = 0.3
        zone4LoanAble = 0.7
        middlePriceLoanLimit = 900000000
        # 중도금 대출 가능 여부
        print("중도금 대")
        print("******************")
        if self.totalPrice.getNumeric() > middlePriceLoanLimit:
            print("불가")
            self.middlePriceLoanAble = False
        else:
            print("가능")
            self.middlePriceLoanAble = True

        if (self.zoneType == 1) or (self.zoneType == 2):
            if self.totalPrice.getNumeric() > zone12NoLoanLimit:
                self.loanLimit = 0

            elif self.totalPrice.getNumeric() > zone12Limit:
                smallLoanTemp = zone12Limit * zone12LoanAbleSmall
                bigLoanTemp = (self.totalPrice.getNumeric()- zone12Limit) * zone12LoanAbleBig
                self.loanLimit = smallLoanTemp + bigLoanTemp
            else:
                # 9억 이하 40%
                self.loanLimit = self.totalPrice.getNumeric() * zone12LoanAbleSmall

        elif self.zoneType == 3:
            if self.totalPrice.getNumeric() > zone3Limit:
                smallLoanTemp = (self.totalPrice.getNumeric() *zone3LoanAbleSmall)
                bigLoanTemp = (self.totalPrice.getNumeric() - zone3Limit) * zone3LoanAbleBig
                self.loanLimit = smallLoanTemp + bigLoanTemp
            else:
                self.loanLimit = self.totalPrice.getNumeric() * zone3LoanAbleSmall
        else:
            self.loanLimit= self.totalPrice.getNumeric() * zone4LoanAble
        self.needMoneyFinal = Price(max([0, (self.finalPrice.getNumeric() - self.loanLimit)]))
        self.loanLimit = Price(self.loanLimit)
        



    def toDict(self):
        dict = {
            u"title" : self.title,
            u"generalSupply" : self.generalSupply,
            u"specialSupply" : self.specialSupply,
            u"totalSupply" : self.totalSupply,
            u"totalPriceNumeric" : self.totalPrice.getNumeric(),
            u"totalPriceText" : self.totalPrice.getText(),
            u"sizeInMeter" : self.sizeInMeter,
            u"sizeInPy" : self.sizeInPy,
            u"homeTypeCode" : self.id,
            u"middlePriceLoanAble" : self.middlePriceLoanAble
        }
        if self.firstPrice != None:
            dict[u"firstPriceNumeric"] = self.firstPrice.getNumeric()
            dict[u"firstPriceText"] = self.firstPrice.getText()
        if self.middlePrice != None:
            dict[u"middlePriceNumeric"] = self.middlePrice.getNumeric()
            dict[u"middlePriceText"] = self.middlePrice.getText()
        if self.finalPrice != None:
            dict[u"finalPriceNumeric"] = self.finalPrice.getNumeric()
            dict[u"finalPriceText"] = self.finalPrice.getText()
        if self.middlePriceLoanAble != None:
            dict[u"middlePriceLoanable"] = self.middlePriceLoanAble
        if self.needMoneyFirst != None:
            dict[u"needMoneyFirst"] = self.needMoneyFirst.getText()
        if self.needMoneyFinal != None:
            dict[u"needMoneyFinal"] = self.needMoneyFinal.getText()
        if self.loanLimit != None:
            dict[u"loanLimitNumeric"] = self.loanLimit.getNumeric()
            dict[u"loanLimitText"] = self.loanLimit.getText()

        return dict
    def getId(self):
        return self.id

    @staticmethod
    def from_dict(source):
        homeType = Type(
            homeTypeCode = source[u"homeTypeCode"],
            title = source[u"title"],
            size = source[u"sizeInMeter"],
            generalSupply = source[u"generalSupply"],
            specialSupply= source[u"specialSupply"],
            totalSupply = source[u"totalSupply"]
        )
        # TODO : setTotalPrice만 튀어나온게 보기 싫다.
        homeType.setTotalPrice(
            totalPrice = source[u"totalPriceNumeric"]
        )
        return homeType

class Price(object):
    def __init__(self,price):
        if math.isnan(price):
            self.numeric = None
            self.inText = None
        else:
            self.numeric = int(price)
            self.inText = self.priceToText(price)
        print("Price Init!!@@@@@@@@@@")
        print(self.numeric)
        print(self.inText)
    def priceToText(self, price):
        return str(round(price / 100000000, 2)) + "억 원"
    def getText(self):
        return self.inText
    def getNumeric(self):
        return self.numeric

class Guide(object):
    def __init__(self, id, title, subtitle, webUrl, imgUrl= None):
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.imgUrl = imgUrl
        self.webUrl = webUrl
    def toDict(self):
        dict = {
            u"title" : self.title,
            u"subtitle" : self.subtitle,
            u"imgUrl" : self.imgUrl,
            u"webUrl" : self.webUrl
        }
        return dict
    def getId(self):
        return self.id