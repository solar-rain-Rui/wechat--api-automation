
from frame.apis.base_api import BaseApi
import requests
from frame.common.logger import log



class Departments(BaseApi):
    """
    业务接口信息的具体描述，只关注接口本身，不需要设计业务和断言
    可以在每个接口对应方法中返回接口的响应
    """

    def __init__(self, token=None):
        super().__init__(token)

    def create(self,data):
        """
        创建部门接口
        :return:
        """
        log.info(f"当前token为: {self.token}")
        create_url = f"{self.base_url}/department/create?access_token={self.token}"

        req={
            "method": "POST",
            "url": create_url,
            "json": data
        }
        r=self.send_api(req)

        return r

    def update(self,data):
        """
        更新部门接口
        :return:
        """
        update_url=f"{self.base_url}/department/update?access_token={self.token}"
        req={
            "method": "POST",
            "url": update_url,
            "json": data
        }
        r=self.send_api(req)
        return r

    def delete(self,depart_id):
        """
        删除部门接口
        :return:
        """
        delete_url=f"{self.base_url}/department/delete?access_token={self.token}&id={depart_id}"
        req={
            "method": "GET",
            "url": delete_url
        }
        r=self.send_api(req)
        return r
    def get(self,params=None):
        """
        查询部门id
        :return:
        """
        get_url = f"{self.base_url}/department/simplelist?access_token={self.token}"
        req={
            "method": "GET",
            "url": get_url,
            "params": params
        }
        r=self.send_api(req)
        return r

    def list_all(self):
        return self.send_api({
            "method": "GET",
            "url": "https://qyapi.weixin.qq.com/cgi-bin/department/simplelist",
            "params": {
                "access_token": self.token
            }
        })



