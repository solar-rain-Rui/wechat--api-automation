from frame.apis.base_api import BaseApi

print(">>> LOADING Tags CLASS FROM:", __file__)

import allure
from frame.common.logger import log

class Tags(BaseApi):
    @allure.step("创建标签")
    def create(self, tagname, tagid=None):
        data = {"tagname": tagname}
        if tagid:
            data["tagid"] = tagid
        req = {
            "method": "POST",
            "url": "https://qyapi.weixin.qq.com/cgi-bin/tag/create",
            "params": {"access_token": self.token},
            "json": data
        }
        log.info(f"创建标签请求体: {data}")
        return self.send_api(req)

    @allure.step("更新标签")
    def update(self, tagid, tagname):
        data = {"tagid": tagid, "tagname": tagname}
        req = {
            "method": "POST",
            "url": "https://qyapi.weixin.qq.com/cgi-bin/tag/update",
            "params": {"access_token": self.token},
            "json": data
        }
        return self.send_api(req)

    @allure.step("获取标签信息")
    def get(self, tagid):
        req = {
            "method": "GET",
            "url": "https://qyapi.weixin.qq.com/cgi-bin/tag/get",
            "params": {"access_token": self.token, "tagid": tagid}
        }
        return self.send_api(req)

    @allure.step("删除标签")
    def delete(self, tagid):
        req = {
            "method": "GET",
            "url": "https://qyapi.weixin.qq.com/cgi-bin/tag/delete",
            "params": {"access_token": self.token, "tagid": tagid}
        }
        return self.send_api(req)



    @allure.step("添加标签成员")
    def add_users(self, tagid, userlist=None, partylist=None):
        """
        给标签添加成员或部门
        :param tagid: 标签 ID
        :param userlist: 用户列表，例如 ["user1", "user2"]
        :param partylist: 部门列表，例如 [1,2]
        """
        data = {"tagid": tagid}
        if userlist is not None:
            data["userlist"] = userlist
        if partylist is not None:
            data["partylist"] = partylist

        req = {
            "method": "POST",
            "url": "https://qyapi.weixin.qq.com/cgi-bin/tag/addtagusers",
            "params": {"access_token": self.token},
            "json": data
        }
        return self.send_api(req)

    @allure.step("获取标签成员")
    def get_users(self, tagid):
        """
        获取标签下成员（userlist / partylist）
        :param tagid: 标签 ID
        """
        req = {
            "method": "GET",
            "url": "https://qyapi.weixin.qq.com/cgi-bin/tag/get",
            "params": {"access_token": self.token, "tagid": tagid}
        }
        return self.send_api(req)

    def list(self):
        req = {
            "method": "GET",
            "url": "https://qyapi.weixin.qq.com/cgi-bin/tag/list",
            "params": {
                "access_token": self.token
            }
        }
        return self.send_api(req)