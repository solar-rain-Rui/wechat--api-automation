# frame/api/tags.py
import allure
from frame.apis.wework import WeWork
from frame.common.logger import log

class Tags(WeWork):
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
    def update(self, tagid, new_name):
        data = {"tagid": tagid, "tagname": new_name}
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
