import pytest
import allure
import os

from frame.common.logger import log
from frame.common.tools import load_yaml
from frame.common.assertions import AssertUtil
from frame.common.schema import SchemaValidator
from frame.common.tools import CREATED_DEPT_IDS


@allure.feature("部门管理")
class TestDepartments:

    @allure.story("创建部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["create_department"])
    def test_create_department(self, department_api,case):
        allure.dynamic.title(case["name"])
        res = department_api.create(case["data"])
        res_json = res.json()
        assert res.status_code == 200
        # 判断是否成功创建部门
        if res_json.get("errcode") == 0:
            dep_id = res_json.get("id")
            if dep_id:
                CREATED_DEPT_IDS.append(dep_id)
                log.info(f"✅ 创建测试部门ID：{dep_id}")
            else:
                log.warning(f"部门创建成功但返回没有 id: {res_json}")
        else:
            # 异常场景也打印日志，但不报 KeyError
            log.warning(f"创建部门返回错误: {res_json}")


        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        #jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/department_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)
        #数据库断言
        # sql = f"SELECT name FROM departments WHERE id = {fake_department}"
        # AssertUtil.assert_db_value(db, sql, case["data"]["name"], key="name")


    @allure.story("查询部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["get_department"])
    def test_get_department(self, department_api, case):
        allure.dynamic.title(case["name"])

        res = department_api.get(params=case["data"])
        assert res.status_code == 200
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        # jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/department_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)
        #数据库断言



    @allure.story("更新部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["update_department"])
    def test_update_department(self, department_api, case):
        allure.dynamic.title(case["name"])
        # 修改临时部门名
        data=case["data"]
        res = department_api.update(data)
        assert res.status_code == 200
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        # jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/department_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)

    # @allure.story("删除部门")
    # @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["delete_department"])
    # def test_delete_department(self, department_api, case, temp_department):
    #     allure.dynamic.title(case["name"])
    #     # 删除 fixture 创建的临时部门
    #     case["params"]["id"] = temp_department
    #     res = department_api.delete(case["params"])
    @allure.story("删除部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["delete_department"])#让fixture接受参数
    def test_delete_department(self, department_api, case):
        """测试删除部门接口，使用纯数据驱动，不依赖fixture"""
        allure.dynamic.title(case["name"])
        dep_id = case["data"]["id"]
        # 发起删除请求
        res = department_api.delete(dep_id)
        # 校验接口状态码
        assert res.status_code == 200
        #校验业务返回码
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        # jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/department_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)