from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from models import *
import datetime
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
    def getHomeList(self, startDate, endDate):
        self.listParams["beginPd"] = startDate
        self.listParams["endPd"] = endDate
        targetUrl = self.getListUrl()
        html = urlopen(targetUrl)
        bsObject = BeautifulSoup(html, "html.parser")
        totalCount = bsObject.body.find_all("p", class_ = "total_txt")[0].find("b").get_text()
        totalCount = int(totalCount)
        targetList = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")
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

    def getListUrl(self):
        parts = urlparse(self.listUrl)
        parts = parts._replace(query = urlencode(self.listParams))
        new_url = urlunparse(parts)
        return new_url
    def getHomeDetail(self):
        for home in self.homeList:
            targetUrl = self.getDetailUrl(homeNo = home.homeNo, pbNo = home.pbNo)
            html = urlopen(targetUrl)
            bsObject = BeautifulSoup(html, "html.parser")

            # 첫번째 테이블 로직
            addressText = bsObject.body.find_all("table")[0].find("tbody").find_all("tr")[0].find_all("td")[1].get_text()
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

            # 청약 일정 관련
            dateTable = bsObject.body.find_all("table")[1]
            noticeDate = dateTable.find_all("tr")[0].find("td").get_text().strip()
            noticeDate = noticeDate.split(" ")[0]
            noticeDate = datetime.datetime.strptime(noticeDate, "%Y-%m-%d")
            hasSpecialSupply = False
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
                documentLink = bsObject.body.find("dl", class_="pop_btn_txt").find("dd").find("a").get("href").strip()
                documentLink = "https://www.applyhome.co.kr" + documentLink

            print("청약 이름 ", home.homeName)
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
                dateContract= dateContract
            )
            subscription.addTypeList(homeTypeList)
            self.subscriptionList.append(subscription)


    def getDetailUrl(self, homeNo, pbNo):
        self.detailParams["houseManageNo"] = homeNo
        self.detailParams["pblancNo"]= pbNo
        parts = urlparse(self.detailUrl)
        parts = parts._replace(query=urlencode(self.detailParams))
        new_url = urlunparse(parts)
        return new_url

class Home(object):
    def __init__(self,pbNo,homeNo, homeName,supplyType, subscriptionType,companyName):
        self.pbNo = pbNo
        self.homeNo = homeNo
        self.homeName = homeName
        self.supplyType = supplyType
        self.subType = subscriptionType
        self.companyName = companyName



if __name__ == "__main__":
    applyHome = ApplyHome()
    applyHome.getHomeList(startDate = "202007", endDate = "202008")
    applyHome.getHomeDetail()
    for subscription in applyHome.subscriptionList:
        print(subscription)
        print("청약!!!!!!!!!!!!!!!!!!!!!!!!!!!!@@@@@@@@")