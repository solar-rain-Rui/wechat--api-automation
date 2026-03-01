import requests

from frame.common.config import cf

from frame.common.logger import log


def fetch_token():
    """向企业微信获取新的 access_token"""
    log.info(" 正在重新获取 access_token...")

    base_url = cf.get("base_url")
    corpid = cf.get("corpid")["接口自动化测试"]
    corpsecret = cf.get("corpsecret")["contacts"]

    url = f"{base_url}/gettoken?corpid={corpid}&corpsecret={corpsecret}"

    r=requests.get(url)
    token = r.json().get("access_token")

    if not token:
        raise RuntimeError("获取 access_token 失败！")

    return token