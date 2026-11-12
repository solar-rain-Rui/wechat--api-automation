import re

import requests

from frame.common.config import cf
from frame.common.logger import log


def _mask_url(url):
    """日志脱敏：隐藏 URL 中的 access_token 参数值，避免敏感信息进入日志"""
    return re.sub(r"(access_token=)[^&]+", r"\1***", url)


class BaseApi:
    """
    通用 HTTP 请求基类。

    职责边界：
    - 只负责发送 HTTP 请求、记录请求/响应日志
    - 不感知任何业务认证细节（token 如何获取、何时失效由子类决定）
    - 不假设响应一定是 JSON，直接返回原始 Response 对象，
      由调用方按需解析（JSON / HTML / 二进制均可）
    """

    def __init__(self, token=None):
        self.token = token
        self.base_url = cf.get("base_url")

    def send_api(self, req):
        """
        对于 requests 进行二次封装
        :param req: 与 requests.request 参数一致的字典，
                    如 {"method": "POST", "url": ..., "params": ..., "json": ...}
        :return: requests.Response 原始响应对象
        """
        log.info(f"请求接口为：{_mask_url(req['url'])}")
        r = requests.request(**req, proxies={"http": None, "https": None})  # 禁用本地代理
        log.info(f"接口响应为：{r.text}")
        return r
