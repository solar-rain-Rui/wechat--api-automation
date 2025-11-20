import pytest
import allure
from frame.common.logger import log

@allure.epic("企业微信接口自动化")
@allure.feature("标签管理")
@allure.story("标签业务流：创建 → 更新 → 查询 → 删除")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.flow
class TestTagFlow:
    """
    标签管理模块 - 业务流测试
    模拟完整业务流程：
        1️⃣ 创建标签
        2️⃣ 更新标签名称
        3️⃣ 获取标签详情
        4️⃣ 删除标签
    """

    def test_tag_business_flow(self, tag_api):
        """
        测试标签的完整业务流
        """
        # Step 1️⃣ 创建标签
        log.info("Step 1: 创建标签")
        # create_data = {
        #     "tagname": "业务流测试标签"
        # }
        create_res = tag_api.create("业务流测试标签")
        create_json = create_res.json()
        log.info(f"创建标签响应: {create_json}")
        assert create_json["errcode"] == 0

        # 提取 tagid
        tag_id = create_json.get("tagid")
        assert tag_id is not None, "创建标签失败，未返回 tagid"

        # Step 2️⃣ 更新标签名称
        log.info("Step 2: 更新标签名称")
        update_name = "业务流测试标签_更新"
        # update_data = {
        #     "tagid": tag_id,
        #     "tagname": update_name
        # }
        update_res = tag_api.update(tag_id,update_name)
        update_json = update_res.json()
        log.info(f"更新标签响应: {update_json}")
        assert update_json["errcode"] == 0

        # Step 3️⃣ 获取标签详情
        log.info("Step 3: 获取标签详情")
        get_res = tag_api.get(tag_id)
        get_json = get_res.json()
        log.info(f"查询标签响应: {get_json}")
        assert get_json["errcode"] == 0

        # ⚠️ 获取标签详情返回格式如下：
        # {
        #   "errcode": 0,
        #   "errmsg": "ok",
        #   "tagname": "业务流测试标签_更新",
        #   "userlist": [],
        #   "partylist": []
        # }
        assert get_json["tagname"] == update_name, "更新后的标签名与查询结果不一致"

        # Step 4️⃣ 删除标签
        log.info("Step 4: 删除标签")
        delete_res = tag_api.delete(tag_id)
        delete_json = delete_res.json()
        log.info(f"删除标签响应: {delete_json}")
        assert delete_json["errcode"] == 0
