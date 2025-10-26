import pytest
import allure
from frame.common.tools import load_yaml
from frame.common.assertions import AssertUtil


@allure.feature("部门管理")
class TestDepartments:

    @allure.story("创建部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["create_department"])
    def test_create_department(self, department_api, case):
        allure.dynamic.title(case["name"])
        res = department_api.create(case["data"])
        assert res.status_code == 200
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])

    @allure.story("查询部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["get_department"])
    def test_get_department(self, department_api, case, temp_department):
        allure.dynamic.title(case["name"])
        # 用 fixture 创建的临时部门
        case["params"]["id"] = temp_department
        res = department_api.get(case["params"])
        assert res.status_code == 200
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])

    @allure.story("更新部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["update_department"])
    def test_update_department(self, department_api, case, temp_department):
        allure.dynamic.title(case["name"])
        # 修改临时部门名
        case["data"]["id"] = temp_department
        res = department_api.update(case["data"])
        assert res.status_code == 200
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])

    @allure.story("删除部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["delete_department"])
    def test_delete_department(self, department_api, case, temp_department):
        allure.dynamic.title(case["name"])
        # 删除 fixture 创建的临时部门
        case["params"]["id"] = temp_department
        res = department_api.delete(case["params"])
        assert res.status_code == 200
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
