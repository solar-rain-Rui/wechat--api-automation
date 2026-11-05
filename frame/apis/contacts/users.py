# frame/api/users.py
from frame.apis.weixin_base import WeComApi


class Users(WeComApi):
    """成员管理模块"""

    def create(self, data):
        """创建成员"""
        req = {
            "method": "post",
            "url": f"{self.base_url}/user/create",
            "params": {"access_token": self.token},
            "json": data
        }
        return self.send_api(req)

    def get(self, userid):
        """获取成员"""
        req = {
            "method": "get",
            "url": f"{self.base_url}/user/get",
            "params": {
                "access_token": self.token,
                "userid": userid
            }
        }
        return self.send_api(req)

    def update(self, data):
        """更新成员"""
        req = {
            "method": "post",
            "url": f"{self.base_url}/user/update",
            "params": {"access_token": self.token},
            "json": data
        }
        return self.send_api(req)

    def delete(self, userid):
        """删除成员"""
        req = {
            "method": "get",
            "url": f"{self.base_url}/user/delete",
            "params": {
                "access_token": self.token,
                "userid": userid
            }
        }
        return self.send_api(req)

    def list(self, department_id=1, fetch_child=1):
        """
        获取部门用户列表
        官方必须传 department_id，不存在查全量用户接口
        """
        return self.send_api({
            "method": "GET",
            "url": f"{self.base_url}/user/list",
            "params": {
                "access_token": self.token,
                "department_id": department_id,
                "fetch_child": fetch_child
            }
        })


