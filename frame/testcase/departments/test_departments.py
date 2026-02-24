import pytest
import allure
import os
import copy

from frame.common.logger import log
from frame.common.tools import load_yaml
from frame.common.assertions import AssertUtil
from frame.common.schema import SchemaValidator
from frame.testcase.conftest import replace_auto_placeholder


@allure.epic("企业微信接口自动化")
@allure.feature("部门管理")
class TestDepartments:

    @allure.story("创建部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["create_department"])
    def test_create_department(self, department_factory, case):
        """测试创建部门接口，使用统一预处理函数处理 ${auto} 占位符，并通过factory fixture进行创建和清理"""
        allure.dynamic.title(case["name"])

        # 使用统一预处理函数处理 ${auto} 占位符
        processed_data = replace_auto_placeholder(case["data"])

        # 通过 factory 创建部门，自动托管清理
        res = department_factory.create(processed_data)
        res_json = res.json()

        assert res.status_code == 200

        # 断言业务返回码
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])

        # jsonschema 结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/department_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)

        # 记录成功创建的部门ID，仅做日志输出
        if res_json.get("errcode") == 0:
            dep_id = res_json.get("id")
            if dep_id:
                log.info(f"✅ 创建测试部门ID：{dep_id}")

    @allure.story("查询部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["get_department"])
    def test_get_department(self, department_api, department_factory, case):
        """测试查询部门接口，使用 factory fixture 准备测试数据"""
        allure.dynamic.title(case["name"])
        
        # 准备测试数据：如果 id 是 ${auto}，先创建一个部门
        test_data = copy.deepcopy(case["data"])
        dep_id = test_data.get("id")
        
        if dep_id == "${auto}":
            # 对于 ${auto}，使用 factory 创建一个部门用于查询
            create_res = department_factory.create({
                "name": "${auto}",
                "parentid": "${auto}"
            })
            create_json = create_res.json()
            if create_json.get("errcode") == 0:
                dep_id = create_json.get("id")
        elif dep_id == 99999:
            # 对于 99999（不存在的部门），直接使用该值测试边界场景
            pass
        
        # 执行查询
        res = department_api.get(params={"id": dep_id})
        assert res.status_code == 200
        
        # 断言业务返回码
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        
        # jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/department_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)

    @allure.story("更新部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["update_department"])
    def test_update_department(self, department_api, department_factory, case):
        """测试更新部门接口，使用 factory fixture 准备测试数据"""
        allure.dynamic.title(case["name"])
        
        # 准备测试数据：如果 id 是 ${auto}，先创建一个部门
        test_data = copy.deepcopy(case["data"])
        dep_id = test_data.get("id")
        
        if dep_id == "${auto}":
            # 使用 factory 创建一个部门用于更新
            create_res = department_factory.create({
                "name": "${auto}",
                "parentid": "${auto}"
            })
            create_json = create_res.json()
            if create_json.get("errcode") == 0:
                dep_id = create_json.get("id")
                test_data["id"] = dep_id
        
        # 使用统一的预处理函数处理更新数据中的 ${auto} 占位符
        test_data = replace_auto_placeholder(test_data)
        
        # 执行更新
        res = department_api.update(test_data)
        assert res.status_code == 200
        
        # 断言业务返回码
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        
        # jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/department_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)

    @allure.story("删除部门")
    @pytest.mark.parametrize("case", load_yaml("datas/departments.yaml")["delete_department"])
    def test_delete_department(self, department_api, department_factory, case):
        """测试删除部门接口，使用 factory fixture 准备测试数据"""
        allure.dynamic.title(case["name"])
        
        # 准备测试数据：如果 id 是 ${auto}，先创建一个部门
        test_data = copy.deepcopy(case["data"])
        dep_id = test_data.get("id")
        
        if dep_id == "${auto}":
            # 对于"删除有子部门部门"的场景，需要创建父子部门
            if case["name"] == "删除有子部门部门":
                # 先创建父部门
                parent_res = department_factory.create({
                    "name": "${auto}",
                    "parentid": "${auto}"
                })
                parent_json = parent_res.json()
                if parent_json.get("errcode") == 0:
                    parent_id = parent_json.get("id")
                    # 创建子部门
                    child_res = department_factory.create({
                        "name": "${auto}",
                        "parentid": parent_id
                    })
                    # 使用父部门ID进行删除测试
                    dep_id = parent_id
            else:
                # 普通删除场景，使用 factory 创建一个部门
                create_res = department_factory.create({
                    "name": "${auto}",
                    "parentid": "${auto}"
                })
                create_json = create_res.json()
                if create_json.get("errcode") == 0:
                    dep_id = create_json.get("id")
        elif dep_id == 99999:
            # 不存在的部门，直接使用该值测试边界场景
            pass
        
        # 执行删除
        res = department_api.delete(dep_id)
        assert res.status_code == 200
        
        # 断言业务返回码
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        
        # jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/department_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)
