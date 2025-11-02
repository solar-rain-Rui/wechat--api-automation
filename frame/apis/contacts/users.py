# frame/api/users.py
from frame.apis.wework import WeWork


class Users(WeWork):
    """成员管理模块"""

    def create(self, data):
        """创建成员"""
        req = {
            "method": "post",
            "url": f"{self.base_url}/user/create?access_token={self.token}",
            "json": data
        }
        print(">>> 创建用户请求体:", data)  # 👈 看看 department 是不是 []
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
