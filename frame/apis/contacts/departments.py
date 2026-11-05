from frame.apis.weixin_base import WeComApi
from frame.common.logger import log


class Departments(WeComApi):
    """
    业务接口信息的具体描述，只关注接口本身，不需要设计业务和断言
    可以在每个接口对应方法中返回接口的响应
    """

    def __init__(self, token=None):
        super().__init__(token)

    def create(self, data):
        """
        创建部门接口
        :return:
        """
        req = {
            "method": "POST",
            "url": f"{self.base_url}/department/create",
            "params": {"access_token": self.token},
            "json": data
        }
        return self.send_api(req)

    def update(self, data):
        """
        更新部门接口
        :return:
        """
        req = {
            "method": "POST",
            "url": f"{self.base_url}/department/update",
            "params": {"access_token": self.token},
            "json": data
        }
        return self.send_api(req)

    def delete(self, depart_id):
        """
        删除部门接口
        :return:
        """
        req = {
            "method": "GET",
            "url": f"{self.base_url}/department/delete",
            "params": {
                "access_token": self.token,
                "id": depart_id
            }
        }
        return self.send_api(req)

    def get(self, params=None):
        """
        查询部门
        :return:
        """
        # 查询参数与 access_token 统一放在 params 中传递
        req_params = {"access_token": self.token}
        if isinstance(params, dict):
            req_params.update(params)
        req = {
            "method": "GET",
            "url": f"{self.base_url}/department/simplelist",
            "params": req_params
        }
        return self.send_api(req)

    def list_all(self):
        return self.send_api({
            "method": "GET",
            "url": f"{self.base_url}/department/simplelist",
            "params": {
                "access_token": self.token
            }
        })
