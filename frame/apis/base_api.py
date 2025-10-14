
import requests
class BaseApi:

    def send_api(self,req):
        """
        对于requests进行二次封装
        :return:接口响应
        """

        r=requests.request(**req)
        return r

