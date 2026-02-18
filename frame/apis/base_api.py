
import requests

from frame.common.config import cf
from frame.common.logger import log
#from frame.utils.log_utils import logger


class BaseApi:
    def __init__(self, token=None):
        self.token = token

    def send_api(self,req):
        """
        对于requests进行二次封装
        :return:接口响应
        """
        # 自动注入 token
        if self.token:
            req.setdefault("headers", {})
            req["headers"]["access_token"] = self.token

        log.info(f"请求接口为：{req['url']}")
        r=requests.request(**req,proxies={"http": None, "https": None})#禁用下代理
        log.info(f"接口响应为：{r.text}")
        return r

