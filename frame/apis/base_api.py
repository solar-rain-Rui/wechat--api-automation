
import requests

from frame.common.config import cf
from frame.common.logger import log
from frame.common.token_get import fetch_token


#from frame.utils.log_utils import logger


class BaseApi:
    def __init__(self, token=None):
        self.token = token
        self.base_url = cf.get("base_url")
    def send_api(self,req):
        """
        对于requests进行二次封装
        :return:接口响应
        """

        log.info(f"请求接口为：{req['url']}")
        r=requests.request(**req,proxies={"http": None, "https": None})#禁用下代理
        res=r.json()
        # ===== token 失效自动处理 =====
        if res.get("errcode") in [40014, 42001]:
            log.warning(" access_token 失效，自动刷新并重试一次")

            #  获取新 token
            new_token = fetch_token()

            #  把新 token 注入请求
            if "params" not in req:
                req["params"] = {}
            req["params"]["access_token"] = new_token

            #  重试一次
            r = requests.request(**req)
        log.info(f"接口响应为：{r.text}")
        return r

