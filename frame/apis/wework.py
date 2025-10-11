

import requests

class WeWork:
    """
    企业微信特有的业务逻辑，完成access_token的获取
    """
    def __init__(self):
        self.token=self.get_access_token()

    def get_access_token(self):
        """
        向access_token接口发起请求，获取 access_token的值
        :return:access_token的值
        """
        # 定义登录的凭证
        corp_id = "ww779187ee7c9f7085"
        # 通讯录应用密钥
        corp_secret = "AAR4FC_5E6m4mbvKWepNrLt7qPFdIHXrjrK77sQcNqE"
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
        # 发出请求，获取access_token
        r = requests.request("GET", url)
        # 提取响应体中的access_token值
        token = r.json().get("access_token")
        print(f"获取到的token值为{token}")
        return token