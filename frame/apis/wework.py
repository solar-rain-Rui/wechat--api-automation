

import requests


from frame.apis.base_api import BaseApi
#from frame.utils.utils import Utils
from frame.common.config import cf
class WeWork(BaseApi):
    """
    企业微信特有的业务逻辑，完成access_token的获取
    """
    def __init__(self,token=None):
        """
        构造方法：
        - token：如果传入，直接使用
        - 如果没有传入，则自动调用 get_access_token() 获取
        """
        # 从配置文件读取 base_url
        self.base_url = cf.get("base_url")
        # 获取或使用传入的 token
        if token:
            self.token = token
        else:
            self.token = self.get_access_token()

    def get_access_token(self):
        """
        向access_token接口发起请求，获取 access_token的值
        :return:access_token的值
        """
        #获取yaml文件中的配置数据:corpid,base_url,corpsecret
        self.corpid=cf.get("corpid")["接口自动化测试"]
        self.base_url=cf.get("base_url")
        self.corpsecret=cf.get("corpsecret")["contacts"]
        url = f"{self.base_url}/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"

        # # 发出请求，获取access_token
        # r = requests.request("GET", url)
        req={
            "method":"GET",
            "url":url

        }
        #调用自己封装的发请求的方法
        r=self.send_api(req)
        # 提取响应体中的access_token值
        token = r.json().get("access_token")
        print(f"获取到的token值为{token}")
        return token

    # def get_config(self):
    #     """
    #     获取yaml文件中的配置数据
    #     :return:
    #     """
    #     #读取yaml文件
    #     yaml_data=Utils.get_yaml_data("frame/config/test_env.yaml")
    #     #获取需要的值
    #     self.base_url=yaml_data.get("base_url")
    #     print(f"获取到的base_url为: {self.base_url}")
    #     self.corpid=yaml_data.get("corpid").get("接口自动化测试")
    #     print(f"获取到的corpid为: {self.corpid}")
    #     self.corpsecret=yaml_data.get("corpsecret").get("contacts")
    #     print(f"获取到的corpsecret为: {self.corpsecret}")