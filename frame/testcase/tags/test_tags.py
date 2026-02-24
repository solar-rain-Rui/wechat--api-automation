import os
import copy

import pytest
import allure

from frame.common.assertions import AssertUtil
from frame.common.schema import SchemaValidator
from frame.common.tools import load_yaml
from frame.testcase.conftest import replace_auto_placeholder_tag


@allure.epic("企业微信接口自动化")
@allure.feature("标签管理模块")
class TestTags:
    @allure.story("创建标签")
    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["create_tag"])
    def test_create_tag(self, tag_factory, case):
        allure.dynamic.title(case["name"])
        case = copy.deepcopy(case)
        res = tag_factory(case["data"])
        assert res.status_code == 200
        res_json = res.json()
        if "errcode_not" in case.get("expect", {}):
            assert res_json.get("errcode") != case["expect"]["errcode_not"]
        else:
            AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/tag_schema.json")
        SchemaValidator.validate_json(res.json(), schema_path)

    @allure.story("查询标签")
    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["get_tag"])
    def test_get_tag(self, tag_api, tag_factory, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        tagid = case["data"]["tagid"]
        if tagid == "${auto}":
            create_res = tag_factory({"tagname": "${auto}"})
            tagid = getattr(create_res, "created_tagid", None)
            assert tagid is not None, "factory 未返回 created_tagid"
        res = tag_api.get(tagid)
        res_json = res.json()
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/tag_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)

    @allure.story("更新标签")
    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["update_tag"])
    def test_update_tag(self, tag_api, tag_factory, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        data = replace_auto_placeholder_tag(case["data"])
        if case["data"].get("tagid") == "${auto}":
            create_res = tag_factory({"tagname": "${auto}"})
            tagid = getattr(create_res, "created_tagid", None)
            assert tagid is not None, "factory 未返回 created_tagid"
            data["tagid"] = tagid
        res = tag_api.update(data["tagid"], data["tagname"])
        res_json = res.json()
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/tag_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)

    @allure.story("删除标签")
    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["delete_tag"])
    def test_delete_tag(self, tag_api, tag_factory, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        tagid = case["data"]["tagid"]
        if tagid == "${auto}":
            create_res = tag_factory({"tagname": "${auto}"})
            tagid = getattr(create_res, "created_tagid", None)
            assert tagid is not None, "factory 未返回 created_tagid"
        res = tag_api.delete(tagid)
        res_json = res.json()
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/tag_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)

    @allure.story("添加标签成员")
    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["add_tag_users"])
    def test_add_tag_users(self, tag_api, tag_factory, user_factory, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        data = case["data"]

        #  用 factory 处理 tag（由 factory 内部调用 replace_auto_placeholder_tag）
        tagid = data.get("tagid")
        if tagid == "${auto}":
            create_res = tag_factory({"tagname": "${auto}"})
            tagid = getattr(create_res, "created_tagid")
            assert tagid, "factory 未返回 created_tagid"

        #  userlist 也交给 factory，但这里仅做编排，不做生成逻辑
        userlist = data.get("userlist")
        processed_userlist = None

        if userlist:
            processed_userlist = []
            for item in userlist:
                if item == "${auto}":
                    create_user_res = user_factory({
                        "userid": "${auto}",
                        "name": "${auto}",
                        "mobile": "${auto}",
                        "department": [1]
                    })
                    userid = getattr(create_user_res, "created_userid")
                    assert userid, "factory 未返回 created_userid"
                    processed_userlist.append(userid)
                else:
                    processed_userlist.append(item)

        #  partylist 原样
        partylist = data.get("partylist")

        #  调接口
        res = tag_api.add_users(
            tagid=tagid,
            userlist=processed_userlist,
            partylist=partylist
        )
        #  断言
        assert res.status_code == 200
        res_json = res.json()

        AssertUtil.assert_json_value(
            res_json,
            "$.errcode",
            case["expect"]["errcode"]
        )
        schema_path = os.path.join(
            os.path.dirname(__file__),
            "../../schema/tag_schema.json"
        )
        SchemaValidator.validate_json(res_json, schema_path)

    @allure.story("获取标签成员")
    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["get_tag_users"])
    def test_get_tag_users(self, tag_api, tag_factory, case):
        case = copy.deepcopy(case)
        allure.dynamic.title(case["name"])
        tagid = case["data"]["tagid"]
        if tagid == "${auto}":
            create_res = tag_factory({"tagname": "${auto}"})
            tagid = getattr(create_res, "created_tagid", None)
            assert tagid is not None, "factory 未返回 created_tagid"
        res = tag_api.get_users(tagid)
        assert res.status_code == 200
        res_json = res.json()
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        schema_path = os.path.join(os.path.dirname(__file__), "../../schema/tag_schema.json")
        SchemaValidator.validate_json(res_json, schema_path)
