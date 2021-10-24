import time
import hmac
import hashlib
import base64
import urllib.parse
import io
from pyzbar import pyzbar
from PIL import Image
import requests, json  # 导入依赖库
import datetime


def timecheck():
    return (int(datetime.datetime.now().strftime('%M')) < 35 and int(datetime.datetime.now().strftime('%M')) >29) and int(datetime.datetime.now().strftime('%H')) % 6 ==0
    
# based on https://github.com/TechXueXi/TechXueXi/issues/108 (thanks to mudapi)
def decode_img(data):
    img_b64decode = base64.b64decode(data[data.index(';base64,')+8:])
    decoded = pyzbar.decode(Image.open(io.BytesIO(img_b64decode)))
    return decoded[0].data.decode("utf-8")


class DingDingHandler:
    def __init__(self, token, secret):
        self.token = token
        self.secret = secret

    def get_url(self):
        timestamp = round(time.time() * 1000)
        secret_enc = self.secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        # 完整的url
        api_url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(
            self.token, timestamp, sign
        )
        print("钉钉机器人url: ", api_url)
        return api_url

    def ddimgsend(self, img_data, retry=0):

        # data:image/png;base64,iVBORw0KGgoA...
        self.ddlinksend(img_data, title=f"学习吧{'-重试：'+str(retry) if retry>0 else ''}")
        self.ddtextsend(decode_img(img_data))

    def ddlinksend(self, link, text='学习强国', title='学习吧'):
        headers = {"Content-Type": "application/json"}  # 定义数据类型
        data = {
            "msgtype": "link",
            "link": {
                "text": text,
                "title": title,  #f"学习吧{'-重试：' + str(retry) if retry > 0 else ''}",
                "messageUrl": link,
            },
        }
        if timecheck():
            print("过滤通知"+res.text)
            return
        else:
            res = requests.post(self.get_url(), data=json.dumps(data), headers=headers)  # 发送post请求
            print(res.text)

    def ddtextsend(self, text):
        data={}
        headers = {"Content-Type": "application/json"}  # 定义数据类型
        if text.startswith('dtxuexi://appclient/'):
            data = {
                "msgtype": "link",
                "link": {
                    "text": "请点击",
                    "title": "跳转登陆",
                    "messageUrl": text,
                },
            }
        else:
            data = {
                "msgtype": "text",
                "text": {

                    "content": text,
                },
            }
        if "新用户" in text and text.startswith('dtxuexi://appclient/') == False:
            return
        if "总计用时" in text and text.startswith('dtxuexi://appclient/') == False:
            return
        res = requests.post(self.get_url(), data=json.dumps(data), headers=headers)  # 发送post请求
        print(res.text)
