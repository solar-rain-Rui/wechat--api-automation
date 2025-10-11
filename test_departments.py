

import requests
import pytest
class TestDeparments:
    """
    部门管理接口自动化测试脚本
    """

    def setup_class(self):
        #定义登录的凭证
        corp_id = "ww779187ee7c9f7085"
        #通讯录应用密钥
        corp_secret = "AAR4FC_5E6m4mbvKWepNrLt7qPFdIHXrjrK77sQcNqE"
        url=f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
        #发出请求，获取access_token
        r=requests.request("GET", url)
        #提取响应体中的access_token值
        self.token=r.json().get("access_token")
        print(f"获取到的token值为{self.token}")

    def test_create_department(self):
        """
        创建部门单接口测试(冒烟用例)
        """
        url=f"https://qyapi.weixin.qq.com/cgi-bin/department/create?access_token={self.token}"
        data={
            "name": "技术部",
            "name_en": "JISHU1",
            "parentid": 1,
            "order": 1,
            "id": 2
            }
        r=requests.request(method="POST", url=url, json=data)
        print(r.text)
        #断言接口状态
        assert r.status_code == 200
        #断言业务逻辑
        assert r.json().get("errcode") == 0

    #参数化完成单接口校验
    @pytest.mark.parametrize(
        "name,name_en,parentid,order,depart_id,expect",
        [
            [" ","JISHU3",1,5,6,60001],
            ["研发部1t6yujk9osjhynnj890lkmbg54321","YANFA",1,4,5,0]
        ]
    )
    def test_create_departments_by_params(self,name,name_en,parentid,order,depart_id,expect):
        url = f"https://qyapi.weixin.qq.com/cgi-bin/department/create?access_token={self.token}"
        data = {
            "name": name,
            "name_en": name_en,
            "parentid": parentid,
            "order": order,
            "id": depart_id
        }
        r=requests.request("POST", url, json=data)
        print(r.text)
        #断言
        assert r.status_code == 200
        assert r.json().get("errcode") == expect

    #验证接口的业务逻辑
    def test_creat_departments_exist(self):
        """
        验证接口业务逻辑
        创建部门前，已存在部门，需要先删除，再创建，可以创建成功
        """
        #准备一个已存在的部门
        depart_id=210
        create_url=f"https://qyapi.weixin.qq.com/cgi-bin/department/create?access_token={self.token}"
        create_data={"name": "技术部",
        "name_en": "JISHU1",
        "parentid": 1,
        "order": 1,
        "id": depart_id}
        r=requests.request("POST", create_url, json=create_data)
        print(f"创建部门结果为{r.text}")
        assert r.status_code == 200
        #再次创建部门（失败）
        r = requests.request("POST", create_url, json=create_data)
        print(f"创建部门结果为{r.text}")
        assert r.status_code == 200
        assert r.json().get("errcode") == 60008
        #删除部门
        delete_url=f"https://qyapi.weixin.qq.com/cgi-bin/department/delete?access_token={self.token}&id={depart_id}"
        r=requests.request("GET", delete_url)
        print(r.text)
        #再次创建部门（成功）
        r = requests.request("POST", create_url, json=create_data)
        print(f"创建部门结果为{r.text}")
        #针对接口的响应内容进行断言
        assert r.status_code == 200
        assert r.json().get("errcode") == 0
        #断言真实的数据操作效果(通过数据库断言，或者通过查询接口断言)
        get_url=f"https://qyapi.weixin.qq.com/cgi-bin/department/simplelist?access_token={self.token}"
        r = requests.request("GET", get_url)
        print(r.text)
        #获取所有部门的id放到列表中
        depart_ids=[d.get("id") for d in r.json().get("department_id")]
        print(f"搜索部门id的列表为{depart_ids}")
        assert depart_id in depart_ids

