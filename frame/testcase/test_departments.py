from frame.apis.contacts.departments import Departments

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
        depart_ids = [d.get("id") for d in r.json().get("department_id")]
        assert self.depart_id in depart_ids
        #更新部门
        r=self.department.update(self.update_data)
        assert r.status_code == 200
        assert r.json().get("errcode") == 0
        #查询是否更新成功
            #后面用数据库断言来实现

        #删除部门
        r=self.department.delete(self.depart_id)
        assert r.status_code == 200
        assert r.json().get("errcode") == 0
        #查询是否删除成功
        # 获取所有部门id放到列表中
        depart_ids = [d.get("id") for d in r.json().get("department_id")]
        assert self.depart_id not in depart_ids


