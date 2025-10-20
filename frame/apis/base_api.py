
import requests

from frame.utils.log_utils import logger


class BaseApi:

    def send_api(self,req):
        """
        对于requests进行二次封装
        :return:接口响应
        """
        logger.info(f"请求数据为{req}")
        r=requests.request(**req)
        logger.info(f"接口响应为{r.text}")
        return r

