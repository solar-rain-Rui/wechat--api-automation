
import requests

from frame.common.config import cf
from frame.common.logger import log
#from frame.utils.log_utils import logger


class BaseApi:

    def send_api(self,req):
        """
        对于requests进行二次封装
        :return:接口响应
        """
        log.info(f"请求数据为{req}")
        r=requests.request(**req)
        log.info(f"接口响应为{r.text}")
        return r

