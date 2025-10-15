import pytest
from frame.apis.contacts.departments import Departments
from frame.utils.utils import Utils


class TestCreateDepartments:

    def setup_class(self):
        #实例化部门类
        self.department=Departments()

    #参数完成创建部门单接口校验
    @pytest.mark.parametrize(
        "depart_data",
        Utils.get_yaml_data("frame/datas/departments.yaml")
    )
    def test_create_departments_by_params(self, depart_data):
        r=self.department.create(depart_data.get("data"))
        assert r.status_code == 200
        assert r.json().get("errcode")==depart_data.get("expect")