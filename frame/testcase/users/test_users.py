# frame/testcase/users/test_users.py
import pytest
import allure
import copy
from frame.common.tools import load_yaml
from frame.common.assertions import AssertUtil


@allure.epic("企业微信接口自动化")
@allure.feature("成员管理模块")
class TestUsers:
    @allure.story("创建成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["create_user"])
    def test_create_user(self, user_api, temp_department,case):
        case = copy.deepcopy(case)  # ✅ 防止上一个用例污染当前数据
        allure.dynamic.title(case["name"])
        case["data"]["department"] = [temp_department]

        res = user_api.create(case["data"])
        assert res.status_code == 200
        res_json = res.json()

        # JSONPath 断言
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])

    @allure.story("获取成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["get_user"])
    def test_get_user(self, user_api, temp_user,case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        case["data"]["userid"]=temp_user
        res = user_api.get(case["data"]["userid"])
        res_json = res.json()

        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        AssertUtil.assert_json_value(res_json, "$.errmsg", case["expect"]["errmsg"])

    @allure.story("更新成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["update_user"])
    def test_update_user(self, user_api, temp_user,case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        case["data"]["userid"] = temp_user
        res = user_api.update( case["data"])
        res_json = res.json()

        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        AssertUtil.assert_json_value(res_json, "$.errmsg", case["expect"]["errmsg"])

    @allure.story("删除成员")
    @pytest.mark.parametrize("case", load_yaml("datas/users.yaml")["delete_user"])
    def test_delete_user(self, user_api, temp_user,case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        case["data"]["userid"] = temp_user
        res = user_api.delete(case["data"]["userid"])
        res_json = res.json()

        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        AssertUtil.assert_json_value(res_json, "$.errmsg", case["expect"]["errmsg"])
