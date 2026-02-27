import pytest
import allure

from frame.common.logger import log
from frame.common.tools import load_yaml
from frame.common.assertions import AssertUtil


@allure.epic("企业微信接口自动化")
@allure.feature("消息发送")
class TestSendMessage:

    @allure.story("发送消息")
    @pytest.mark.parametrize("case", load_yaml("datas/send_message.yaml")["send_message"])
    def test_send_message(self, message_api, case):
        """测试发送消息接口"""
        allure.dynamic.title(case["name"])
        
        # 执行消息发送
        res = message_api.send_message(case["data"])
        res_json = res.json()
        
        assert res.status_code == 200
        
        # 断言业务返回码
        AssertUtil.assert_json_value(res_json, "$.errcode", case["expect"]["errcode"])
        
        # 记录测试结果
        if res_json.get("errcode") == 0:
            log.info(f"✅ 消息发送成功：{case['name']}")
        else:
            log.info(f"⚠️ 消息发送验证通过（预期错误）：{case['name']}")


