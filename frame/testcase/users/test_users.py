# frame/testcase/users/test_users.py
import os

import pytest
import allure
import copy

from frame.common.schema import SchemaValidator
from frame.common.tools import load_yaml
from frame.common.assertions import AssertUtil
from frame.common.tools import CREATED_USER_IDS


@allure.epic("企业微信接口自动化")
@allure.feature("成员管理模块")
class TestUsers:
    @allure.story("创建成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["create_user"])
    def test_create_user(self, user_api, case):
        case = copy.deepcopy(case)  # ✅ 防止上一个用例污染当前数据
        allure.dynamic.title(case["name"])
        res = user_api.create(case["data"])
        assert res.status_code == 200
        res_json = res.json()
        # 记录到全局列表
        userid=case["data"]["userid"]
        CREATED_USER_IDS.append(userid)
        # JSONPath 断言
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])

    @allure.story("获取成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["get_user"])
    def test_get_user(self, user_api, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        res = user_api.get(case["data"]["userid"])
        res_json = res.json()
        #jsonpath断言
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])

        # jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/users_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)
    @allure.story("更新成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["update_user"])
    def test_update_user(self, user_api,case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        res = user_api.update( case["data"])
        res_json = res.json()

        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])

        #jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/users_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)

    @allure.story("删除成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["delete_user"])
    def test_delete_user(self, user_api,case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        res = user_api.delete(case["data"]["userid"])
        res_json = res.json()
        #jsonpath断言
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])

        # jsonschema结构断言
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/users_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)
