import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from models import *
import datetime
import math
import time
from ScorePredictor.Predictor import Predictor


class ApplyHomeCrawler(object):
    def __init__(self):
        self.listUrl = "https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancListView.do"
        self.listParams = {
            "beginPd": "",
            "endPd": "",
            "pageIndex": 1,
            "pageSelAt": "Y",
            "gvPgmId": "AIA01M01"
        }
        self.homeList = []
        self.detailUrl = "https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancDetail.do"
        self.detailParams = {
            "houseManageNo": "",
            "pblancNo": "",
            "gvPgmId": "AIA01M01"
        }
        self.competitionListUrl = "https://www.applyhome.co.kr/ai/aia/selectAPTCompetitionPopup.do"
        self.subscriptionList = []
        self.officetelListUrl = "https://www.applyhome.co.kr/ai/aia/selectOtherLttotPblancListView.do"

        self.officetelDetailUrl = "https://www.applyhome.co.kr/ai/aia/selectPRMOLttotPblancDetailView.do"
        self.noRankListUrl = "https://www.applyhome.co.kr/ai/aia/selectAPTRemndrLttotPblancListView.do"
        self.noRankDetailUrl = "https://www.applyhome.co.kr/ai/aia/selectAPTRemndrLttotPblancDetailView.do"

    def getHomeList(self, startDate, endDate):
        self.listParams["beginPd"] = startDate
        self.listParams["endPd"] = endDate
        targetUrl = self.getListUrl(type=1)
        req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        bsObject = BeautifulSoup(html, "html.parser")
        totalCount = bsObject.body.find_all("p", class_="total_txt")[0].find("b").get_text()
        totalCount = int(totalCount)
        targetPageNumber = int(math.ceil(totalCount / 10.0))
        for page in range(targetPageNumber):
            self.listParams["pageIndex"] = page + 1
            targetUrl = self.getListUrl(type=1)
            html = urlopen(targetUrl)
            bsObject = BeautifulSoup(html, "html.parser")
            targetList = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")
            print(targetList)
            for target in targetList:
                pbNo = target.get("data-pbno")
                homeNo = target.get("data-hmno")
                homeName = target.get("data-honm")
                subscriptionType = target.find_all("td")[1].get_text()
                supplyType = target.find_all("td")[2].get_text()
                if supplyType == "분양주택":
                    supplyType = "분양"
                else:
                    supplyType = "임대"
                print("경쟁률 정보!!!!!!!!!!!!")
                print(homeNo)
                print(homeName)
                print(target.find_all("td")[10])
                print(target.find_all("td")[10].get_text())
                buttonList = target.find_all("td")[10].find_all("button")
                print(buttonList)
                hasCompetitionData = False
                if len(buttonList) != 0:
                    hasCompetitionData = True
                companyName = target.find_all("td")[4].get_text()
                home = Home(pbNo=pbNo, homeNo=homeNo, homeName=homeName, subscriptionType=subscriptionType,
                            supplyType=supplyType, companyName=companyName, hasCompetitionData=hasCompetitionData)
                self.homeList.append(home)
        print(self.homeList)  # 웹 문서 전체가 출력됩니다.

    def getListUrl(self, type):
        # type 정의
        # 1 : 아파트
        # 2 : 오피스텔
        # 3 : 무가점
        if int(type) == 1:
            targetUrl = self.listUrl
            self.listParams["gvPgmId"] = "AIA01M01"
        elif int(type) == 2:
            targetUrl = self.officetelListUrl
            self.listParams["gvPgmId"] = "AIA02M01"
        else:
            targetUrl = self.noRankListUrl
            self.listParams["gvPgmId"] = "AIA03M01"
        parts = urlparse(targetUrl)
        parts = parts._replace(query=urlencode(self.listParams))
        new_url = urlunparse(parts)
        return new_url

    def getHomeCompetitionUrl(self, homeNo, pbNo, houseName):
        self.detailParams["houseManageNo"] = homeNo
        self.detailParams["pblancNo"] = pbNo
        self.detailParams["houseNm"] = houseName
        self.detailParams["gvPgmId"] = "AIA01M01"
        targetUrl = self.competitionListUrl
        parts = urlparse(targetUrl)
        parts = parts._replace(query=urlencode(self.detailParams))
        new_url = urlunparse(parts)
        self.detailParams = {}
        return new_url

    def getHomeCompetitionRate(self):
        print("경쟁률 정보 받기@@@@@@@@@@@@@@@@@@@")
        for home in self.homeList:
            print(home.homeName)
            print("경쟁률 정보가 있는가?")
            print(home.hasCompetitionData)
            subscriptionIndex, subscription = self.getSubscriptionMatchId(home.homeNo)
            if (home.subType == "민영") & (subscriptionIndex != None) & (home.hasCompetitionData == True):
                targetUrl = self.getHomeCompetitionUrl(homeNo=home.homeNo, pbNo=home.pbNo, houseName=home.homeName)
                req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
                html = urlopen(req).read()
                bsObject = BeautifulSoup(html, "html.parser")
                targetList = bsObject.body.find("table").find("tbody").find_all("tr")
                # data-ty를 먼저 구한다. 그리고 그 걸 기준으로 iterate
                dataTypeList = []
                for target in targetList:
                    dataType = target.get("data-ty")
                    if dataType not in dataTypeList:
                        dataTypeList.append(dataType)
                for dataTypeIndex, dataType in enumerate(dataTypeList):
                    targetItems = bsObject.body.find("table").find("tbody").find_all("tr", attrs={"data-ty": dataType})
                    firstAmountOfApplicants = int(targetItems[0].find_all("td")[4].get_text().replace(',', ''))
                    firstCompetitionRate = targetItems[0].find_all("td")[5].get_text()
                    firstNotDone = False
                    firstIsFallShort = False
                    if (firstAmountOfApplicants == 0) or (firstCompetitionRate == "-"):
                        firstCompetitionRate = None
                        firstNotDone = True
                    elif (list(firstCompetitionRate.strip())[0] == "("):
                        firstCompetitionRate = None
                        firstIsFallShort = True
                    else:
                        firstCompetitionRate = float(firstCompetitionRate)
                    secondAmountOfApplicants = int(targetItems[2].find_all("td")[4].get_text().replace(',', ''))
                    secondCompetitionRate = targetItems[2].find_all("td")[5].get_text()
                    secondNotDone = False
                    secondIsFallShort = False
                    if (secondAmountOfApplicants == 0) or (secondCompetitionRate == "-"):
                        secondCompetitionRate = None
                        secondNotDone = True
                    elif (list(secondCompetitionRate.strip())[0] == "("):
                        secondCompetitionRate = None
                        secondIsFallShort = True
                    else:
                        secondCompetitionRate = float(secondCompetitionRate)
                    dontSaveScore = False
                    try:
                        minScore = targetItems[0].find_all("td")[8].get_text()
                    except IndexError as E:
                        dontSaveScore = True
                    if dontSaveScore == False:
                        if (minScore == "-") or (minScore == "0"):
                            dontSaveScore = True
                        else:
                            minScore = float(minScore)
                        if dontSaveScore == False:
                            maxScore = float(targetItems[0].find_all("td")[9].get_text())
                            averageScore = float(targetItems[0].find_all("td")[10].get_text())
                        if dontSaveScore == False:
                            self.subscriptionList[subscriptionIndex].typeList[dataTypeIndex].setWinningScore(
                                minScore=minScore, maxScore=maxScore, averageScore=averageScore)
                        if firstNotDone == False:
                            self.subscriptionList[subscriptionIndex].typeList[dataTypeIndex].setFirstCompetitionRate(
                                isFallShort=firstIsFallShort, applicant=firstAmountOfApplicants,
                                rate=firstCompetitionRate)
                        if secondNotDone == False:
                            self.subscriptionList[subscriptionIndex].typeList[dataTypeIndex].setSecondCompetitionRate(
                                isFallShort=secondIsFallShort, applicant=secondAmountOfApplicants,
                                rate=secondCompetitionRate)

    def getSubscriptionMatchId(self, id):
        for index, subscription in enumerate(self.subscriptionList):
            if subscription.id == id:
                return (index, subscription)
        return (None, None)

    def getHomeDetail(self):
        for home in self.homeList:
            targetUrl = self.getDetailUrl(homeNo=home.homeNo, pbNo=home.pbNo)
            req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read()
            bsObject = BeautifulSoup(html, "html.parser")

            # 첫번째 테이블 로직
            retry = False
            tryAgain = False
            # 첫번째 테이블 로직
            try:
                addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[
                    1].get_text()
            except IndexError as E:
                print("최초 에러!")
                tryAgain = True
            if (tryAgain == True) & (retry == False):
                time.sleep(30)
                req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
                html = urlopen(req).read()
                bsObject = BeautifulSoup(html, "html.parser")
                retry = True
            elif (tryAgain == True) & (retry == True):
                pass

            if (tryAgain == True):
                try:
                    addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[
                        1].get_text()
                except IndexError as E:
                    print("재시도 후 에러")
                    pass
            addressProvinceCode = addressText.split(" ")[0].replace(" ", "")

            if len(addressText.split(" ")) > 1:
                addressDetailFirstKor = addressText.split(" ")[1].strip()
            else:
                addressDetailFirstKor = " "
            if len(addressText.split(" ")) > 2:
                addressDetailSecondKor = " ".join(addressText.split(" ")[2:]).strip()
            else:
                addressDetailSecondKor = " "

            totalSupply = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[1].find_all("td")[
                1].get_text().strip()
            totalSupply = totalSupply[:-2]
            contact = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[3].find_all("td")[
                1].get_text().strip()
            contact = contact.split(" ")[1]
            print(addressProvinceCode)
            print(addressDetailFirstKor)
            print(addressDetailSecondKor)
            print(totalSupply)
            print(totalSupply[:-2])
            print(contact)
            print("=============")
            skipData = False
            # 청약 일정 관련
            dateTable = bsObject.body.find_all("table")[1]
            noticeDate = dateTable.find_all("tr")[0].find("td").get_text().strip()
            noticeDate = noticeDate.split(" ")[0]
            try:
                noticeDate = datetime.datetime.strptime(noticeDate, "%Y-%m-%d")
            except ValueError as e:
                noticeDate = None
                skipData = True
            hasSpecialSupply = False
            if skipData == False:
                if len(dateTable.find_all("tr")) == 7:
                    hasSpecialSupply = True
                if hasSpecialSupply:
                    dateSpecialSupplyNear = dateTable.find_all("tr")[2].find_all("td")[1].get_text().strip().split("~")[
                        0]
                    dateSpecialSupplyOther = \
                    dateTable.find_all("tr")[2].find_all("td")[2].get_text().strip().split("~")[0]
                    dateFirstNear = dateTable.find_all("tr")[3].find_all("td")[1].get_text().strip().split("~")[0]
                    dateFirstOther = dateTable.find_all("tr")[3].find_all("td")[2].get_text().strip().split("~")[0]
                    dateSecondNear = dateTable.find_all("tr")[4].find_all("td")[1].get_text().strip().split("~")[0]
                    dateSecondOther = dateTable.find_all("tr")[4].find_all("td")[2].get_text().strip().split("~")[0]
                    dateAnnounce = dateTable.find_all("tr")[5].find("td").get_text().split(" ")[0].split("~")[0].strip()
                    dateContract = dateTable.find_all("tr")[6].find("td").get_text().strip().split(" ")[0].split("~")[0]
                    dateSpecialSupplyNear = datetime.datetime.strptime(dateSpecialSupplyNear, "%Y-%m-%d")
                    dateSpecialSupplyOther = datetime.datetime.strptime(dateSpecialSupplyOther, "%Y-%m-%d")
                else:
                    dateSpecialSupplyNear = None
                    dateSpecialSupplyOther = None
                    dateFirstNear = dateTable.find_all("tr")[2].find_all("td")[1].get_text().strip().split("~")[0]
                    dateFirstOther = dateTable.find_all("tr")[2].find_all("td")[2].get_text().strip().split("~")[0]
                    dateSecondNear = dateTable.find_all("tr")[3].find_all("td")[1].get_text().strip().split("~")[0]
                    dateSecondOther = dateTable.find_all("tr")[3].find_all("td")[2].get_text().strip().split("~")[0]
                    dateAnnounce = dateTable.find_all("tr")[4].find("td").get_text().split(" ")[0].split("~")[0].strip()
                    dateContract = dateTable.find_all("tr")[5].find("td").get_text().strip().split(" ")[0].split("~")[0]

                if dateFirstNear == "":
                    dateFirstNear = None
                else:
                    dateFirstNear = datetime.datetime.strptime(dateFirstNear, "%Y-%m-%d")
                if dateFirstOther == "":
                    dateFirstOther = None

                else:
                    dateFirstOther = datetime.datetime.strptime(dateFirstOther, "%Y-%m-%d")
                if dateSecondNear == "":
                    deteSecondNear = None
                else:
                    dateSecondNear = datetime.datetime.strptime(dateSecondNear, "%Y-%m-%d")
                if dateSecondOther == "":
                    dateSecondOther = None
                else:
                    dateSecondOther = datetime.datetime.strptime(dateSecondOther, "%Y-%m-%d")
                if dateAnnounce == "":
                    dateAnnounce = None
                else:
                    dateAnnounce = datetime.datetime.strptime(dateAnnounce, "%Y-%m-%d")
                if dateContract == "":
                    dateContract = None
                else:
                    dateContract = datetime.datetime.strptime(dateContract, "%Y-%m-%d")


            else:
                dateSpecialSupplyNear = None
                dateSpecialSupplyOther = None
                dateFirstNear = None
                dateFirstOther = None
                dateSecondNear = None
                dateSecondOther = None
                dateAnnounce = None
                dateContract = None
            # TODO : noticeDate to DateTime

            # dateSpecialSupplyNear = dateTable.find_all("tr")[1].find

            # 공급 관련
            supplyTable = bsObject.body.find_all("table")[2]
            # 마지막 값은 Total이라 따로 관리한다.
            rowList = supplyTable.find("tbody").find_all("tr")[:-1]
            homeTypeList = []
            for row in rowList:
                tdList = row.find_all("td")
                newTdList = []
                for td in tdList:
                    if (td.has_attr("rowspan")) == False:
                        newTdList.append(td)

                homeTypeName = newTdList[0].get_text().strip()
                homeTypeSize = newTdList[1].get_text().strip()
                homeTypeGeneralSupply = newTdList[2].get_text().strip()
                homeTypeSpecialSupply = newTdList[3].get_text().strip()
                homeTypeTotalSupply = newTdList[4].get_text().strip()
                # print()
                homeTypeCode = row.find_all("td")[5].get_text().strip()
                homeTypeCode = home.homeNo + "_" + homeTypeName
                homeType = Type(
                    homeTypeCode=homeTypeCode,
                    title=homeTypeName,
                    size=homeTypeSize,
                    generalSupply=int(homeTypeGeneralSupply.replace(',', '')),
                    specialSupply=int(homeTypeSpecialSupply.replace(',', '')),
                    totalSupply=int(homeTypeTotalSupply.replace(',', ''))
                )
                homeTypeList.append(homeType)
            # 총 Table 개수를 체크하자 - 특별공급인 아니면 5개의 테이블
            # priceTable
            priceTable = bsObject.body.find_all("table")[-2]
            priceList = priceTable.find("tbody").find_all("tr")
            for index, homeType in enumerate(homeTypeList):
                homeTypeTotalPrice = int(priceList[index].find_all("td")[1].get_text().replace(',', '')) * 10000
                homeType.setTotalPrice(homeTypeTotalPrice)
            # 모집 공고문 찾기
            documentLink = None
            if bsObject.body.find("dl", class_="pop_btn_txt") != None:
                try:
                    documentLink = bsObject.body.find("dl", class_="pop_btn_txt").find("dd").find("a").get(
                        "href").strip()
                    documentLink = "https://www.applyhome.co.kr" + documentLink
                except AttributeError as e:
                    documentLink = None

            subscription = Subscription(
                houseManageNo=home.homeNo,
                title=home.homeName,
                addressProvinceCode=addressProvinceCode,
                addressDetailFirstKor=addressDetailFirstKor,
                addressDetailSecondKor=addressDetailSecondKor,
                buildingType="아파트",
                supplyType=home.supplyType,
                subscriptionType=home.subType,
                noRank=False,
                noRankDate=None,
                hasSpecialSupply=hasSpecialSupply,
                dateSpecialSupplyNear=dateSpecialSupplyNear,
                dateSpecialSupplyOther=dateSpecialSupplyOther,
                dateFirstNear=dateFirstNear,
                dateFirstOther=dateFirstOther,
                dateSecondNear=dateSecondNear,
                dateSecondOther=dateSecondOther,
                dateNotice=noticeDate,
                officialLink=targetUrl,
                documentLink=documentLink,
                dateAnnounce=dateAnnounce,
                dateContract=dateContract,
                noRankNotSpecified=False
            )
            subscription.addTypeList(homeTypeList)
            self.subscriptionList.append(subscription)

    def getDetailUrl(self, homeNo, pbNo):
        self.detailParams = {
            "houseManageNo": "",
            "pblancNo": "",
            "gvPgmId": ""
        }
        self.detailParams["houseManageNo"] = homeNo
        self.detailParams["pblancNo"] = pbNo
        parts = urlparse(self.detailUrl)
        parts = parts._replace(query=urlencode(self.detailParams))
        new_url = urlunparse(parts)
        return new_url

    def getOfficetelDetailUrl(self, homeNo, pbNo, houseSecd):
        # TODO: 끝나면 클렌징 로직 추가
        self.detailParams = {
            "houseManageNo": "",
            "pblancNo": "",
            "gvPgmId": ""
        }
        self.detailParams["houseManageNo"] = homeNo
        self.detailParams["pblancNo"] = pbNo
        self.detailParams["houseSecd"] = houseSecd
        self.detailParams["gvPgmId"] = "AIA02M01"
        parts = urlparse(self.officetelDetailUrl)
        parts = parts._replace(query=urlencode(self.detailParams))
        new_url = urlunparse(parts)
        return new_url

    def getNoRankDetailUrl(self, homeNo, pbNo, houseSecd):
        self.detailParams = {
            "houseManageNo": "",
            "pblancNo": "",
            "gvPgmId": ""
        }
        # TODO: 끝나면 클렌징 로직 추가
        self.detailParams["houseManageNo"] = homeNo
        self.detailParams["pblancNo"] = pbNo
        # self.detailParams["houseSecd"] = houseSecd
        self.detailParams["gvPgmId"] = "AIA03M01"
        parts = urlparse(self.noRankDetailUrl)
        parts = parts._replace(query=urlencode(self.detailParams))
        new_url = urlunparse(parts)
        return new_url

    def getOfficetelList(self, startDate, endDate):
        self.listParams["beginPd"] = startDate
        self.listParams["endPd"] = endDate
        targetUrl = self.getListUrl(type=2)
        req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        bsObject = BeautifulSoup(html, "html.parser")
        totalCount = bsObject.body.find_all("p", class_="total_txt")[0].find("b").get_text()
        totalCount = int(totalCount)
        targetPageNumber = int(math.ceil(totalCount / 10.0))
        for page in range(targetPageNumber):
            self.listParams["pageIndex"] = page + 1
            targetUrl = self.getListUrl(type=2)
            html = urlopen(targetUrl)
            bsObject = BeautifulSoup(html, "html.parser")
            targetList = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")
            for target in targetList:
                pbNo = target.get("data-pbno")
                homeNo = target.get("data-hmno")
                homeName = target.get("data-honm")
                buildingType = target.find_all("td")[0].get_text()
                houseSecd = target.get("data-hsecd")
                if buildingType == "오피스텔" or buildingType == "도시형생활주택":
                    supplyType = "분양주택"
                else:
                    supplyType = "임대"

                home = Home(pbNo=pbNo, homeNo=homeNo, homeName=homeName, supplyType=supplyType,
                            buildingType=buildingType, houseSecd=houseSecd)
                self.homeList.append(home)

    def getOfficetelDetail(self):
        print("officetel/기타 주택 개수")
        print(len(self.homeList))
        for home in self.homeList:
            print("======================================")
            print("주택 데이터 처리 시작")
            print(home.homeName)

            targetUrl = self.getOfficetelDetailUrl(homeNo=home.homeNo, pbNo=home.pbNo, houseSecd=home.houseSecd)
            req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read()
            bsObject = BeautifulSoup(html, "html.parser")
            print(html)
            retry = False
            tryAgain = False
            # 첫번째 테이블 로직
            try:
                addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[
                    1].get_text()
            except IndexError as E:
                print("최초 에러!")
                tryAgain = True

            if (tryAgain == True) & (retry == False):
                time.sleep(30)
                req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
                html = urlopen(req).read()
                bsObject = BeautifulSoup(html, "html.parser")
                retry = True
            elif (tryAgain == True) & (retry == True):
                pass

            if (tryAgain == True):
                try:
                    addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[
                        1].get_text()
                except IndexError as E:
                    print("재시도 후 에러")
                    continue

            addressProvinceCode = addressText.split(" ")[0].replace(" ", "")
            if len(addressText.split(" ")) > 1:
                addressDetailFirstKor = addressText.split(" ")[1].strip()
            else:
                addressDetailFirstKor = " "
            if len(addressText.split(" ")) > 2:
                addressDetailSecondKor = " ".join(addressText.split(" ")[2:]).strip()
            else:
                addressDetailSecondKor = " "
            totalSupply = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[1].find_all("td")[
                1].get_text().strip()
            totalSupply = totalSupply[:-2]
            contact = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[2].find_all("td")[
                1].get_text().strip()
            contact = contact.split(" ")[1]
            skipData = False
            # 청약 일정 관련
            dateTable = bsObject.body.find_all("table")[1]
            noticeDate = dateTable.find_all("tr")[0].find("td").get_text().strip()
            noticeDate = noticeDate.split(" ")[0]
            try:
                noticeDate = datetime.datetime.strptime(noticeDate, "%Y-%m-%d")
            except ValueError as e:
                noticeDate = None
                skipData = True
            hasSpecialSupply = False
            if skipData == False:
                # 슬프지만 지금은 일단 가장 후순위 정보로 놔둠 ㅜㅜ 수정해야 한다.
                dateSecondOther = dateTable.find_all("tr")[1].find("td").get_text().strip().split("~")[0].strip()
                dateAnnounce = dateTable.find_all("tr")[2].find("td").get_text().split(" ")[0].split("~")[0].split("(")[
                    0].strip()
                dateContract = dateTable.find_all("tr")[3].find("td").get_text().strip().split(" ")[0].split("~")[0]
                dateAnnounce = datetime.datetime.strptime(dateAnnounce, "%Y-%m-%d")
                dateSecondOther = datetime.datetime.strptime(dateSecondOther, "%Y-%m-%d")
                dateContract = datetime.datetime.strptime(dateContract, "%Y-%m-%d")
                dateSpecialSupplyNear = None
                dateSpecialSupplyOther = None
                dateFirstNear = None
                dateFirstOther = None
                dateSecondNear = None
            else:
                dateSpecialSupplyNear = None
                dateSpecialSupplyOther = None
                dateFirstNear = None
                dateFirstOther = None
                dateSecondNear = None
                dateSecondOther = None
                dateAnnounce = None
                dateContract = None
            # TODO : noticeDate to DateTime

            print("2순위 기타(접수 시작일)", dateSecondOther)
            print("당첨자 발표일", dateAnnounce)
            print("계약일", dateContract)

            # 공급 관련
            supplyTable = bsObject.body.find_all("table")[2]
            rowList = supplyTable.find("tbody").find_all("tr")
            homeTypeList = []
            for row in rowList:
                tdList = row.find_all("td")
                newTdList = []
                for td in tdList:
                    if (td.has_attr("rowspan")) == False:
                        newTdList.append(td)

                # TODO : 군 정보는 안 씀. 이건 데이터 흐트러 질까봐ㅜㅜ
                homeTypeName = newTdList[1].get_text().strip()
                homeTypeSize = newTdList[2].get_text().strip()
                homeTypeTotalSupply = newTdList[3].get_text().strip()
                # print()
                homeTypeCode = row.find_all("td")[4].get_text().strip()
                homeTypeCode = home.homeNo + "_" + homeTypeName
                homeType = Type(
                    homeTypeCode=homeTypeCode,
                    title=homeTypeName,
                    size=homeTypeSize,
                    generalSupply=int(homeTypeTotalSupply),
                    specialSupply=int(0),
                    totalSupply=int(homeTypeTotalSupply)
                )
                homeTypeList.append(homeType)
            # 총 Table 개수를 체크하자 - 특별공급인 아니면 5개의 테이블
            # priceTable
            priceTable = bsObject.body.find_all("table")[-2]
            priceList = priceTable.find("tbody").find_all("tr")
            for index, homeType in enumerate(homeTypeList):
                homeTypeTotalPrice = int(priceList[index].find_all("td")[2].get_text().replace(',', '')) * 10000
                homeType.setTotalPrice(homeTypeTotalPrice)
            # 모집 공고문 찾기
            documentLink = None
            if bsObject.body.find("dl", class_="pop_btn_txt") != None:
                try:
                    documentLink = bsObject.body.find("dl", class_="pop_btn_txt").find("dd").find("a").get(
                        "href").strip()
                    documentLink = "https://www.applyhome.co.kr" + documentLink
                except AttributeError as e:
                    documentLink = None

            subscription = Subscription(
                houseManageNo=home.homeNo,
                title=home.homeName,
                addressProvinceCode=addressProvinceCode,
                addressDetailFirstKor=addressDetailFirstKor,
                addressDetailSecondKor=addressDetailSecondKor,
                buildingType=home.buildingType,
                supplyType=home.supplyType,
                subscriptionType=home.subType,
                noRank=False,
                noRankDate=None,
                hasSpecialSupply=hasSpecialSupply,
                dateSpecialSupplyNear=dateSpecialSupplyNear,
                dateSpecialSupplyOther=dateSpecialSupplyOther,
                dateFirstNear=dateFirstNear,
                dateFirstOther=dateFirstOther,
                dateSecondNear=dateSecondNear,
                dateSecondOther=dateSecondOther,
                dateNotice=noticeDate,
                officialLink=targetUrl,
                documentLink=documentLink,
                dateAnnounce=dateAnnounce,
                dateContract=dateContract,
                noRankNotSpecified=False
            )
            subscription.addTypeList(homeTypeList)
            self.subscriptionList.append(subscription)

    def getNoRankList(self, startDate, endDate):
        self.listParams["beginPd"] = startDate
        self.listParams["endPd"] = endDate
        targetUrl = self.getListUrl(type=3)
        req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        bsObject = BeautifulSoup(html, "html.parser")
        totalCount = bsObject.body.find_all("p", class_="total_txt")[0].find("b").get_text()
        totalCount = int(totalCount)
        targetPageNumber = int(math.ceil(totalCount / 10.0))
        for page in range(targetPageNumber):
            self.listParams["pageIndex"] = page + 1
            targetUrl = self.getListUrl(type=3)
            html = urlopen(targetUrl)
            bsObject = BeautifulSoup(html, "html.parser")
            targetList = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")
            print(targetList)
            for target in targetList:
                pbNo = target.get("data-pbno")
                homeNo = target.get("data-hmno")
                homeName = target.get("data-honm")
                houseSecd = target.get("data-hsecd")
                supplyType = "분양"
                home = Home(pbNo=pbNo, homeNo=homeNo, homeName=homeName, supplyType=supplyType, houseSecd=houseSecd)
                self.homeList.append(home)
        print(self.homeList)  # 웹 문서 전체가 출력됩니다.

    def getNoRankDetail(self):
        print("무가점 개수")
        print(len(self.homeList))
        for home in self.homeList:
            print("======================================")
            print("주택 데이터 처리 시작")
            print(home.homeName)

            targetUrl = self.getNoRankDetailUrl(homeNo=home.homeNo, pbNo=home.pbNo, houseSecd=home.houseSecd)
            req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read()
            bsObject = BeautifulSoup(html, "html.parser")
            print(bsObject.body.find_all("table"))
            # 첫번째 테이블 로직
            retry = False
            tryAgain = False
            # 첫번째 테이블 로직
            try:
                addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[
                    1].get_text()
            except IndexError as E:
                print("최초 에러!")
                tryAgain = True
            if (tryAgain == True) & (retry == False):
                time.sleep(30)
                req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
                html = urlopen(req).read()
                bsObject = BeautifulSoup(html, "html.parser")
                retry = True
            elif (tryAgain == True) & (retry == True):
                pass

            if (tryAgain == True):
                try:
                    addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[
                        1].get_text()
                except IndexError as E:
                    print("재시도 후 에러")
                    pass

            addressProvinceCode = addressText.split(" ")[0].replace(" ", "")
            if len(addressText.split(" ")) > 1:
                addressDetailFirstKor = addressText.split(" ")[1].strip()
            else:
                addressDetailFirstKor = " "
            if len(addressText.split(" ")) > 2:
                addressDetailSecondKor = " ".join(addressText.split(" ")[2:]).strip()
            else:
                addressDetailSecondKor = " "
            totalSupply = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[1].find_all("td")[
                1].get_text().strip()
            totalSupply = totalSupply[:-2]
            contact = None
            print(addressProvinceCode)
            print(addressDetailFirstKor)
            print(addressDetailSecondKor)
            print(totalSupply)
            print(totalSupply[:-2])
            print(contact)
            print("=============")
            skipData = False
            # 청약 일정 관련
            dateTable = bsObject.body.find_all("table")[1]
            noticeDate = dateTable.find_all("tr")[0].find("td").get_text().strip()
            noticeDate = noticeDate.split(" ")[0]
            try:
                noticeDate = datetime.datetime.strptime(noticeDate, "%Y-%m-%d")
            except ValueError as e:
                noticeDate = None
                skipData = True
            hasSpecialSupply = False
            if skipData == False:
                # 슬프지만 지금은 일단 가장 후순위 정보로 놔둠 ㅜㅜ 수정해야 한다.
                dateSecondOther = dateTable.find_all("tr")[1].find("td").get_text().strip().split("~")[0].strip()
                dateAnnounce = dateTable.find_all("tr")[2].find("td").get_text().split(" ")[0].split("~")[0].split("(")[
                    0].strip()
                dateContract = dateTable.find_all("tr")[3].find("td").get_text().strip().split(" ")[0].split("~")[0]
                dateAnnounce = datetime.datetime.strptime(dateAnnounce, "%Y-%m-%d")
                dateSecondOther = datetime.datetime.strptime(dateSecondOther, "%Y-%m-%d")
                dateContract = datetime.datetime.strptime(dateContract, "%Y-%m-%d")
                dateSpecialSupplyNear = None
                dateSpecialSupplyOther = None
                dateFirstNear = None
                dateFirstOther = None
                dateSecondNear = None
            else:
                dateSpecialSupplyNear = None
                dateSpecialSupplyOther = None
                dateFirstNear = None
                dateFirstOther = None
                dateSecondNear = None
                dateSecondOther = None
                dateAnnounce = None
                dateContract = None
            # TODO : noticeDate to DateTime

            print("2순위 기타(접수 시작일)", dateSecondOther)
            print("당첨자 발표일", dateAnnounce)
            print("계약일", dateContract)

            # 공급 관련
            supplyTable = bsObject.body.find_all("table")[2]
            rowList = supplyTable.find("tbody").find_all("tr")
            homeTypeList = []
            for row in rowList:
                tdList = row.find_all("td")
                newTdList = []
                for td in tdList:
                    if (td.has_attr("rowspan")) == False:
                        newTdList.append(td)

                # TODO : 군 정보는 안 씀. 이건 데이터 흐트러 질까봐ㅜㅜ
                homeTypeName = newTdList[0].get_text().strip()
                homeTypeSize = 0
                homeTypeTotalSupply = newTdList[1].get_text().strip()

                noRankNotSpecified = False
                if homeTypeTotalSupply == "-":
                    homeTypeTotalSupply = 0
                    noRankNotSpecified = True

                # print()
                # 홈타입 코드가 없어 임의 생성
                homeTypeCode = home.homeNo + "_" + homeTypeName
                homeType = Type(
                    homeTypeCode=homeTypeCode,
                    title=homeTypeName,
                    size=homeTypeSize,
                    generalSupply=int(homeTypeTotalSupply),
                    specialSupply=int(0),
                    totalSupply=int(homeTypeTotalSupply)
                )
                homeTypeList.append(homeType)

            # 비우면 미동작해서 0으로 채움
            for index, homeType in enumerate(homeTypeList):
                homeType.setTotalPrice(0)
            # 모집 공고문 찾기
            documentLink = None
            if bsObject.body.find("dl", class_="pop_btn_txt") != None:
                try:
                    documentLink = bsObject.body.find("dl", class_="pop_btn_txt").find("dd").find("a").get(
                        "href").strip()
                    documentLink = "https://www.applyhome.co.kr" + documentLink
                except AttributeError as e:
                    documentLink = None

            subscription = Subscription(
                houseManageNo=home.homeNo,
                title=home.homeName,
                addressProvinceCode=addressProvinceCode,
                addressDetailFirstKor=addressDetailFirstKor,
                addressDetailSecondKor=addressDetailSecondKor,
                buildingType=home.buildingType,
                supplyType=home.supplyType,
                subscriptionType=home.subType,
                noRank=True,
                noRankDate=None,
                hasSpecialSupply=hasSpecialSupply,
                dateSpecialSupplyNear=dateSpecialSupplyNear,
                dateSpecialSupplyOther=dateSpecialSupplyOther,
                dateFirstNear=dateFirstNear,
                dateFirstOther=dateFirstOther,
                dateSecondNear=dateSecondNear,
                dateSecondOther=dateSecondOther,
                dateNotice=noticeDate,
                officialLink=targetUrl,
                documentLink=documentLink,
                dateAnnounce=dateAnnounce,
                dateContract=dateContract,
                noRankNotSpecified=noRankNotSpecified
            )
            subscription.addTypeList(homeTypeList)
            self.subscriptionList.append(subscription)


class Home(object):
    def __init__(self, pbNo, homeNo, homeName, supplyType, buildingType="아파트", subscriptionType="", companyName="",
                 houseSecd="", hasCompetitionData=False):
        self.pbNo = pbNo
        self.homeNo = homeNo
        self.homeName = homeName
        self.supplyType = supplyType
        self.subType = subscriptionType
        self.companyName = companyName
        self.houseSecd = houseSecd
        self.buildingType = buildingType
        self.hasCompetitionData = hasCompetitionData


if __name__ == "__main__":
    applyHome = ApplyHomeCrawler()
    # applyHome.getHomeList(startDate = "202007", endDate = "202008")
    # applyHome.getHomeDetail()
    applyHome.getOfficetelList(startDate="202008", endDate="202008")
    applyHome.getOfficetelDetail()
    # applyHome.getNoRankList(startDate="201807", endDate="202008")
    # applyHome.getNoRankDetail()
    for subscription in applyHome.subscriptionList:
        print(subscription)
