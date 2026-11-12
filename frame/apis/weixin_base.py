"""
企业微信专属请求基类。

职责边界：
- 继承 BaseApi，复用其通用 HTTP 发送能力（日志、代理配置等）
- 仅补充企业微信的 access_token 失效判断、刷新与自动重试逻辑
- BaseApi 对企业微信零感知，两者通过「一层简单继承」组合，
  不引入插件系统或认证提供者体系

失效重试规则（防止请求风暴）：
- 仅当响应 JSON 中的 errcode 属于 TOKEN_EXPIRED_CODES 才判定为 token 失效
- 失效后强制刷新一次 token、重试一次请求，无论重试结果如何都不再重试
"""

import copy

from frame.apis.base_api import BaseApi
from frame.common.logger import log
from frame.common.token_get import fetch_token


class WeComApi(BaseApi):
    # 企业微信中表示 access_token 不合法/已过期的错误码
    TOKEN_EXPIRED_CODES = {40014, 42001}

    def send_api(self, req):
        """
        发送企业微信请求：
        1. 走通用层 BaseApi.send_api 发出请求
        2. 响应表示 token 失效时，刷新 token 并重试一次
        :param req: 与 requests.request 参数一致的字典，
                    token 统一放在 req["params"]["access_token"] 中传递
        """
        r = super().send_api(req)

        if not self._is_token_expired(r):
            return r

        log.warning("access_token 失效，自动刷新并重试一次")

        # 刷新并回写实例：后续所有请求直接使用新 token，不再重复触发刷新
        new_token = fetch_token(force=True)
        self.token = new_token

        # 深拷贝重试请求，避免原地修改调用方传入的参数字典；
        # params 为 None 或缺失时自动补齐为空字典
        retry_req = copy.deepcopy(req)
        retry_req["params"] = dict(req.get("params") or {})
        retry_req["params"]["access_token"] = new_token

        # 重试完全复用通用发送逻辑，代理配置、日志行为与原请求一致
        return super().send_api(retry_req)

    def _is_token_expired(self, response):
        """
        判断响应是否表示 token 失效。
        响应不是 JSON（或 JSON 不是字典）时无法提取 errcode，
        视为未失效，原样返回响应，由调用方自行处理。
        """
        try:
            res_json = response.json()
        except ValueError:
            return False
        return isinstance(res_json, dict) and res_json.get("errcode") in self.TOKEN_EXPIRED_CODES
