import requests

from frame.common.config import cf
from frame.common.logger import log

# 模块级 token 缓存：
# 会话内多个 API 实例（departments/users/tags/message）共享同一个 token；
# token 失效重试时只有第一个实例真正请求 gettoken，
# 其余实例刷新时直接命中缓存，避免对鉴权接口产生重复请求
_token_cache = None


def fetch_token(force=False):
    """
    获取企业微信 access_token
    :param force: True 时强制重新获取（token 失效后的刷新场景）；
                  默认返回缓存值
    """
    global _token_cache
    if _token_cache and not force:
        return _token_cache

    log.info("正在获取 access_token...")

    base_url = cf.get("base_url")
    corpid = cf.get("corpid")["接口自动化测试"]
    corpsecret = cf.get("corpsecret")["contacts"]

    # 注意：该 URL 含 corpsecret，不做日志输出
    url = f"{base_url}/gettoken?corpid={corpid}&corpsecret={corpsecret}"

    r = requests.get(url)
    token = r.json().get("access_token")

    if not token:
        raise RuntimeError("获取 access_token 失败！")

    _token_cache = token
    return token
