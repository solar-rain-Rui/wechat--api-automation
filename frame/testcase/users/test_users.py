# frame/testcase/users/test_users.py
import os
import copy

import pytest
import allure

from frame.common.schema import SchemaValidator
from frame.common.utils.tools import load_yaml
from frame.common.assertions import AssertUtil
from frame.testcase.conftest import replace_auto_placeholder_user


@allure.epic("企业微信接口自动化")
@allure.feature("成员管理模块")
class TestUsers:
    @allure.story("创建成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["create_user"])
    def test_create_user(self, user_factory, case):
        allure.dynamic.title(case["name"])
        case = copy.deepcopy(case)
        res = user_factory(case["data"])
        assert res.status_code == 200
        res_json = res.json()
        if "errcode_not" in case.get("expect", {}):
            assert res_json.get("errcode") != case["expect"]["errcode_not"]
        else:
            AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/users_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)

    @allure.story("获取成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["get_user"])
    def test_get_user(self, user_api, user_factory, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        userid = case["data"]["userid"]
        if userid == "${auto}":
            create_res = user_factory({
                "userid": "${auto}",
                "name": "${auto}",
                "mobile": "${auto}",
                "department": [1],
            })
            userid = getattr(create_res, "created_userid", None)
            assert userid, "factory 未返回 created_userid"
        res = user_api.get(userid)
        res_json = res.json()
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/users_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)

    @allure.story("更新成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["update_user"])
    def test_update_user(self, user_api, user_factory, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        data = replace_auto_placeholder_user(case["data"])
        if case["data"].get("userid") == "${auto}":
            create_res = user_factory({
                "userid": "${auto}",
                "name": "${auto}",
                "mobile": "${auto}",
                "department": [1],
            })
            userid = getattr(create_res, "created_userid", None)
            assert userid, "factory 未返回 created_userid"
            data["userid"] = userid
        res = user_api.update(data)
        res_json = res.json()
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/users_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)

    @allure.story("删除成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["delete_user"])
    def test_delete_user(self, user_api, user_factory, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        userid = case["data"]["userid"]
        if userid == "${auto}":
            create_res = user_factory({
                "userid": "${auto}",
                "name": "${auto}",
                "mobile": "${auto}",
                "department": [1],
            })
            userid = getattr(create_res, "created_userid", None)
            assert userid, "factory 未返回 created_userid"
        res = user_api.delete(userid)
        res_json = res.json()
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/users_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)
