import pytest
import allure
from frame.common.assertions import AssertUtil
from frame.common.schema import SchemaValidator
from frame.common.tools import load_yaml  # 假设你有这个加载函数

@allure.feature("标签管理模块")
class TestTags:
    @pytest.mark.parametrize("case", load_yaml("datas/tags.yaml")["create_tag"])
    def test_create_tag(self, tag_api, case):
        allure.dynamic.title(case["name"])
        res = tag_api.create(**case["data"])
        AssertUtil.assert_json_value(res.json(), "$.errcode", case["expect"]["errcode"])
        SchemaValidator.validate_json(res.json(), "frame/schema/tag_schema.json")

    def test_update_tag(self, tag_api, temp_tag):
        res = tag_api.update(temp_tag, "更新名称")
        AssertUtil.assert_json_value(res.json(), "$.errcode", 0)
        SchemaValidator.validate_json(res.json(), "frame/schema/tag_schema.json")

    def test_get_tag(self, tag_api, temp_tag):
        res = tag_api.get(temp_tag)
        AssertUtil.assert_json_value(res.json(), "$.errcode", 0)
        SchemaValidator.validate_json(res.json(), "frame/schema/tag_schema.json")

    def test_delete_tag(self, tag_api, temp_tag):
        res = tag_api.delete(temp_tag)
        AssertUtil.assert_json_value(res.json(), "$.errcode", 0)
        SchemaValidator.validate_json(res.json(), "frame/schema/tag_schema.json")
