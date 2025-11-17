import pytest
import allure
from frame.common.assertions import AssertUtil
from frame.common.schema import SchemaValidator
from frame.common.tools import load_yaml  # 假设你有这个加载函数
print("🧩 create_tag cases:", load_yaml("datas/tags.yaml")["create_tag"])
print("🧩 update_tag cases:", load_yaml("datas/tags.yaml")["update_tag"])

@allure.feature("标签管理模块")
class TestTags:
    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["create_tag"])
    def test_create_tag(self, tag_api, case):
        allure.dynamic.title(case["name"])
        res = tag_api.create(**case["data"])

        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        SchemaValidator.validate_json(res.json(), "frame/schema/tag_schema.json")

    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["update_tag"])
    def test_update_tag(self, tag_api,case):
        res = tag_api.update(**case["data"])
        AssertUtil.assert_json_value(res.json(), "$.errcode", 0)
        SchemaValidator.validate_json(res.json(), "frame/schema/tag_schema.json")

    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["get_tag"])
    def test_get_tag(self, tag_api, case):
        res = tag_api.get(**case["data"])
        AssertUtil.assert_json_value(res.json(), "$.errcode", 0)
        SchemaValidator.validate_json(res.json(), "frame/schema/tag_schema.json")

    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["delete_tag"])
    def test_delete_tag(self, tag_api, case):
        res = tag_api.delete(**case["data"])
        AssertUtil.assert_json_value(res.json(), "$.errcode", 0)
        SchemaValidator.validate_json(res.json(), "frame/schema/tag_schema.json")
