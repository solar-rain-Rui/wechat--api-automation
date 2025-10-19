from frame.apis.wework import WeWork
import requests

class Departments(WeWork):
    """
    业务接口信息的具体描述，只关注接口本身，不需要设计业务和断言
    可以在每个接口对应方法中返回接口的响应
    """
    def create(self,data):
        """
        创建部门接口
        :return:
        """
        #create_url = f"https://qyapi.weixin.qq.com/cgi-bin/department/create?access_token={self.token}"#token?
        create_url = f"{self.base_url}/department/create?access_token={self.token}"#token?

        #r=requests.request("POST", create_url, json=data)
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
        #update_url=f"https://qyapi.weixin.qq.com/cgi-bin/department/update?access_token={self.token}"

        update_url=f"{self.base_url}/department/update?access_token={self.token}"
        #r=requests.request("POST", update_url, json=data)
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
        #delete_url=f"https://qyapi.weixin.qq.com/cgi-bin/department/delete?access_token={self.token}&id={depart_id}"
        delete_url=f"{self.base_url}/department/delete?access_token={self.token}&id={depart_id}"

        #r=requests.request("GET", delete_url)
        req={
            "method": "GET",
            "url": delete_url
        }
        r=self.send_api(req)
        return r
    def get(self):
        """
        查询部门id
        :return:
        """
        #get_url = f"https://qyapi.weixin.qq.com/cgi-bin/department/simplelist?access_token={self.token}"
        get_url = f"{self.base_url}/department/simplelist?access_token={self.token}"

        #r=requests.request("GET", get_url)
        req={
            "method": "GET",
            "url": get_url
        }
        r=self.send_api(req)
        return r


