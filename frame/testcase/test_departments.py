
"""
接口自动化测试框架第一版
1.通过ApiObject模式，把框架分为了3层
2.通过wework获取access_token
3.在departments中完成了部门管理业务接口的描述，继承了wework,完成了access_token的传递
4.在测试用例中通过setup完成了业务接口的实例化和测试数据的准备
5.在具体的测试用例中传入测试数据，拼接业务逻辑，完成断言
"""
import json

from frame.utils.utils import Utils

"""
接口自动化测试框架优化
1.完成了base_api的封装，封装了requests发送请求的方法
2.把配置数据拆分到yaml文件中进行管理，完成了数据和用例的抽离
"""





from frame.apis.contacts.departments import Departments
from jsonpath import jsonpath

class TestDepartment:

    def setup_class(self):
        #实例化部门类
        self.department=Departments()
        #准备测试数据
        self.depart_id=210
        self.create_data={
             "name": "技术部",
             "name_en": "JISHU1",
             "parentid": 1,
             "order": 1,
             "id": self.depart_id
        }
        self.update_name="广州研发中心-update"
        self.update_data={
            "name":self.update_name,
            "id":self.depart_id
        }
    def test_departments_flow(self):
        """
        部门增删改查的场景
        :return:
        """
        #创建部门
        r=self.department.create(self.create_data)
        assert r.status_code == 200
        assert r.json().get("errcode") == 0
        #查询是否创建成功
        r=self.department.get()
            #获取所有部门id放到列表中
        #depart_ids = [d.get("id") for d in r.json().get("department_id")]
        #通过jsonpath获取所有部门id，放到列表中
        depart_ids=jsonpath(r.json(),"$..id")
        print(f"获取到的部门Id列表为{depart_ids}")
        assert self.depart_id in depart_ids
        #更新部门
        r=self.department.update(self.update_data)
        assert r.status_code == 200
        assert r.json().get("errcode") == 0
        #查询是否更新成功
            #后面用数据库断言来实现
        database_info={
           "host":"127.0.0.1",
           "port":3306,
           "database":"contacts",
           "user":"root",
           "password":"root1997",
           "charset":"utf8"
       }
        datas=Utils.query_db("select name from departments where id={self.depart_id}",database_info)
        assert datas[0][0]==self.update_name
        #删除部门
        r=self.department.delete(self.depart_id)
        assert r.status_code == 200
        assert r.json().get("errcode") == 0
        #查询是否删除成功
        r=self.department.get()
        # 获取所有部门id放到列表中
        #depart_ids = [d.get("id") for d in r.json().get("department_id")]
        depart_ids = jsonpath(r.json(), "$..id")
        print(f"获取到的部门Id列表为{depart_ids}")
        assert self.depart_id not in depart_ids

    def test_get_departments_schema(self):
        """
        测试获取所有部门id接口响应符合预期结构
        :param self:
        :return:
        """
        expect={
                "errcode": 0,
                "errmsg": "ok",
                "department_id": [
                    {
                        "id": 2,
                        "parentid": 1,
                        "order": 10
                    },
                    {
                        "id": 3,
                        "parentid": 2,
                        "order": 40
                    }
                ]
        }
        #生成json schema文件
        schema_path="frame/config/get_departments_schema.json"
        Utils.generate_schema(expect,schema_path)
        #发出查询请求
        r=self.department.get()
        #断言响应体符合预期结构
        schema=json.load(open(schema_path,encoding="utf-8"))
        print(f"获取到的schema内容为:{schema}")
        assert Utils.schema_validate(r.json(),schema)


