
import pytest
import allure
from frame.common.logger import log

@allure.epic("企业微信接口自动化")
@allure.feature("标签管理")
@allure.story("标签业务流：创建 → 打标签 → 查询 → 删除")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.flow
class TestTagFlow:
    """
    标签管理模块 - 业务流测试
    """
    def test_tag_business_flow(self, tag_api,user_api, user_factory):
        """
        标签完整业务流：
        创建标签 → 创建用户 → 打标签 → 查询校验 → 删除标签 → 删除用户
        """

        # ========== Step 1 创建标签 ==========
        log.info("Step 1: 创建标签")
        create_res = tag_api.create("业务流测试标签")
        create_json = create_res.json()
        assert create_json["errcode"] == 0
        tag_id = create_json["tagid"]

        # ========== Step 2 创建用户 ==========
        log.info("Step 2: 创建用户")
        create_user_res = user_factory({
            "userid": "${auto}",
            "name": "${auto}",
            "mobile": "${auto}",
            "department": [1]
        })

        userid = getattr(create_user_res, "created_userid")

        # ==========  Step 3 给标签打用户（核心） ==========
        log.info("Step 3: 给标签添加用户")
        add_res = tag_api.add_users(
            tagid=tag_id,
            userlist=[userid]
        )
        add_json = add_res.json()
        log.info(f"打标签响应: {add_json}")
        assert add_json["errcode"] == 0

        # ========== Step 4 查询标签校验 ==========
        log.info("Step 4: 查询标签详情")
        get_json = tag_api.get(tag_id).json()
        assert get_json["errcode"] == 0

        user_ids = [u["userid"] for u in get_json.get("userlist", [])]
        assert userid in user_ids

        # ========== Step 5 删除标签 ==========
        log.info("Step 5: 删除标签")
        assert tag_api.delete(tag_id).json()["errcode"] == 0

        # ========== Step 6 删除用户 ==========
        log.info("Step 6: 删除用户")
        user_api.delete(userid)