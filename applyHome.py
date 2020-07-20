import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from models import *
import datetime
import math
class ApplyHome(object):
    def __init__(self):
        self.listUrl = "https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancListView.do"
        self.listParams = {
            "beginPd" : "",
            "endPd" : "",
            "pageIndex" : 1,
            "pageSelAt" : "Y",
            "gvPgmId" : "AIA01M01"
        }
        self.homeList = []
        self.detailUrl = "https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancDetail.do"
        self.detailParams = {
            "houseManageNo" : "",
            "pblancNo" : "",
            "gvPgmId" : "AIA01M01"
        }
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
        totalCount = bsObject.body.find_all("p", class_ = "total_txt")[0].find("b").get_text()
        totalCount = int(totalCount)
        targetPageNumber = int(math.ceil(totalCount/10.0))
        for page in range(targetPageNumber):
            self.listParams["pageIndex"] = page +1
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
                companyName = target.find_all("td")[4].get_text()
                home = Home(pbNo = pbNo, homeNo = homeNo, homeName = homeName, subscriptionType= subscriptionType, supplyType = supplyType,companyName = companyName)
                self.homeList.append(home)
        print(self.homeList)  # 웹 문서 전체가 출력됩니다.

    def getListUrl(self,type):
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
        parts = parts._replace(query = urlencode(self.listParams))
        new_url = urlunparse(parts)
        return new_url
    def getHomeDetail(self):
        for home in self.homeList:
            targetUrl = self.getDetailUrl(homeNo = home.homeNo, pbNo = home.pbNo)
            req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read()
            bsObject = BeautifulSoup(html, "html.parser")

            # 첫번째 테이블 로직

            try:
                addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[
                    1].get_text()
            except IndexError as E:
                print("에러!!!!!!!!!")
                continue
            addressProvinceCode = addressText.split(" ")[0].replace(" ","")
            addressDetailFirstKor = addressText.split(" ")[1].strip()
            addressDetailSecondKor = " ".join(addressText.split(" ")[2:]).strip()
            totalSupply = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[1].find_all("td")[1].get_text().strip()
            totalSupply = totalSupply[:-2]
            contact = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[3].find_all("td")[1].get_text().strip()
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
                    dateSpecialSupplyNear = dateTable.find_all("tr")[2].find_all("td")[1].get_text().strip().split("~")[0]
                    dateSpecialSupplyOther = dateTable.find_all("tr")[2].find_all("td")[2].get_text().strip().split("~")[0]
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


                dateFirstNear = datetime.datetime.strptime(dateFirstNear, "%Y-%m-%d")
                dateFirstOther = datetime.datetime.strptime(dateFirstOther, "%Y-%m-%d")
                dateSecondNear = datetime.datetime.strptime(dateSecondNear, "%Y-%m-%d")
                dateSecondOther = datetime.datetime.strptime(dateSecondOther, "%Y-%m-%d")
                print("고지일",dateAnnounce,"입니다.")
                dateAnnounce = datetime.datetime.strptime(dateAnnounce, "%Y-%m-%d")
                print("고지일", dateContract, "입니다.")
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
            if hasSpecialSupply:
                print("특별공급 해당", dateSpecialSupplyNear)
                print("특별공급 기타", dateSpecialSupplyOther)
            print("1순위 해당", dateFirstNear)
            print("1순위 기타",dateFirstOther)
            print("2순위 해당",dateSecondNear)
            print("2순위 기타",dateSecondOther)
            print("당첨자 발표일",dateAnnounce)
            print("계약일", dateContract)

            # 공급 관련
            supplyTable = bsObject.body.find_all("table")[2]
            # 마지막 값은 Total이라 따로 관리한다.
            rowList = supplyTable.find("tbody").find_all("tr")[:-1]
            homeTypeList = []
            for row in rowList:
                tdList =  row.find_all("td")
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
                homeType = Type(
                    homeTypeCode = homeTypeCode,
                    title = homeTypeName,
                    size = homeTypeSize,
                    generalSupply = int(homeTypeGeneralSupply),
                    specialSupply = int(homeTypeSpecialSupply),
                    totalSupply = int(homeTypeTotalSupply)
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
            if bsObject.body.find("dl", class_= "pop_btn_txt") != None:
                try:
                    documentLink = bsObject.body.find("dl", class_="pop_btn_txt").find("dd").find("a").get("href").strip()
                    documentLink = "https://www.applyhome.co.kr" + documentLink
                except AttributeError as e:
                    documentLink = None

            subscription = Subscription(
                houseManageNo = home.homeNo,
                title = home.homeName,
                addressProvinceCode = addressProvinceCode,
                 addressDetailFirstKor = addressDetailFirstKor,
                 addressDetailSecondKor = addressDetailSecondKor,
                 buildingType = "아파트",
                supplyType = home.supplyType,
                 subscriptionType = home.subType,
                 noRank = False,
                 noRankDate = None,
                 hasSpecialSupply = hasSpecialSupply,
                 dateSpecialSupplyNear = dateSpecialSupplyNear,
                 dateSpecialSupplyOther = dateSpecialSupplyOther,
                 dateFirstNear = dateFirstNear,
                 dateFirstOther = dateFirstOther,
                 dateSecondNear = dateSecondNear,
                 dateSecondOther = dateSecondOther,
                 dateNotice = noticeDate,
                 officialLink = targetUrl,
                 documentLink = documentLink,
                dateAnnounce = dateAnnounce,
                dateContract= dateContract,
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
        self.detailParams["pblancNo"]= pbNo
        parts = urlparse(self.detailUrl)
        parts = parts._replace(query=urlencode(self.detailParams))
        new_url = urlunparse(parts)
        return new_url
    def getOfficetelDetailUrl(self,homeNo, pbNo,houseSecd):
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
    def getNoRankDetailUrl(self,homeNo, pbNo,houseSecd):
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
            targetUrl =  self.getListUrl(type=2)
            html = urlopen(targetUrl)
            bsObject = BeautifulSoup(html, "html.parser")
            targetList = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")
            print(targetList)
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

                home = Home(pbNo=pbNo, homeNo=homeNo, homeName=homeName, supplyType =supplyType,buildingType=buildingType,houseSecd=houseSecd)
                self.homeList.append(home)
        print(self.homeList)  # 웹 문서 전체가 출력됩니다.
    def getOfficetelDetail(self):
        print("officetel/기타 주택 개수")
        print(len(self.homeList))
        for home in self.homeList:
            print("======================================")
            print("주택 데이터 처리 시작")
            print(home.homeName)

            targetUrl = self.getOfficetelDetailUrl(homeNo = home.homeNo, pbNo = home.pbNo, houseSecd= home.houseSecd)
            req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read()
            bsObject = BeautifulSoup(html, "html.parser")
            print(html)

            # 첫번째 테이블 로직
            try:
                addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[
                    1].get_text()
            except IndexError as E:
                print("에러!!!!!!!!!")
                continue
            addressProvinceCode = addressText.split(" ")[0].replace(" ","")
            if len(addressText.split(" ")) > 1:
                addressDetailFirstKor = addressText.split(" ")[1].strip()
            else :
                addressDetailFirstKor = " "
            if len(addressText.split(" ")) > 2:
                addressDetailSecondKor = " ".join(addressText.split(" ")[2:]).strip()
            else:
                addressDetailSecondKor = " "
            totalSupply = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[1].find_all("td")[1].get_text().strip()
            totalSupply = totalSupply[:-2]
            contact = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[2].find_all("td")[1].get_text().strip()
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
               # 슬프지만 지금은 일단 가장 후순위 정보로 놔둠 ㅜㅜ 수정해야 한다.
               dateSecondOther = dateTable.find_all("tr")[1].find("td").get_text().strip().split("~")[0].strip()
               dateAnnounce = dateTable.find_all("tr")[2].find("td").get_text().split(" ")[0].split("~")[0].split("(")[0].strip()
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

            print("2순위 기타(접수 시작일)",dateSecondOther)
            print("당첨자 발표일",dateAnnounce)
            print("계약일", dateContract)

            # 공급 관련
            supplyTable = bsObject.body.find_all("table")[2]
            rowList = supplyTable.find("tbody").find_all("tr")
            homeTypeList = []
            for row in rowList:
                tdList =  row.find_all("td")
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
                homeType = Type(
                    homeTypeCode = homeTypeCode,
                    title = homeTypeName,
                    size = homeTypeSize,
                    generalSupply = int(homeTypeTotalSupply),
                    specialSupply = int(0),
                    totalSupply = int(homeTypeTotalSupply)
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
            if bsObject.body.find("dl", class_= "pop_btn_txt") != None:
                try:
                    documentLink = bsObject.body.find("dl", class_="pop_btn_txt").find("dd").find("a").get("href").strip()
                    documentLink = "https://www.applyhome.co.kr" + documentLink
                except AttributeError as e:
                    documentLink = None

            subscription = Subscription(
                houseManageNo = home.homeNo,
                title = home.homeName,
                addressProvinceCode = addressProvinceCode,
                 addressDetailFirstKor = addressDetailFirstKor,
                 addressDetailSecondKor = addressDetailSecondKor,
                 buildingType = home.buildingType,
                supplyType = home.supplyType,
                 subscriptionType = home.subType,
                 noRank = False,
                 noRankDate = None,
                 hasSpecialSupply = hasSpecialSupply,
                 dateSpecialSupplyNear = dateSpecialSupplyNear,
                 dateSpecialSupplyOther = dateSpecialSupplyOther,
                 dateFirstNear = dateFirstNear,
                 dateFirstOther = dateFirstOther,
                 dateSecondNear = dateSecondNear,
                 dateSecondOther = dateSecondOther,
                 dateNotice = noticeDate,
                 officialLink = targetUrl,
                 documentLink = documentLink,
                dateAnnounce = dateAnnounce,
                dateContract= dateContract,
                noRankNotSpecified= False
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
            targetUrl =  self.getListUrl(type=3)
            html = urlopen(targetUrl)
            bsObject = BeautifulSoup(html, "html.parser")
            targetList = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")
            print(targetList)
            for target in targetList:
                pbNo = target.get("data-pbno")
                homeNo = target.get("data-hmno")
                homeName = target.get("data-honm")
                houseSecd = target.get("data-hsecd")
                supplyType = "분양주택"
                home = Home(pbNo=pbNo, homeNo=homeNo, homeName=homeName, supplyType =supplyType,houseSecd=houseSecd)
                self.homeList.append(home)
        print(self.homeList)  # 웹 문서 전체가 출력됩니다.
    def getNoRankDetail(self):
        print("무가점 개수")
        print(len(self.homeList))
        for home in self.homeList:
            print("======================================")
            print("주택 데이터 처리 시작")
            print(home.homeName)

            targetUrl = self.getNoRankDetailUrl(homeNo = home.homeNo, pbNo = home.pbNo, houseSecd= home.houseSecd)
            req = urllib.request.Request(targetUrl, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read()
            bsObject = BeautifulSoup(html, "html.parser")
            print(bsObject.body.find_all("table"))
            # 첫번째 테이블 로직
            try:
                addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[1].get_text()
            except IndexError as E:
                print("에러!!!!!!!!!")
                continue

            addressProvinceCode = addressText.split(" ")[0].replace(" ","")
            if len(addressText.split(" ")) > 1:
                addressDetailFirstKor = addressText.split(" ")[1].strip()
            else :
                addressDetailFirstKor = " "
            if len(addressText.split(" ")) > 2:
                addressDetailSecondKor = " ".join(addressText.split(" ")[2:]).strip()
            else:
                addressDetailSecondKor = " "
            totalSupply = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[1].find_all("td")[1].get_text().strip()
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
               dateAnnounce = dateTable.find_all("tr")[2].find("td").get_text().split(" ")[0].split("~")[0].split("(")[0].strip()
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

            print("2순위 기타(접수 시작일)",dateSecondOther)
            print("당첨자 발표일",dateAnnounce)
            print("계약일", dateContract)

            # 공급 관련
            supplyTable = bsObject.body.find_all("table")[2]
            rowList = supplyTable.find("tbody").find_all("tr")
            homeTypeList = []
            for row in rowList:
                tdList =  row.find_all("td")
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
                homeTypeCode = home.homeNo + "_"+ homeTypeName
                homeType = Type(
                    homeTypeCode = homeTypeCode,
                    title = homeTypeName,
                    size = homeTypeSize,
                    generalSupply = int(homeTypeTotalSupply),
                    specialSupply = int(0),
                    totalSupply = int(homeTypeTotalSupply)
                )
                homeTypeList.append(homeType)

            # 비우면 미동작해서 0으로 채움
            for index, homeType in enumerate(homeTypeList):
                homeType.setTotalPrice(0)
            # 모집 공고문 찾기
            documentLink = None
            if bsObject.body.find("dl", class_= "pop_btn_txt") != None:
                try:
                    documentLink = bsObject.body.find("dl", class_="pop_btn_txt").find("dd").find("a").get("href").strip()
                    documentLink = "https://www.applyhome.co.kr" + documentLink
                except AttributeError as e:
                    documentLink = None

            subscription = Subscription(
                houseManageNo = home.homeNo,
                title = home.homeName,
                addressProvinceCode = addressProvinceCode,
                 addressDetailFirstKor = addressDetailFirstKor,
                 addressDetailSecondKor = addressDetailSecondKor,
                 buildingType = home.buildingType,
                supplyType = home.supplyType,
                 subscriptionType = home.subType,
                 noRank = True,
                 noRankDate = None,
                 hasSpecialSupply = hasSpecialSupply,
                 dateSpecialSupplyNear = dateSpecialSupplyNear,
                 dateSpecialSupplyOther = dateSpecialSupplyOther,
                 dateFirstNear = dateFirstNear,
                 dateFirstOther = dateFirstOther,
                 dateSecondNear = dateSecondNear,
                 dateSecondOther = dateSecondOther,
                 dateNotice = noticeDate,
                 officialLink = targetUrl,
                 documentLink = documentLink,
                dateAnnounce = dateAnnounce,
                dateContract= dateContract,
                noRankNotSpecified = noRankNotSpecified
            )
            subscription.addTypeList(homeTypeList)
            self.subscriptionList.append(subscription)



class Home(object):
    def __init__(self,pbNo,homeNo, homeName,supplyType, buildingType = "아파트", subscriptionType = "",companyName= "",houseSecd = ""):
        self.pbNo = pbNo
        self.homeNo = homeNo
        self.homeName = homeName
        self.supplyType = supplyType
        self.subType = subscriptionType
        self.companyName = companyName
        self.houseSecd = houseSecd
        self.buildingType = buildingType


if __name__ == "__main__":
    applyHome = ApplyHome()
    # applyHome.getHomeList(startDate = "202007", endDate = "202008")
    # applyHome.getHomeDetail()
    applyHome.getOfficetelList(startDate="201807", endDate="202008")
    applyHome.getOfficetelDetail()
    # applyHome.getNoRankList(startDate="201807", endDate="202008")
    # applyHome.getNoRankDetail()
    for subscription in applyHome.subscriptionList:
        print(subscription)
