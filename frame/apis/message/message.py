"""
企业微信 - 消息发送接口封装

设计原则：
- 继承 BaseApi
- 统一走 send_api
- api 层不写断言
- 与现有 user/tag/department 风格对齐
"""

from frame.apis.base_api import BaseApi
from frame.common.logger import log
from frame.config.settings import MOCK_MESSAGE


class MessageApi(BaseApi):
    """企业微信消息发送接口"""

    SEND_MESSAGE_PATH = "/message/send"

    def send_message(self, data):
        """
        通用发送消息接口

        支持：
        - MOCK_MESSAGE = True  → 本地mock
        - MOCK_MESSAGE = False → 真实请求

        :param data: 请求体
        :return: response
        """

        # ================= mock 分支 =================
        if MOCK_MESSAGE:
            log.info("🚧 MessageApi 走 MOCK 分支")

            # 根据 data 特征判断是哪种场景
            if data.get("touser") == "not_exist_user_999":
                errcode = 60111
            elif not data.get("touser") and not data.get("toparty") and not data.get("totag"):
                errcode = 41003
            elif data.get("content") == "":
                errcode = 41003
            elif "deleted" in str(data.get("touser", "")) or "test_invalid_dept_user" in str(data.get("touser", "")):
                errcode = 60111
            else:
                errcode = 0  # 默认成功

            class MockResponse:
                def __init__(self, errcode):
                    self.status_code = 200
                    self._json = {"errcode": errcode, "errmsg": "ok (mock)"}

                def json(self):
                    return self._json

            return MockResponse(errcode)

        # ================= real 分支 =================
        url = f"{self.base_url}{self.SEND_MESSAGE_PATH}?access_token={self.token}"

        req = {
            "method": "POST",
            "url": url,
            "json": data,
        }

        return self.send_api(req)
