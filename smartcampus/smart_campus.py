import json
import requests
from bs4 import BeautifulSoup
from smartcampus.redis_model import RedisModel


class SmartCampus:

    root_url = "http://ids.wbu.edu.cn/authserver/login?service=http://my.wbu.edu.cn/index.portal"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)" +
                      " Chrome/58.0.3029.110 Safari/537.36",
        "host": "ids.wbu.edu.cn",
        "Referer": "http://ids.wbu.edu.cn/authserver/login?service=http://my.wbu.edu.cn/index.portal",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://ids.wbu.edu.cn",
        "Content-Length": "132",
    }
    headers1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                      "Chrome/58.0.3029.110 Safari/537.36",
        "host": "jw.wbu.edu.cn",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
    }
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)" +
                      " Chrome/58.0.3029.110 Safari/537.36",
        "host": "ids.wbu.edu.cn",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
    }

    headers3 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                      "Chrome/58.0.3029.110 Safari/537.36",
        "host": "jw.wbu.edu.cn",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
    }

    headers4 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)" +
                      " Chrome/58.0.3029.110 Safari/537.36",
        "host": "jw.wbu.edu.cn",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://jw.wbu.edu.cn",
    }

    headers5 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)" +
                      " Chrome/58.0.3029.110 Safari/537.36",
        "host": "my.wbu.edu.cn",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, stu_id, stu_pwd):
        self.stu_id = stu_id
        self.stu_pwd = stu_pwd
        self.ids = requests.session()
        self.my = requests.session()
        self.jw = requests.session()

    # 查看redis中是否有stu_id对应的session 如果没有重新登陆账号
    def login_in(self):
        session = RedisModel.get_record(self.stu_id)
        if session is None:
            self.login()
        else:
            session = eval(session)
            self.ids.cookies.set("JSESSIONID", session["ids"])
            self.jw.cookies.set("JSESSIONID", session["jw"])
            self.my.cookies.set("JSESSIONID", session["my"])

    # 登陆教务系统 获取session 并且储存在redis中
    def login(self):
        data = {
            "username": self.stu_id,
            "password": self.stu_pwd,
            "_eventId": "submit",
            "rmShown": 1,
        }
        r = self.ids.get(self.root_url)
        soup = BeautifulSoup(r.text, "html.parser")
        s = soup.select("input")
        data["execution"] = s[3]["value"]
        data["lt"] = s[2]["value"]
        self.ids.post(url="http://ids.wbu.edu.cn/authserver/login?", data=data,
                          headers=self.headers, allow_redirects=False)
        # 登陆信息门户
        k = self.ids.get("http://ids.wbu.edu.cn/authserver/login?service=http://my.wbu.edu.cn/index.portal",
                         headers=self.headers2, allow_redirects=False)
        # 获取信息门户的location
        my_location = k.headers["Location"]
        self.my.get(my_location)
        # 登陆教务系统
        m = self.ids.get(url="http://ids.wbu.edu.cn/authserver/login?service=http://jw.wbu.edu.cn/jsxsd/caslogin.jsp",
                         headers=self.headers2, allow_redirects=False)
        jw_location = m.headers["Location"]
        # 获取教务系统的location
        self.jw.get(url=jw_location, headers=self.headers3)
        session = {
            "ids": self.ids.cookies["JSESSIONID"],
            "my": self.my.cookies["JSESSIONID"],
            "jw": self.jw.cookies["JSESSIONID"],
        }
        RedisModel.add_record(self.stu_id, session)

    # 爬取学生最基本的信息
    def get_stu_info(self):
        self.login_in()
        p = self.my.get(url="http://my.wbu.edu.cn/pnull.portal?.pmn=view&action=showItem&.ia=false" +
                            "&.pen=pe751&itemId=239&childId=241&page=1", headers=self.headers5)
        p.encoding = "utf-8"
        soup = BeautifulSoup(p.text, "html.parser")
        s = soup.select("td")
        info = {
            "std_id": self.stu_id,
            "name": s[2].text.replace("\r", "").replace("\n", "").replace("\t", ""),
            "college": s[9].text.replace("\r", "").replace("\n", "").replace("\t", ""),
            "class": s[13].text.replace("\r", "").replace("\n", "").replace("\t", "")
        }
        print(info)

    # 爬取校园卡信息
    def get_stu_card(self):
        self.login_in()
        p = self.my.get(url="http://my.wbu.edu.cn/pnull.portal?pmn=view&action=showItem&.ia=false&.pen=pe575" +
                            "&itemId=341&childId=342&page=1")
        p.encoding = "utf-8"
        soup = BeautifulSoup(p.text, "html.parser")
        s = soup.select("td")
        info = {
            "std_id": self.stu_id,
            "card_number": s[1].text.replace("\r", "").replace("\n", "").replace("\t", ""),
            "card_state": s[2].text.replace("\r", "").replace("\n", "").replace("\t", ""),
            "card_balance": s[3].text.replace("\r", "").replace("\n", "").replace("\t", ""),
        }
        print(info)


a = SmartCampus(160577095, "dw921985398")
a.get_stu_info()
a.get_stu_card()
b = SmartCampus(160577061, "175798")
b.get_stu_info()
b.get_stu_card()