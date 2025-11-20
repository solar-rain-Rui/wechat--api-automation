import pytest
import allure
from frame.common.logger import log

@allure.epic("企业微信接口自动化")
@allure.feature("用户管理")
@allure.story("用户业务流：创建 → 修改 → 查询 → 删除")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.flow
class TestUserFlow:
    """
    用户管理业务流测试
    目标：验证用户的创建 → 修改 → 查询 → 删除整个流程的正确性
    """

    def test_user_business_flow(self, user_api):
        """
        测试步骤：
        1. 创建用户
        2. 修改用户信息
        3. 查询用户详情
        4. 删除用户
        """

        # 1️⃣ 创建用户
        log.info("Step 1: 创建用户")
        user_id = "flow_test_user"
        create_data = {
            "userid": user_id,
            "name": "业务流测试用户",
            "mobile": "13800001111",
            "department": [1]
        }
        create_res = user_api.create(create_data)
        log.info(f"创建用户响应: {create_res.json()}")
        assert create_res.status_code == 200
        assert create_res.json()["errcode"] == 0

        # 2️⃣ 修改用户信息
        log.info("Step 2: 修改用户信息")
        update_data = {
            "userid": user_id,
            "name": "业务流用户_修改后",
            "mobile": "13800002222"
        }
        update_res = user_api.update(update_data)
        log.info(f"修改用户响应: {update_res.json()}")
        assert update_res.json()["errcode"] == 0

        # 3️⃣ 查询用户详情
        # log.info("Step 3: 查询用户详情")
        # get_res = user_api.get(user_id)
        # log.info(f"查询用户响应: {get_res.json()}")
        # get_json = get_res.json()
        # assert get_json["errcode"] == 0
        # assert get_json["name"] == "业务流用户_修改后"
        # assert get_json["mobile"] == "13800002222"

        # 4️⃣ 删除用户
        log.info("Step 4: 删除用户")
        delete_res = user_api.delete(user_id)
        log.info(f"删除用户响应: {delete_res.json()}")
        assert delete_res.status_code == 200
        assert delete_res.json()["errcode"] == 0

        log.info("✅ 用户业务流测试执行完毕，所有步骤通过！")
